from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import mysql.connector
import uuid

from config import config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # sets max upload size to 1MB
app.config['SECRET_KEY'] = 'requiredKeyToStoreDataInSession'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'go_to_login_page'
connection = None


class User(UserMixin):
    # Assuming you have a User class for your user model
    def __init__(self, id, name, email, user_type):
        self.id = id
        self.name = name
        self.email = email
        self.user_type = user_type

    def get_id(self):
        return self.id
    
    def is_admin(self):
        return self.user_type == 'Admin'

def get_db_connection():
    global connection
    if connection is None or not connection.is_connected():
        connection = create_database_connection()
    return connection


def create_database_connection():
    try:
        conn = mysql.connector.connect(**config)
        print("Database connection successful")
        return conn
    except mysql.connector.Error as err:
        print("Database connection failed: {}".format(err))
        return None


def close_database_connection(conn):
    if conn:
        conn.close()
        print("Database connection closed")


def check_connection_status():
    return "Connected" if connection else "Not Connected"

@app.before_request
def before_request():
    g.db_conn = get_db_connection()

@app.teardown_appcontext
def teardown_db(exception=None):
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    global connection

    # Catch message passed from add_user route
    message = request.args.get('message', "")

    if request.method == 'POST':
        # Check if open_connection button was clicked
        if 'open_connection' in request.form:
            connection = create_database_connection()
            if connection:
                message = "Connected to the database successfully!"
            else:
                message = "Failed to connect to the database."

        # Check if close_connection button was clicked
        elif 'close_connection' in request.form:
            if connection:
                close_database_connection(connection)
                connection = None
                message = "Connection closed successfully!"
            else:
                message = "No active connection to close."

    # fetch users
    users = get_users_from_database()
    connection_status = "Connected" if connection else "Not Connected"
    return render_template('index.html', connection_status=connection_status, message=message, users=users)

@app.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    global connection
    message = ""

    if not current_user.is_admin():
        message = "User is not an admin"
        return redirect(url_for('index', message=message))

    if request.method == 'POST':
        username = request.form['username']
        if connection:
            cursor = connection.cursor()

            sql = "DELETE FROM Comments WHERE UserID = (SELECT UserID FROM User WHERE Name = %s)"
            cursor.execute(sql, (username,))

            sql = "DELETE FROM Rating WHERE UserID = (SELECT UserID FROM User WHERE Name = %s)"
            cursor.execute(sql, (username,))

            sql = "SELECT RecipeID FROM Recipe WHERE UserID = (SELECT UserID FROM User WHERE Name = %s)"
            cursor.execute(sql, (username,))
            recipe_ids = cursor.fetchall()

            for recipe_id in recipe_ids:
                sql = "DELETE FROM RecipeImage WHERE RecipeID = %s"
                cursor.execute(sql, (recipe_id[0],))

                sql = "DELETE FROM Recipe WHERE RecipeID = %s"
                cursor.execute(sql, (recipe_id[0],))

            sql = "DELETE FROM User WHERE Name = %s"
            cursor.execute(sql, (username,))

            connection.commit()
            cursor.close()
            message = f"User {username} and related data deleted successfully!"
        else:
            message = "No active connection. Can't delete user."

    return redirect(url_for('index', message=message))


@login_manager.user_loader
def load_user(Email):
    # Load user from your database
    return User.query.get(Email)


@app.route('/dashboard')
@login_required
def dashboard():
    return "Welcome to your dashboard"


@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    global connection
    message = ""

    if request.content_length > app.config['MAX_CONTENT_LENGTH']:
        abort(413)  # Payload Too Large

    if not current_user.is_admin():
        message = "User is not an admin"
        return redirect(url_for('index', message=message))

    if request.method == 'POST':
        # Get data from form
        name = request.form['name']
        cursor = connection.cursor()
        check_name_query = "SELECT COUNT(*) FROM User WHERE LOWER(Name) = %s"
        cursor.execute(check_name_query, (name.lower(),))
        result = cursor.fetchone()
        if result[0]:
            message = "Username is not unique"
            return redirect(url_for('index', message=message))
        cursor.close()

        email = request.form.get('email', None)  # email can be NULL based on your schema
        profile_picture = request.files['profile_picture'].read() if 'profile_picture' in request.files else None
        user_type = request.form['user_type']

        # Generate a UUID for the user_id
        user_id = str(uuid.uuid4())

        # Insert into database
        if connection:
            cursor = connection.cursor()
            insert_query = (
                "INSERT INTO User (Name, Email, ProfilePicture, UserType, UserID) VALUES (%s, %s, %s, %s, %s)"
            )
            data = (name, email, profile_picture, user_type, user_id)

            try:
                cursor.execute(insert_query, data)
                connection.commit()
                message = "User added successfully!"
            except mysql.connector.Error as err:
                print("Error: {}".format(err))
                message = "Failed to add user."
            finally:
                cursor.close()
        else:
            message = "No database connection."

    return redirect(url_for('index', message=message))

