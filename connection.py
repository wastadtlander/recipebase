from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

config = {
    'host': 'localhost',
    'user': 'root',
    'password': '', # <-- ENTER YOUR PASSWORD. DO NOT PUSH WITH PASSWORD.
    'database': 'recipebase'
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

@app.route('/', methods=['GET', 'POST'])
def index():
    global connection
    if request.method == 'POST':
        if 'open_connection' in request.form:
            connection = create_database_connection()
        elif 'close_connection' in request.form:
            close_database_connection(connection)
            connection = None 
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
    connection_status = "Connected" if connection else "Not Connected"
    return render_template('index.html', connection_status=connection_status)

if __name__ == '__main__':
    app.run(debug=True)
