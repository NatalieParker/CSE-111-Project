from flask import Flask, render_template, request, jsonify
import sqlite3

DB_PATH = "project.db"

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # so we can access columns by name
    return conn

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/cart")
def cart():
    return render_template("cart.html")

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

@app.route("/stores")
def api_get_stores():
    campus_key = request.args.get("campusKey")
    category = request.args.get("category")

    conn = get_db_connection()
    cur = conn.cursor()

    if campus_key:
        cur.execute("""
            SELECT s_storeKey, s_name
            FROM store
            WHERE s_campusKey = ?
            ORDER BY s_name;
        """, (campus_key,))
    else:
        cur.execute("""
            SELECT s_storeKey, s_name
            FROM store
            ORDER BY s_name;
        """)

    stores = cur.fetchall()
    results = []

    for store in stores:
        storeKey = store["s_storeKey"]

        query = """
            SELECT p.p_productKey, p.p_name, p.p_price, p.p_category
            FROM product p
            JOIN stock ps ON ps.ps_productKey = p.p_productKey
            WHERE ps.ps_storeKey = ?
        """

        params = [storeKey]

        if category:
            query += " AND p.p_category = ?"
            params.append(category)

        query += " ORDER BY p.p_name;"

        cur.execute(query, params)
        products = cur.fetchall()

        results.append({
            "storeKey": storeKey,
            "storeName": store["s_name"],
            "products": [
                {
                    "productKey": p["p_productKey"],
                    "productName": p["p_name"],
                    "price": p["p_price"],
                    "category": p["p_category"]
                }
                for p in products
            ]
        })

    conn.close()
    return jsonify({"stores": results})

if __name__ == "__main__":
    app.run(debug=True)