# Rating a recipe
@app.route('/rate_recipe', methods=['POST'])
@login_required
def rate_recipe(): 
    if request.method == 'POST':
        # User ID
        user_id = current_user.get_id()

        # Selected Rating
        rating = request.form['rating']

        # Recipe ID
        recipe_id = request.form['recipe_id']

        cursor = connection.cursor()
        if connection:
            cursor = connection.cursor()
            try:
                # Insert rating data
                insert_rating_query = (
                    '''INSERT INTO rating (RecipeID, UserID, Value) VALUES (%s, %s, %s) 
                    ON DUPLICATE KEY UPDATE Value = VALUES(Value);'''
                )
                cursor.execute(insert_rating_query, (recipe_id, user_id, rating))

                connection.commit()
                flash('Rating added successfully!')
            except mysql.connector.Error as err:
                connection.rollback()
                flash('An error occurred: ' + str(err))
            finally:
                cursor.close()
        else:
            flash('Database connection not established.')

        return redirect(url_for('view_recipe', recipe_id=recipe_id))
    else:
        return None

# Adding a comment to a recipe
@app.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    if request.method == 'POST':
        # Form data
        text = request.form['text']

        # Recipe ID
        recipe_id = request.form['recipe_id']

        # User ID
        user_id = current_user.get_id()

        # Comment ID
        comment_id = str(uuid.uuid4())

        cursor = connection.cursor()
        if connection:
            cursor = connection.cursor()
            try:
                # Insert comment data
                insert_recipe_query = (
                    'INSERT INTO comments (CommentID, Body, UserID, Recipe) VALUES (%s, %s, %s, %s)'
                )
                cursor.execute(insert_recipe_query, (comment_id, text, user_id, recipe_id))

                connection.commit()
                flash('Commment added successfully!')
            except mysql.connector.Error as err:
                connection.rollback()
                flash('An error occurred: ' + str(err))
            finally:
                cursor.close()
        else:
            flash('Database connection not established.')

        return redirect(url_for('view_recipe', recipe_id=recipe_id))
    else:
        return None


@app.route('/remove_recipe/<recipe_id>', methods=['POST'])
@login_required
def remove_recipe(recipe_id):
    if not current_user.is_admin():
        message = "User is not an admin"
        return redirect(url_for('index', message=message))

    # Assuming you have a connection to your database
    cursor = connection.cursor()
    try:
        # Delete the recipe from the database
        cursor.execute("DELETE FROM recipe WHERE RecipeID = %s", (recipe_id,))
        connection.commit()
        flash('Recipe removed successfully.')
    except Exception as ex:
        flash('Error removing recipe: ' + str(e))
    finally:
        cursor.close()

    return redirect(url_for('go_to_user_page'))

@app.route('/remove_comment/<comment_id>', methods=['POST'])
@login_required
def remove_comment(comment_id):
    # Assuming you have a connection to your database
    cursor = connection.cursor()
    try:
        # Delete the recipe from the database
        cursor.execute("DELETE FROM comments WHERE CommentID = %s", (comment_id,))
        connection.commit()
        flash('Recipe removed successfully.')
    except Exception as e:
        flash('Error removing recipe: ' + str(e))
    finally:
        cursor.close()

    return redirect(url_for('go_to_user_page'))


@app.route('/get_image/<int:user_id>')
def get_image(user_id):
    cursor = connection.cursor()
    cursor.execute("SELECT ProfilePicture FROM user WHERE UserID = %s", (user_id,))
    data = cursor.fetchone()
    cursor.close()
    if data and data[0]:
        return app.response_class(data[0], content_type='image/jpeg')  # you might need to adjust the content type
    else:
        return "No image", 404


@app.route('/get_recipe_image/<image_id>')
def get_recipe_image(image_id):
    conn = get_db_connection()  # Ensure a valid connection
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Image FROM recipeimage WHERE ImageID = %s", (image_id,))
        image = cursor.fetchone()
        if image:
            return app.response_class(image[0], mimetype='image/jpeg')  # Adjust the MIME type if necessary
        else:
            return 'Image not found', 404
    except mysql.connector.Error as err:
        print("Database error: ", err)
        return "Database error", 500
    finally:
        cursor.close()


