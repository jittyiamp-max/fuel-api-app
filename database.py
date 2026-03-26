import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': '192.168.100.14',
    'port': 3306,
    'database': 'app_run',
    'user': 'root',
    'password': 'P@ssword'
}

def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as err:
        if err.errno == 2003:
            print(f"Error: Can't connect to MySQL server on '{DB_CONFIG['host']}'")
        elif err.errno == 1045:
            print(f"Error: Access denied for user '{DB_CONFIG['user']}'")
        else:
            print(f"Error: {err}")
        return None

# Create tables if they don't exist
def create_tables():
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create fuel_oil table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fuel_oil (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    odometer FLOAT NOT NULL,
                    liters FLOAT NOT NULL,
                    price_per_liter FLOAT NOT NULL,
                    total_cost FLOAT NOT NULL,
                    fill_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            connection.commit()
            print("Tables created successfully!")
        except Error as err:
            print(f"Error creating tables: {err}")
        finally:
            cursor.close()
            connection.close()