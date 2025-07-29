import psycopg2
from psycopg2 import sql 

# PostgreSQL connection details
DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'datadrill_db'
DB_USER = 'datadrill_user'
DB_PASSWORD = 'Dhruv@123' 

def create_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print(f"Connected to PostgreSQL database: {DB_NAME}")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return conn

def create_tables(conn):
    try:
        cursor = conn.cursor()
        # Users table
        cursor.execute(sql.SQL('''
            CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                registration_date DATE NOT NULL
            )
        ''').format(sql.Identifier('users'))) #  sql.Identifier for table names

        # Orders table
        cursor.execute(sql.SQL('''
            CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price NUMERIC(10, 2) NOT NULL,
                order_date DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES {} (id)
            )
        ''').format(sql.Identifier('orders'), sql.Identifier('users')))

        conn.commit()
        print("Tables created successfully.")
    except psycopg2.Error as e:
        print(f"Error creating tables: {e}")
        conn.rollback() # Rollback in case of error

def insert_sample_data(conn):
    try:
        cursor = conn.cursor()
        # Insert users
        users_data = [
            ('Alice Smith', 'alice@example.com', '2023-01-15'),
            ('Bob Johnson', 'bob@example.com', '2023-02-20'),
            ('Charlie Brown', 'charlie@example.com', '2023-03-01'),
            ('Diana Prince', 'diana@example.com', '2023-04-10'),
            ('Eve Adams', 'eve@example.com', '2024-05-05')
        ]
        # Use psycopg2's parameter placeholder: %s
        cursor.executemany("INSERT INTO users (name, email, registration_date) VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING", users_data)

        # Insert orders
        orders_data = [
            (1, 'Laptop', 1, 1200.00, '2023-06-01'),
            (1, 'Mouse', 2, 25.00, '2023-06-01'),
            (2, 'Keyboard', 1, 75.00, '2023-07-10'),
            (3, 'Monitor', 1, 300.00, '2023-08-15'),
            (4, 'Webcam', 1, 50.00, '2023-09-01'),
            (1, 'Headphones', 1, 150.00, '2023-10-20'),
            (5, 'Smartwatch', 1, 250.00, '2024-06-01'),
            (2, 'SSD', 1, 80.00, '2024-07-25')
        ]
        cursor.executemany("INSERT INTO orders (user_id, product_name, quantity, price, order_date) VALUES (%s, %s, %s, %s, %s)", orders_data)

        conn.commit()
        print("Sample data inserted successfully.")
    except psycopg2.Error as e:
        print(f"Error inserting sample data: {e}")
        conn.rollback()

if __name__ == '__main__':
    conn = create_connection()
    if conn:
        create_tables(conn)
        insert_sample_data(conn)
        conn.close()