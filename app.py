"""
FlavorVault - A Flask web application for managing and sharing recipes.
This module contains the main application logic and route handlers.
"""

from functools import wraps
import os
# Group bson imports together
from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import (
    Flask,
    flash,
    render_template,
    redirect,
    request,
    session,
    url_for,
)
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from pymongo.errors import PyMongoError
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    EmailField,
)
from wtforms.validators import DataRequired, Length, EqualTo, Email

if os.path.exists("env.py"):
    import env  # pylint: disable=unused-import

    # env.py sets environment variables, import is needed even if unused

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
app.config["WTF_CSRF_ENABLED"] = True

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
CATEGORY_DELETE_ERROR_MSG = "Cannot delete category that contains recipes"
CATEGORY_NOT_FOUND_MSG = "Category not found"
ADMIN_ACCESS_ERROR_MSG = "This page is accessible only to administrators"
USER_NOT_FOUND_MSG = "User not found"
RECIPE_EDIT_ERROR_MSG = "You can only edit your own recipes!"
RECIPE_NOT_FOUND_MSG = "Recipe not found"
RECIPE_DELETE_ERROR_MSG = "You can only delete your own recipes!"
CATEGORY_EXISTS_ERROR_MSG = "Category already exists"


# Centralized error handler
def handle_db_error(e=None):
    """
    Centralized error handler for database operations.

    Args:
        e (Exception, optional): The exception that was raised. Defaults to None.

    Returns:
        Response: Redirect response to recipes page with error message
    """
    if e:
        app.logger.error("Database error: %s", str(e))
    flash(DB_ERROR_MSG)
    return redirect(url_for("get_recipes"))


def admin_required(f):
    """
    Decorator to restrict access to admin users only.

    Args:
        f (function): The function to be decorated

    Returns:
        function: Decorated function that checks for admin privileges
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            flash(PROFILE_ACCESS_ERROR_MSG)
            return redirect(url_for("login"))
        if session["user"].lower() != "admin":
            flash(ADMIN_ACCESS_ERROR_MSG)
            return redirect(url_for("get_recipes"))
        return f(*args, **kwargs)

    return decorated_function


# Get recipes
@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    """
    Display all recipes on the home page.

    Returns:
        Response: Rendered recipes.html template with all recipes
    """
    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration process.

    Validates registration form data, checks for existing users,
    and creates new user accounts in the database.

    Returns:
        Response: On GET: registration form
                 On POST success: redirect to user profile
                 On POST failure: redirect to registration with error
    
    Notes:
        - Usernames are stored in lowercase
        - Passwords are hashed before storage
        - Email addresses are stored in lowercase
        - Redirects to profile if user is already logged in
    """
    if session.get("user"):
        return redirect(url_for("profile", username=session["user"]))

    form = RegistrationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data.lower().strip()
            email = form.email.data.lower().strip()

            existing_user = mongo.db.users.find_one({"username": username})
            if existing_user:
                flash(USERNAME_EXISTS_MSG)
                return redirect(url_for("register"))

            new_user = {
                "username": username,
                "email": email,
                "password": generate_password_hash(form.password.data),
            }

            try:
                mongo.db.users.insert_one(new_user)
                session["user"] = username
                flash(REGISTRATION_SUCCESS_MSG)
                return redirect(url_for("profile", username=session["user"]))
            except PyMongoError as e:
                return handle_db_error(e)

        flash(REGISTRATION_ERROR_MSG)

    return render_template("register.html", form=form)


# Registration Form
class RegistrationForm(FlaskForm):
    """
    Form class for user registration.

    Fields:
        username: 5-15 characters
        email: Valid email address
        password: Minimum 5 characters
        confirm_password: Must match password
        submit: Submit button
    """

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=5, max=15)]
    )
    email = EmailField(
        "Email", validators=[DataRequired(), Email(message="Invalid email address.")]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=5, message="Password must be at least 5 characters long."),
            EqualTo("confirm_password", message="Passwords must match."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
        ],
    )
    submit = SubmitField("Register")


