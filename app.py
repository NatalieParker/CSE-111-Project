from flask import Flask, render_template, request
import sqlite3

DB_PATH = "project.db"

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # so we can access columns by name
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/campuses")
def api_get_campuses():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT ca_campusKey, ca_name, ca_cityKey FROM campus ORDER BY ca_name;")
    campuses = cur.fetchall()

    conn.close()

    return {
        "campuses": [
            {
                "campusKey": row["ca_campusKey"],
                "campusName": row["ca_name"],
                "cityKey": row["ca_cityKey"],
            }
            for row in campuses
        ]
    }

if __name__ == "__main__":
    app.run(debug=True)