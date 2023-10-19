from flask import Flask, render_template
import mysql.connector
from mysql.connector import errorcode

import os

dir_path = os.path.dirname(os.path.realpath(__file__))
template_path = os.path.join(dir_path, '..', 'templates')
static_path = os.path.join(dir_path, '..', 'static')

app = Flask(__name__, template_folder=template_path, static_folder=static_path)

def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="inflationdb.mysql.database.azure.com",
            username="Oakmont",
            password="StrattonStonks741",
            database="oakmont_padb",
        )
        print("Connection established\n")
        return connection
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Access denied. Check your credentials.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Database does not exist.")
        else:
            print(f"Error: {err}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")


def get_most_recent_prediction():
    # Establish database connection
    connection = create_db_connection()
    if not connection:
        return None

    # Create a cursor to execute the query
    cursor = connection.cursor()

    # Execute the query to get the most recent prediction based on the timestamp
    query = """
    SELECT prediction_timestamp, inflation_prediction 
    FROM results 
    ORDER BY prediction_timestamp DESC 
    LIMIT 1;
    """
    cursor.execute(query)

    # Fetch the result
    result = cursor.fetchone()
    data = None
    if result:
        data = {
            "timestamp": result[0].strftime('%Y-%m-%d %H:%M:%S'),
            "prediction": result[1]
        }

    cursor.close()
    connection.close()

    return data


@app.route('/')
def index():
    data = get_most_recent_prediction()
    if not data:
        data = {
            "timestamp": "N/A",
            "prediction": "N/A"
        }
    return render_template('index.html', timestamp=data["timestamp"], prediction=data["prediction"])

if __name__ == "__main__":
    app.run(debug=True)

