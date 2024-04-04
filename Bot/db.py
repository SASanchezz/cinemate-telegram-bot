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
