import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for, jsonify)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, EmailField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email

if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
app.config['WTF_CSRF_ENABLED'] = True

mongo = PyMongo(app)

# Constants for flash messages
USERNAME_EXISTS_MSG = "Username already exists"
REGISTRATION_SUCCESS_MSG = "Registration Successful!"
REGISTRATION_ERROR_MSG = "Please correct the errors in the form."
DB_ERROR_MSG = "An error occurred while processing your request. Please try again."
RECIPE_ADDED_MSG = "Recipe Successfully Added"
RECIPE_UPDATED_MSG = "Recipe Successfully Updated"
RECIPE_DELETED_MSG = "Recipe Successfully Deleted"
CATEGORY_ADDED_MSG = "Category Successfully Added"
CATEGORY_UPDATED_MSG = "Category Successfully Updated"
CATEGORY_DELETED_MSG = "Category Successfully Deleted"
LOGIN_SUCCESS_MSG = "Welcome, {}"
LOGIN_ERROR_MSG = "Incorrect Username and/or Password"
LOGOUT_MSG = "You have been logged out"
PROFILE_ACCESS_ERROR_MSG = "Please log in to view profiles"
RECIPE_ACCESS_ERROR_MSG = "Please log in to add recipes"
CATEGORY_ACCESS_ERROR_MSG = "Please enter a category name"

# Centralized error handler
def handle_db_error(e=None):
    if e:
        app.logger.error(f"Database error: {e}")
    flash(DB_ERROR_MSG)
    return redirect(url_for("get_recipes"))

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
    # Redirect if user is already logged in
    if session.get("user"):
        return redirect(url_for("profile", username=session["user"]))
        
    form = RegistrationForm()
    if request.method == "POST":  # Check if the request method is POST
        if form.validate_on_submit():
            username = form.username.data.lower().strip()
            email = form.email.data.lower().strip()
            
            # Check for existing user
            existing_user = mongo.db.users.find_one({"username": username})
            if existing_user:
                flash(USERNAME_EXISTS_MSG)
                return redirect(url_for("register"))
            
            # Register new user
            register = {
                "username": username,
                "email": email,
                "password": generate_password_hash(form.password.data)
            }
            
            try:
                mongo.db.users.insert_one(register)
                session["user"] = username
                flash(REGISTRATION_SUCCESS_MSG)
                return redirect(url_for("profile", username=session["user"]))
            except Exception as e:
                return handle_db_error(e)
        else:
            # Flash message if form is not submitted successfully
            flash(REGISTRATION_ERROR_MSG)

    return render_template("register.html", form=form)

# Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=5, max=15)
    ])
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=5, message='Password must be at least 5 characters long.'),
        EqualTo('confirm_password', message='Passwords must match.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
    ])
    submit = SubmitField('Register')

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=5, max=15)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=5, max=15)
    ])
    submit = SubmitField('Login')

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    # Redirect if user is already logged in
    if session.get("user"):
        return redirect(url_for("profile", username=session["user"]))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": form.username.data.lower().strip()})

        if existing_user:
            # Check password
            if check_password_hash(existing_user["password"], form.password.data):
                session["user"] = form.username.data.lower()
                flash(LOGIN_SUCCESS_MSG.format(form.username.data))
                return redirect(url_for("profile", username=session["user"]))
            else:
                flash(LOGIN_ERROR_MSG)
                return redirect(url_for("login"))
        else:
            flash(LOGIN_ERROR_MSG)
            return redirect(url_for("login"))

    return render_template("login.html", form=form)

# Profile
@app.route("/profile/<username>")
def profile(username):
    if not session.get("user"):
        flash(PROFILE_ACCESS_ERROR_MSG)
        return redirect(url_for("login"))
        
    try:
        user = mongo.db.users.find_one({"username": session["user"]})
        if not user:
            session.pop("user")
            flash("User not found")
            return redirect(url_for("login"))
            
        return render_template("profile.html", username=user["username"])
        
    except Exception as e:
        return handle_db_error(e)

# Logout
@app.route("/logout")
def logout():
    # Remove the user from the session cookie
    flash(LOGOUT_MSG)
    session.pop("user")
    return redirect(url_for("login"))

# Add a recipe
@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if not session.get("user"):
        flash(RECIPE_ACCESS_ERROR_MSG)
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
            flash(RECIPE_ADDED_MSG)
            return redirect(url_for("get_recipes"))
            
        except Exception as e:
            return handle_db_error(e)
    
    try:
        categories = list(mongo.db.categories.find().sort("category_name", 1))
        return render_template("add_recipe.html", categories=categories)
    except Exception as e:
        return handle_db_error(e)

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
            "created_by": recipe["created_by"]
        }
        # Update the recipe in the database
        mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)}, {"$set": submit})
        flash(RECIPE_UPDATED_MSG)
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
    flash(RECIPE_DELETED_MSG)
    return redirect(url_for("get_recipes"))

# Manage Categories
@app.route("/categories")
@admin_required
def categories():
    try:
        categories = list(mongo.db.categories.find().sort("category_name", 1))
        return render_template("categories.html", categories=categories)
    except Exception as e:
        return handle_db_error(e)

# Add a category
@app.route("/add_category", methods=["GET", "POST"])
@admin_required
def add_category():
    if request.method == "POST":
        category_name = request.form.get("category_name", "").strip()
        
        if not category_name:
            flash(CATEGORY_ACCESS_ERROR_MSG)
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
            flash(CATEGORY_ADDED_MSG)
            return redirect(url_for("categories"))
            
        except Exception as e:
            return handle_db_error(e)
            
    return render_template("add_category.html")

# Edit a category
@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {"category_name": request.form.get("category_name")}
        mongo.db.categories.update_one({"_id": ObjectId(category_id)}, {"$set": submit})
        flash(CATEGORY_UPDATED_MSG)
        return redirect(url_for("categories"))
    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)

# Delete a category
@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.delete_one({"_id": ObjectId(category_id)})
    flash(CATEGORY_DELETED_MSG)
    return redirect(url_for("categories"))

# Run the app
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

