import mysql.connector
from Configuration.db_config import host, user, password, database

db = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

cursor = db.cursor()

async def set_user_email(user_id, email):
    try:
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            sql = "UPDATE Users SET email = %s WHERE user_id = %s"
            cursor.execute(sql, (email, user_id))
            db.commit()
            print(f"Email {user_id} - {email} updated successfully.")
        else:
            sql = "INSERT INTO Users (user_id, email) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, email))
            db.commit()
            print(f"User {user_id} added successfully.")
    except mysql.connector.Error as error:
        print("Error:", error)


async def get_user_email(user_id):
    try:
        sql = "SELECT email FROM Users WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()

        if result:
            email = result[0]
            print("Email found:", email)
            return email
        else:
            print("User not found.")
            return None

    except mysql.connector.Error as error:
        print("Error:", error)


async def set_access_token(user_id, access_token):
    try:
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            sql = "UPDATE Users SET access_token = %s WHERE user_id = %s"
            cursor.execute(sql, (access_token, user_id))
            db.commit()
            print("Access token updated successfully.")
        else:
            print("User does not exist. Cannot set access token.")
    except mysql.connector.Error as error:
        print("Error:", error)


async def get_access_token(user_id):
    try:
        cursor.execute("SELECT access_token FROM Users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            access_token = result[0]
            print("Access token retrieved successfully:", access_token)
            return access_token
        else:
            print("User not found or access token not set.")
            return None
    except mysql.connector.Error as error:
        print("Error:", error)


async def set_refresh_token(user_id, refresh_token):
    try:
        # Check if the user exists
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Update the refresh token if the user exists
            sql = "UPDATE Users SET refresh_token = %s WHERE user_id = %s"
            cursor.execute(sql, (refresh_token, user_id))
            db.commit()
            print("Refresh token updated successfully.")
        else:
            print("User does not exist. Cannot set refresh token.")
    except mysql.connector.Error as error:
        print("Error:", error)


async def get_refresh_token(user_id):
    try:
        # Fetch the refresh token for the given user ID
        cursor.execute("SELECT refresh_token FROM Users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            refresh_token = result[0]
            print("Refresh token retrieved successfully:", refresh_token)
            return refresh_token
        else:
            print("User not found or refresh token not set.")
            return None
    except mysql.connector.Error as error:
        print("Error:", error)
