from flask import Flask, request, jsonify, render_template
import psycopg2 
from nlp_parser import parse_query

app = Flask(__name__)

# PostgreSQL connection details (same as in database.py)
DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'datadrill_db'
DB_USER = 'datadrill_user'
DB_PASSWORD = 'Dhruv@123'

def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        # For fetching results as dictionary-like objects
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise # Re-raise to be caught by the calling function

def execute_sql_query(sql_query):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)

        # Fetch columns and rows
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        processed_rows = [list(row) for row in rows] # Convert tuples to lists for JSON

        return {"columns": columns, "rows": processed_rows}
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": "An internal server error occurred."}
    finally:
        if conn:
            conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def devtools_config():
    return jsonify({}), 200

@app.route('/query', methods=['GET'])
def query_endpoint():
    plain_text_query = request.args.get('text')
    if not plain_text_query:
        return jsonify({"error": "Please provide a 'text' query parameter."}), 400

    sql_query = parse_query(plain_text_query)

    if not sql_query:
        return jsonify({"error": "Could not understand your query. Please try rephrasing."}), 400

    results = execute_sql_query(sql_query)

    if "error" in results:
        return jsonify(results), 500
    else:
        return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)