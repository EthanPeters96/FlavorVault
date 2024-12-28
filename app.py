import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# Get recipes
@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if the username already exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        # Check if the email already exists
        if existing_user:
            flash("Username already exists")
            # Redirect to the register page
            return redirect(url_for("register"))
        # Register the user
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)
        #put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check if the username already exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            # Check if the hashed password matches user's input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                # Put the new user into 'session' cookie
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}!".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # If the password is incorrect, flash an error message
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        else:
            # If the username doesn't exist, flash an error message
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))
    return render_template("login.html")


# Profile
@app.route("/profile/<username>")
def profile(username):
    # Get the session user's username from the database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if session["user"]:
        return render_template("profile.html", username=username)
    else:
        return redirect(url_for("login"))
    

# Logout
@app.route("/logout")
def logout():
    # Remove the user from the session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# Add a recipe
@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        # Create the recipe dictionary from form data
        healthy = "on" if request.form.get("healthy") else "off"
        recipe = {
            "category_name": request.form.get("category_name"),
            "recipe_name": request.form.get("recipe_name"),
            "recipe_description": request.form.get("recipe_description"),
            "date_added": request.form.get("date_added"),
            "healthy": healthy,
            "created_by": session["user"]  # Add the username of the person creating the recipe
        }
        
        # Insert the recipe into the database
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Successfully Added")
        return redirect(url_for("get_recipes"))
    
    # GET method - display the form
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("add_recipe.html", categories=categories)


# Edit a recipe
@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if not session.get("user"):
        flash("Please log in to edit recipes")
        return redirect(url_for("login"))
    
    if session["user"].lower() != recipe["created_by"].lower() and session["user"].lower() != "admin":
        flash("You can only edit your own recipes!")
        return redirect(url_for("get_recipes"))

    if request.method == "POST":
        # Create the recipe dictionary from form data
        healthy = "on" if request.form.get("healthy") else "off"
        submit = {
            "category_name": request.form.get("category_name"),
            "recipe_name": request.form.get("recipe_name"),
            "recipe_description": request.form.get("recipe_description"),
            "date_added": request.form.get("date_added"),
            "healthy": healthy,
            "created_by": recipe["created_by"]  # Preserve original creator
        }
        # Update the recipe in the database
        mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)}, {"$set": submit})
        flash("Recipe Successfully Updated")
        return redirect(url_for("get_recipes"))
    
    # GET method - display the form
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("edit_recipe.html", recipe=recipe, categories=categories)


# Delete a recipe
@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    # Check if user is logged in
    if not session.get("user"):
        flash("Please log in to delete recipes")
        return redirect(url_for("login"))
    
    # Get the recipe
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    
    # Check if recipe exists
    if not recipe:
        flash("Recipe not found")
        return redirect(url_for("get_recipes"))
    
    # Check if user has permission to delete
    if session["user"].lower() != recipe["created_by"].lower() and session["user"].lower() != "admin":
        flash("You can only delete your own recipes!")
        return redirect(url_for("get_recipes"))
    
    # Delete the recipe
    mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("get_recipes"))


# Manage Categories
@app.route("/categories")
def categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


# Add a category
@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {"category_name": request.form.get("category_name")}
        mongo.db.categories.insert_one(category)
        flash("Category Successfully Added")
        return redirect(url_for("categories"))
    return render_template("add_category.html")


# Run the app
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
