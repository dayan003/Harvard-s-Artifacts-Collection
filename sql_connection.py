import pymysql
def get_connection():
    conn = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="Yochi@09",
        database="harvard_db"
    )
    return conn
get_connection()