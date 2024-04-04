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
        sql = "UPDATE Users SET email = %s WHERE user_id = %s"
        cursor.execute(sql, (email, user_id))
        db.commit()
    except mysql.connector.Error as error:
        print("email:", error)


async def get_user_email(user_id):
    try:
        sql = "SELECT email FROM Users WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return None
    except mysql.connector.Error as error:
        print("email:", error)