@app.route('/update_user', methods=['POST'])
def update_user():
    global connection
    message = ""
    user_id = request.form['user_id']
    name = request.form['name']
    email = request.form.get('email')
    profile_picture = request.files['profile_picture']
    user_type = request.form['user_type']
    if connection:
        cursor = connection.cursor()

        placeholders = ["name = %s"]
        values = [name]

        if email:
            placeholders.append("Email = %s")
            values.append(email)
        else:
            placeholders.append("Email = %s")
            values.append(None)

        if profile_picture:
            placeholders.append("`ProfilePicture` = %s")
            values.append(profile_picture.read())
        else:
            placeholders.append("`ProfilePicture` = %s")
            values.append(None)

        placeholders.append("`UserType` = %s")
        values.append(user_type)
        placeholders_str = ", ".join(placeholders)
        update_query = f"UPDATE user SET {placeholders_str} WHERE UserID = %s"
        cursor.execute(update_query, values + [user_id])

        connection.commit()
        message = 'User updated successfully!'
        cursor.close()
    else:
        message = "No database connection."

    return redirect(url_for('index', message=message))


@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        recipe_type = request.form['type']
        text = request.form['text']
        images = request.files.getlist('images')

        recipe_id = str(uuid.uuid4())
        user_id = current_user.get_id()

        cursor = connection.cursor()
        # if connection:
        #     cursor = connection.cursor()
        #     insert_query = (
        #         'INSERT INTO recipe (RecipeID, Title, Type, text, UserID) VALUES (%s, %s, %s, %s, %s)'
        #     )
        #     data = (recipe_id, title, recipe_type, text, user_id)
        #
        #     try:
        #         cursor.execute(insert_query, data)
        #         connection.commit()
        #         message = "Recipe added successfully!"
        #     except mysql.connector.Error as err:
        #         print("Error: {}".format(err))
        #         message = "Failed to add recipe."
        #     finally:
        #         cursor.close()
        #
        #     for image in images:
        #         if image:
        #             filename = secure_filename(image.filename)
        #             image_id = str(uuid.uuid4())
        #             image_path = os.path.join('path/to/save/images', filename)
        #             image.save(image_path)
        #             cursor.execute('INSERT INTO recipeimage (ImageID, RecipeID, Image) VALUES (%s, %s, %s)',
        #                            (image_id, recipe_id, filename))
        if connection:
            cursor = connection.cursor()
            try:
                # Insert recipe data
                insert_recipe_query = (
                    'INSERT INTO recipe (RecipeID, Title, Type, Text, UserID) VALUES (%s, %s, %s, %s, %s)'
                )
                cursor.execute(insert_recipe_query, (recipe_id, title, recipe_type, text, user_id))

                # Insert images
                for image in images:
                    if image:
                        filename = secure_filename(image.filename)
                        image_binary = image.read()
                        insert_image_query = (
                            'INSERT INTO recipeimage (RecipeID, Image) VALUES (%s, %s)'
                        )
                        cursor.execute(insert_image_query, (recipe_id, image_binary))

                connection.commit()
                flash('Recipe added successfully!')
            except mysql.connector.Error as err:
                connection.rollback()
                flash('An error occurred: ' + str(err))
            finally:
                cursor.close()
        else:
            flash('Database connection not established.')

        return redirect(url_for('index'))
    else:
        return render_template('add_new_recipe.html')


# grab users for display
def get_users_from_database():
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()
        cursor.close()
        # print(users)
        return users
    else:
        return None
    # global connection
    # if not connection:
    #     connection = create_database_connection()
    # if connection:
    #     cursor = connection.cursor(dictionary=True)
    #     cursor.execute("SELECT * FROM user")
    #     users = cursor.fetchall()
    #     cursor.close()
    #     return users
    # else:
    #     return None


