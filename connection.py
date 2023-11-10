from MySQLdb import connections
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # sets max upload size to 1MB

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MintySQL', # <-- ENTER YOUR PASSWORD. DO NOT PUSH WITH PASSWORD.
    'database': 'newrecipe'
}

connection = None

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



# @app.route('/', methods=['GET', 'POST'])
# def index():
#     global connection
#     message = ""
#
#     if request.method == 'POST':
#         # Check if open_connection button was clicked
#         if 'open_connection' in request.form:
#             connection = create_database_connection()
#             if connection:
#                 message = "Connected to the database successfully!"
#             else:
#                 message = "Failed to connect to the database."
#
#         # Check if close_connection button was clicked
#         elif 'close_connection' in request.form:
#             if connection:
#                 close_database_connection(connection)
#                 connection = None
#                 message = "Connection closed successfully!"
#             else:
#                 message = "No active connection to close."
#
#         # Delete user functionality
#         elif 'delete_user' in request.form:
#             username = request.form['username']
#             if connection:
#                 cursor = connection.cursor()
#
#                 sql = "DELETE FROM Comments WHERE UserID = (SELECT UserID FROM User WHERE Name = %s)"
#                 cursor.execute(sql, (username,))
#
#                 sql = "DELETE FROM Rating WHERE UserID = (SELECT UserID FROM User WHERE Name = %s)"
#                 cursor.execute(sql, (username,))
#
#                 sql = "SELECT RecipeID FROM Recipe WHERE UserID = (SELECT UserID FROM User WHERE Name = %s)"
#                 cursor.execute(sql, (username,))
#                 recipe_ids = cursor.fetchall()
#
#                 for recipe_id in recipe_ids:
#                     sql = "DELETE FROM RecipeImage WHERE RecipeID = %s"
#                     cursor.execute(sql, (recipe_id[0],))
#
#                     sql = "DELETE FROM Recipe WHERE RecipeID = %s"
#                     cursor.execute(sql, (recipe_id[0],))
#
#                 sql = "DELETE FROM User WHERE Name = %s"
#                 cursor.execute(sql, (username,))
#
#                 connection.commit()
#                 cursor.close()
#                 message = f"User {username} and related data deleted successfully!"
#             else:
#                 message = "No active connection. Can't delete user."
#
#     connection_status = "Connected" if connection else "Not Connected"
#     return render_template('index.html', connection_status=connection_status, message=message)

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

        # Delete user functionality
        elif 'delete_user' in request.form:
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
    #fetch users
    users = get_users_from_database()
    connection_status = "Connected" if connection else "Not Connected"
    return render_template('index.html', connection_status=connection_status, message=message,users = users)




@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    global connection
    message = ""

    if request.content_length > app.config['MAX_CONTENT_LENGTH']:
        abort(413)  # Payload Too Large

    if request.method == 'POST':
        # Get data from form
        name = request.form['name']
        email = request.form.get('email', None)  # email can be NULL based on your schema
        profile_picture = request.files['profile_picture'].read() if 'profile_picture' in request.files else None
        user_type = request.form['user_type']

        # Generate a UUID for the user_id
        user_id = str(uuid.uuid4())

        # Insert into database
        if connection:
            cursor = connection.cursor()
            insert_query = (
                "INSERT INTO user (Name, Email, ProfilePicture, UserType, UserID) VALUES (%s, %s, %s, %s, %s)"
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

    connection_status = "Connected" if connection else "Not Connected"
    # return render_template('add_user.html', message=message, connection_status=connection_status)
    return redirect(url_for('index', message=message))



@app.route('/get_image/<int:user_id>')
def get_image(user_id):
    cursor = connection.cursor()
    cursor.execute("SELECT ProfilePicture FROM user WHERE UserID = %s", (user_id,))
    data = cursor.fetchone()
    cursor.close()
    if data and data[0]:
        return app.response_class(data[0], content_type='image/jpeg') # you might need to adjust the content type
    else:
        return "No image", 404

@app.route('/update_user', methods=['POST'])
def update_user():
    global connection
    message=""
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

    return redirect(url_for('index',message=message))

#grab users for display
def get_users_from_database():
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()
        cursor.close()
        #print(users)
        return users
    else:
        return None

#Attempting displayign table on index.html
@app.route('/update_user_table', methods=['GET'])
def update_table():
    users = get_users_from_database()
    return render_template('user_table_format.html', fetchedUsers=users)


if __name__ == '__main__':
    app.run(debug=True)
