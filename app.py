import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            flash("Please log in to access this page")
            return redirect(url_for("login"))
        if session["user"].lower() != "admin":
            flash("This page is accessible only to administrators")
            return redirect(url_for("get_recipes"))
        return f(*args, **kwargs)
    return decorated_function


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
        username = request.form.get("username", "").lower().strip()
        password = request.form.get("password", "")
        
        
        # Input validation
        if not username or not password:
            flash("Please fill in all fields")
            return redirect(url_for("register"))
            
        if len(username) < 3 or len(username) > 20:
            flash("Username must be between 3 and 20 characters")
            return redirect(url_for("register"))
            
        if len(password) < 6:
            flash("Password must be at least 6 characters")
            return redirect(url_for("register"))

        try:
            existing_user = mongo.db.users.find_one({"username": username})
            
            if existing_user:
                flash("Username already exists")
                return redirect(url_for("register"))
                
            register = {
                "username": username,
                "password": generate_password_hash(password)
            }
            mongo.db.users.insert_one(register)
            session["user"] = username
            flash("Registration Successful!")
            return redirect(url_for("profile", username=session["user"]))
            
        except Exception as e:
            flash("An error occurred during registration. Please try again.")
            return redirect(url_for("register"))
            
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
    if not session.get("user"):
        flash("Please log in to view profiles")
        return redirect(url_for("login"))
        
    try:
        user = mongo.db.users.find_one({"username": session["user"]})
        if not user:
            session.pop("user")
            flash("User not found")
            return redirect(url_for("login"))
            
        return render_template("profile.html", username=user["username"])
        
    except Exception as e:
        flash("An error occurred while loading the profile. Please try again.")
        return redirect(url_for("get_recipes"))
    

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
    if not session.get("user"):
        flash("Please log in to add recipes")
        return redirect(url_for("login"))

    if request.method == "POST":
        recipe_name = request.form.get("recipe_name", "").strip()
        recipe_description = request.form.get("recipe_description", "").strip()
        category_name = request.form.get("category_name")

        # Input validation
        if not recipe_name or not recipe_description or not category_name:
            flash("Please fill in all required fields")
            categories = list(mongo.db.categories.find().sort("category_name", 1))
            return render_template("add_recipe.html", categories=categories)

        try:
            healthy = "on" if request.form.get("healthy") else "off"
            recipe = {
                "category_name": category_name,
                "recipe_name": recipe_name,
                "recipe_description": recipe_description,
                "date_added": request.form.get("date_added"),
                "healthy": healthy,
                "created_by": session["user"]
            }
            
            mongo.db.recipes.insert_one(recipe)
            flash("Recipe Successfully Added")
            return redirect(url_for("get_recipes"))
            
        except Exception as e:
            flash("An error occurred while adding the recipe. Please try again.")
            categories = list(mongo.db.categories.find().sort("category_name", 1))
            return render_template("add_recipe.html", categories=categories)
    
    try:
        categories = list(mongo.db.categories.find().sort("category_name", 1))
        return render_template("add_recipe.html", categories=categories)
    except Exception as e:
        flash("An error occurred while loading categories. Please try again.")
        return redirect(url_for("get_recipes"))


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
@admin_required
def categories():
    try:
        categories = list(mongo.db.categories.find().sort("category_name", 1))
        return render_template("categories.html", categories=categories)
    except Exception as e:
        flash("An error occurred while loading categories. Please try again.")
        return redirect(url_for("get_recipes"))


# Add a category
@app.route("/add_category", methods=["GET", "POST"])
@admin_required
def add_category():
    if request.method == "POST":
        category_name = request.form.get("category_name", "").strip()
        
        if not category_name:
            flash("Please enter a category name")
            return redirect(url_for("add_category"))
            
        try:
            # Check if category already exists
            existing_category = mongo.db.categories.find_one(
                {"category_name": category_name})
            if existing_category:
                flash("Category already exists")
                return redirect(url_for("add_category"))
                
            category = {"category_name": category_name}
            mongo.db.categories.insert_one(category)
            flash("Category Successfully Added")
            return redirect(url_for("categories"))
            
        except Exception as e:
            flash("An error occurred while adding the category. Please try again.")
            return redirect(url_for("add_category"))
            
    return render_template("add_category.html")


# Edit a category
@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {"category_name": request.form.get("category_name")}
        mongo.db.categories.update_one({"_id": ObjectId(category_id)}, {"$set": submit})
        flash("Category Successfully Updated")
        return redirect(url_for("categories"))
    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


# Delete a category
@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.delete_one({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("categories"))


# Run the app
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