# Login Form
class LoginForm(FlaskForm):
    """
    Form class for user login.

    Fields:
        username: 5-15 characters
        password: 5-15 characters
        submit: Submit button
    """

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=5, max=15)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=5, max=15)]
    )
    submit = SubmitField("Login")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login process.

    Returns:
        Response: On GET: login form
                 On POST success: redirect to user profile
                 On POST failure: redirect to login with error
    """
    if session.get("user"):
        return redirect(url_for("profile", username=session["user"]))

    form = LoginForm()
    if form.validate_on_submit():
        existing_user = mongo.db.users.find_one(
            {"username": form.username.data.lower().strip()}
        )

        if existing_user and check_password_hash(
            existing_user["password"], form.password.data
        ):
            session["user"] = form.username.data.lower()
            flash(LOGIN_SUCCESS_MSG.format(form.username.data))
            return redirect(url_for("profile", username=session["user"]))

        flash(LOGIN_ERROR_MSG)
        return redirect(url_for("login"))

    return render_template("login.html", form=form)


# Profile
@app.route("/profile/<username>")
def profile(username):
    """
    Display user profile page.

    Args:
        username (str): Username of the profile to display

    Returns:
        Response: On success: rendered profile.html template
                 On not logged in: redirect to login page
                 On user not found: redirect to login page with error
                 On database error: redirect to recipes page

    Notes:
        - Requires user to be logged in
        - Validates user exists in database
        - Clears session if user not found
        - Handles database errors gracefully
    """
    if not session.get("user"):
        flash(PROFILE_ACCESS_ERROR_MSG)
        return redirect(url_for("login"))

    try:
        user = mongo.db.users.find_one({"username": username})
        if not user:
            session.pop("user")
            flash(USER_NOT_FOUND_MSG)
            return redirect(url_for("login"))

        return render_template("profile.html", username=username)

    except PyMongoError as e:
        return handle_db_error(e)


# Logout
@app.route("/logout")
def logout():
    """
    Handle user logout process.

    Returns:
        Response: Redirect to login page with logout message
    """
    flash(LOGOUT_MSG)
    session.pop("user")
    return redirect(url_for("login"))


# Add a recipe
@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    """
    Handle creation of new recipes.

    Returns:
        Response: On GET: recipe creation form
                 On POST success: redirect to recipes page
                 On POST failure: return to form with error
    """
    if not session.get("user"):
        flash(RECIPE_ACCESS_ERROR_MSG)
        return redirect(url_for("login"))

    if request.method == "POST":
        recipe_name = request.form.get("recipe_name", "").strip()
        recipe_description = request.form.get("recipe_description", "").strip()
        category_name = request.form.get("category_name")

        # Input validation
        if not recipe_name or not recipe_description or not category_name:
            flash(RECIPE_ACCESS_ERROR_MSG)
            all_categories = list(mongo.db.categories.find().sort("category_name", 1))
            return render_template("add_recipe.html", categories=all_categories)

        try:
            healthy = "on" if request.form.get("healthy") else "off"
            recipe = {
                "category_name": category_name,
                "recipe_name": recipe_name,
                "recipe_description": recipe_description,
                "date_added": request.form.get("date_added"),
                "healthy": healthy,
                "created_by": session["user"],
            }

            mongo.db.recipes.insert_one(recipe)
            flash(RECIPE_ADDED_MSG)
            return redirect(url_for("get_recipes"))

        except PyMongoError as e:
            return handle_db_error(e)

    try:
        all_categories = list(mongo.db.categories.find().sort("category_name", 1))
        return render_template("add_recipe.html", categories=all_categories)
    except PyMongoError as e:
        return handle_db_error(e)


# Edit a recipe
@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    """
    Handle editing of existing recipes.

    Args:
        recipe_id (str): MongoDB ObjectId of recipe to edit

    Returns:
        Response: On GET: edit form with recipe data
                 On POST: redirect to recipes page
    """
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if not session.get("user"):
        flash(RECIPE_ACCESS_ERROR_MSG)
        return redirect(url_for("login"))

    if (
        session["user"].lower() != recipe["created_by"].lower()
        and session["user"].lower() != "admin"
    ):
        flash(RECIPE_EDIT_ERROR_MSG)
        return redirect(url_for("get_recipes"))

    if request.method == "POST":
        healthy = "on" if request.form.get("healthy") else "off"
        submit = {
            "category_name": request.form.get("category_name"),
            "recipe_name": request.form.get("recipe_name"),
            "recipe_description": request.form.get("recipe_description"),
            "date_added": request.form.get("date_added"),
            "healthy": healthy,
            "created_by": recipe["created_by"],
        }
        mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)}, {"$set": submit})
        flash(RECIPE_UPDATED_MSG)
        return redirect(url_for("get_recipes"))

    all_categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("edit_recipe.html", recipe=recipe, categories=all_categories)


# Delete a recipe
@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    """
    Handle deletion of recipes.

    Args:
        recipe_id (str): MongoDB ObjectId of recipe to delete

    Returns:
        Response: Redirect to recipes page with success/error message
    """
    if not session.get("user"):
        flash(RECIPE_ACCESS_ERROR_MSG)
        return redirect(url_for("login"))

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if not recipe:
        flash(RECIPE_NOT_FOUND_MSG)
        return redirect(url_for("get_recipes"))

    if (
        session["user"].lower() != recipe["created_by"].lower()
        and session["user"].lower() != "admin"
    ):
        flash(RECIPE_DELETE_ERROR_MSG)
        return redirect(url_for("get_recipes"))

    mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
    flash(RECIPE_DELETED_MSG)
    return redirect(url_for("get_recipes"))


# Manage Categories
@app.route("/categories")
@admin_required
def categories():
    """
    Display all recipe categories.

    Returns:
        Response: Rendered categories.html template with all categories
    """
    try:
        category_list = list(mongo.db.categories.find().sort("category_name", 1))
        return render_template("categories.html", categories=category_list)
    except PyMongoError as e:
        return handle_db_error(e)


# Add a category
@app.route("/add_category", methods=["GET", "POST"])
@admin_required
def add_category():
    """
    Handle creation of new categories.

    Returns:
        Response: On GET: category creation form
                 On POST success: redirect to categories page
                 On POST failure: return to form with error
    """
    if request.method == "POST":
        category_name = request.form.get("category_name", "").strip()

        if not category_name:
            flash(CATEGORY_ACCESS_ERROR_MSG)
            return redirect(url_for("add_category"))

        try:
            existing_category = mongo.db.categories.find_one(
                {"category_name": category_name}
            )
            if existing_category:
                flash(CATEGORY_EXISTS_ERROR_MSG)
                return redirect(url_for("add_category"))

            category = {"category_name": category_name}
            mongo.db.categories.insert_one(category)
            flash(CATEGORY_ADDED_MSG)
            return redirect(url_for("categories"))

        except PyMongoError as e:
            return handle_db_error(e)

    return render_template("add_category.html")


# Edit a category
@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    """
    Handle editing of existing categories.

    Args:
        category_id: The ID of the category to edit

    Returns:
        On GET: Rendered edit_category.html template with category data
        On POST: Redirect to categories page after successful update
    """
    if request.method == "POST":
        submit = {"category_name": request.form.get("category_name")}
        mongo.db.categories.update_one({"_id": ObjectId(category_id)}, {"$set": submit})
        flash(CATEGORY_UPDATED_MSG)
        return redirect(url_for("categories"))
    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


# Delete a category
@app.route("/delete_category/<category_id>")
@admin_required
def delete_category(category_id):
    """
    Handle deletion of categories.

    Args:
        category_id: The ID of the category to delete

    Returns:
        Redirect response to categories page

    Notes:
        - Only administrators can delete categories
        - Categories containing recipes cannot be deleted
        - Displays appropriate flash messages for success/failure
    """
    try:
        # Check if category exists
        try:
            category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
        except InvalidId:
            flash(CATEGORY_NOT_FOUND_MSG)
            return redirect(url_for("categories"))

        if not category:
            flash(CATEGORY_NOT_FOUND_MSG)
            return redirect(url_for("categories"))

        # Check for recipes using this category
        recipes = list(
            mongo.db.recipes.find({"category_name": category["category_name"]})
        )
        if recipes:
            flash(
                CATEGORY_DELETE_ERROR_MSG.format(
                    category_name=category["category_name"], recipe_count=len(recipes)
                )
            )
            return redirect(url_for("categories"))

        mongo.db.categories.delete_one({"_id": ObjectId(category_id)})
        flash(CATEGORY_DELETED_MSG)
    except PyMongoError as e:
        return handle_db_error(e)
    return redirect(url_for("categories"))


# 404 Error
@app.errorhandler(404)
def page_not_found(_):
    """
    Handle 404 page not found errors.

    Args:
        _ (Exception): Flask's error object (unused but required)

    Returns:
        tuple: Rendered 404 template and 404 status code
    """
    return render_template("404.html"), 404


# Run the app
if __name__ == "__main__":
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=debug,
    )