def get_recipes_from_database():
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT recipe.*, user.Name
        FROM recipe
        JOIN user ON recipe.UserID = user.UserID;
        """)
        recipes = cursor.fetchall()
        cursor.close()
        return recipes
    else:
        return None


# Attempting displayign table on index.html
@app.route('/update_user_table', methods=['GET'])
def update_table():
    users = get_users_from_database()
    return render_template('user_table_format.html', fetchedUsers=users)


# Viewing individual recipes and related comments.
@app.route('/view_recipe/<recipe_id>')
def view_recipe(recipe_id):
    recipeData, commentsData, imageData, ratingData, userData = get_single_recipe_info(connection, recipe_id)

    # Calculate average rating
    total_ratings = len(ratingData)
    sum_ratings = sum([rating['Value'] for rating in ratingData]) if total_ratings > 0 else 0
    averageRating = sum_ratings / total_ratings if total_ratings > 0 else 0

    return render_template('single_recipe.html', recipeData=recipeData, commentsData=commentsData, imageData=imageData,
                           ratingData=ratingData, averageRating=averageRating, userData=userData)


def get_single_recipe_info(connection, recipeID):
    cursor = connection.cursor(dictionary=True)
    
    recipe_query = "SELECT * FROM recipe WHERE RecipeID = %s"
    cursor.execute(recipe_query, (recipeID,))
    recipeInfo = cursor.fetchall()

    comments_query = """
        SELECT comments.*, User.Name
        FROM comments
        JOIN user ON comments.UserID = user.UserID
        WHERE comments.Recipe = %s
    """
    cursor.execute(comments_query, (recipeID,))
    commentsInfo = cursor.fetchall()

    images_query = "SELECT * FROM recipeimage WHERE RecipeID = %s"
    cursor.execute(images_query, (recipeID,))
    imagesInfo = cursor.fetchall()

    ratings_query = """
        SELECT rating.*, User.Name
        FROM rating
        JOIN user ON rating.UserID = user.UserID
        WHERE rating.RecipeID = %s
    """
    cursor.execute(ratings_query, (recipeID,))
    ratingsInfo = cursor.fetchall()

    user_query = "SELECT * FROM user WHERE UserID IN (SELECT UserID FROM recipe WHERE RecipeID = %s)"
    cursor.execute(user_query, (recipeID,))
    userInfo = cursor.fetchall()

    cursor.close()

    return recipeInfo, commentsInfo, imagesInfo, ratingsInfo, userInfo


# Routes for nav bar:
@app.route("/stats_page")
def stats_page():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM User")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM User WHERE UserType = 'Admin'")
        admin_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Recipe")
        recipe_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Comments")
        comment_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Rating")
        rating_count = cursor.fetchone()[0]
        return render_template("stats.html", user_count=user_count, admin_count=admin_count, recipe_count=recipe_count, comment_count=comment_count, rating_count=rating_count)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()

@app.route('/go_to_recipe_page')
def go_to_recipe_page():
    recipes = get_recipes_from_database()
    return render_template('recipe_page.html', fetchedRecipes=recipes)

@app.route('/go_to_index')
def go_to_index():
    message = check_connection_status()
    return redirect(url_for('index', message=message))

@app.route('/go_to_login_page')
def go_to_login_page():
    return render_template('login_page.html')

@app.route('/user_page')
@login_required
def go_to_user_page():
    user_id = current_user.get_id()
    cursor = connection.cursor(dictionary=True)

    # Query to fetch user's recipes
    cursor.execute("SELECT * FROM recipe WHERE UserID = %s", (user_id,))
    user_recipes = cursor.fetchall()

    # Query to fetch user's recipes
    cursor.execute("SELECT * FROM comments WHERE UserID = %s", (user_id,))
    user_comments = cursor.fetchall()
    cursor.close()

    return render_template('user_page.html', user=current_user, recipes=user_recipes, comments=user_comments)


# login as a user via UUID
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        user_email = request.form.get('user_email_form')
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE Email = %s", (user_email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            username = user['Name']
            # session['currUser'] = user
            user_data = User(user['UserID'], user['Name'], user['Email'], user['UserType'])
            login_user(user_data)
            loginStatus = f"Login successful. Welcome, {username}!"
        else:
            loginStatus = "Login failed. UserID not found."

        return render_template('login_page.html', login_status=loginStatus)

    return render_template('login_page.html')


@login_manager.user_loader
def load_user(user_id):
    global connection
    if connection is None:
        connection = create_database_connection()

    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE UserID = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        if user_data:
            return User(user_data['UserID'], user_data['Name'], user_data['Email'], user_data['UserType'])
        return None
    else:
        print("Database connection could not be established.")
        return None


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    # return redirect(url_for('index'))
    loginStatus = "Logout successful"

    return render_template('login_page.html', login_status=loginStatus)


if __name__ == '__main__':
    app.run(debug=True)
