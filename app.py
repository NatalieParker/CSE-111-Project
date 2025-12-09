from flask import Flask, render_template, request, jsonify
import sqlite3

DB_PATH = "project.db"

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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

@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json()
    cart = data.get("cart", [])
    customer_id = data.get("customerId")

    if not cart:
        return {"error": "Cart is empty"}, 400

    if not customer_id:
        return {"error": "Missing customerId"}, 400
    
    store_key = cart[0]["storeKey"]

    total_payment = sum(item["price"] * item["quantity"] for item in cart)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COALESCE(MAX(t_transactionKey), 0) + 1 FROM transactions;")
    new_tkey = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO transactions (
            t_transactionKey, t_custKey, t_storeKey, 
            t_transactionstatus, t_totalpayment, t_transactiondate
        ) VALUES (?, ?, ?, 'C', ?, DATE('now'))
    """, (new_tkey, customer_id, store_key, total_payment))

    for item in cart:
        cur.execute("""
            INSERT INTO transprod (
                tp_transactionKey, tp_productKey, tp_quantity
            ) VALUES (?, ?, ?)
        """, (new_tkey, item["productKey"], item["quantity"]))

        cur.execute("""
            UPDATE stock
            SET ps_quantity = ps_quantity - ?
            WHERE ps_storeKey = ? AND ps_productKey = ?
        """, (item["quantity"], item["storeKey"], item["productKey"]))

    cur.execute("""
        UPDATE customer
        SET c_balance = c_balance - ?
        WHERE c_custKey = ?
    """, (total_payment, customer_id))

    conn.commit()
    conn.close()

    return {"message": "Checkout successful", "transactionKey": new_tkey}

@app.route("/transactions")
def get_transactions():
    customer_id = request.args.get("customerId")

    if not customer_id:
        return jsonify({"error": "Missing customerId"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT t.t_transactionKey,
               t.t_transactiondate,
               t.t_totalpayment,
               t.t_transactionstatus,
               s.s_name AS store_name
        FROM transactions t
        JOIN store s ON t.t_storeKey = s.s_storeKey
        WHERE t.t_custKey = ?
        ORDER BY t.t_transactiondate DESC, t.t_transactionKey DESC;
    """, (customer_id,))

    rows = cur.fetchall()
    conn.close()

    return jsonify({
        "transactions": [
            {
                "transactionKey": row["t_transactionKey"],
                "date": row["t_transactiondate"],
                "total": row["t_totalpayment"],
                "status": row["t_transactionstatus"],
                "storeName": row["store_name"],
            }
            for row in rows
        ]
    })

if __name__ == "__main__":
    app.run(debug=True)