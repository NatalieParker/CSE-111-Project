from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    flash,
)
import sqlite3

DB_PATH = "project.db"

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # 세션/flash 메시지용


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn



# # ---------- 인증용 user_account 테이블 생성 (없으면 자동 생성) ----------

# def init_auth_schema():
#     conn = get_db_connection()
#     cur = conn.cursor()

#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS user_account (
#             user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
#             username    TEXT UNIQUE NOT NULL,
#             password    TEXT NOT NULL,
#             role        TEXT NOT NULL CHECK(role IN ('admin', 'customer'))
#         );
#     """)

#     # 기본 admin 계정 없으면 생성
#     cur.execute("SELECT COUNT(*) AS c FROM user_account WHERE role = 'admin';")
#     row = cur.fetchone()
#     if row["c"] == 0:
#         print("[INFO] No admin account found. Creating default admin (admin / admin123).")
#         cur.execute("""
#             INSERT INTO user_account (username, password, role)
#             VALUES (?, ?, 'admin');
#         """, ("admin", "admin123"))

#     conn.commit()
#     conn.close()


# # ---------- 라우트: 로그인 / 회원가입 / 로그아웃 / 홈 ----------

# @app.route("/", methods=["GET", "POST"])
# def login():
#     """
#     루트(/)를 로그인 페이지로 사용.
#     GET  -> login.html 렌더링
#     POST -> username/password 체크 후 성공 시 /home 또는 /admin 으로 리다이렉트
#     """
#     if request.method == "POST":
#         username = request.form.get("username", "").strip()
#         password = request.form.get("password", "").strip()

#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute("""
#             SELECT user_id, username, password, role
#             FROM user_account
#             WHERE username = ?;
#         """, (username,))
#         user = cur.fetchone()
#         conn.close()

#         if user is None or user["password"] != password:
#             flash("Invalid username or password", "error")
#             return render_template("login.html")

#         # 로그인 성공 → 세션에 저장
#         session["user_id"] = user["user_id"]
#         session["username"] = user["username"]
#         session["role"] = user["role"]

#         # role에 따라 다른 페이지로
#         if user["role"] == "admin":
#             return redirect(url_for("admin_dashboard"))
#         else:
#             return redirect(url_for("home"))

#     # GET 요청일 때 로그인 페이지
#     return render_template("login.html")


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     """
#     회원가입 페이지: user_account에 customer 계정 추가
#     (customer 테이블과 연결까지 할 수도 있지만 여기서는 user_account만)
#     """
#     if request.method == "POST":
#         username = request.form.get("username", "").strip()
#         password = request.form.get("password", "").strip()

#         if not username or not password:
#             flash("Username and password are required.", "error")
#             return render_template("register.html")

#         conn = get_db_connection()
#         cur = conn.cursor()
#         # username 중복 체크
#         cur.execute("SELECT 1 FROM user_account WHERE username = ?;", (username,))
#         if cur.fetchone():
#             conn.close()
#             flash("Username already exists.", "error")
#             return render_template("register.html")

#         cur.execute("""
#             INSERT INTO user_account (username, password, role)
#             VALUES (?, ?, 'customer');
#         """, (username, password))
#         conn.commit()
#         conn.close()

#         flash("Registration successful. Please log in.", "success")
#         return redirect(url_for("login"))

#     return render_template("register.html")


# @app.route("/logout")
# def logout():
#     session.clear()
#     flash("Logged out.", "info")
#     return redirect(url_for("login"))


# @app.route("/home")
# def home():
#     """
#     일반 유저(고객)용 메인: 상품 검색 페이지(index.html)
#     """
#     if "user_id" not in session:
#         flash("Please log in first.", "error")
#         return redirect(url_for("login"))
#     # admin이 /home 가면 그냥 검색 페이지 보여줘도 되고, 막고 /admin으로 보낼 수도 있음
#     return render_template("index.html")
# =======
# @app.route("/")
# def main():
#     return render_template("main.html")

# @app.route("/cart")
# def cart():
#     return render_template("cart.html")
# >>>>>>> main


# ---------- 인증용 user_account 테이블 생성 (없으면 자동 생성) ----------

def init_auth_schema():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_account (
            user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            u_custkey   INTEGER INTEGER NOT NULL,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            role        TEXT NOT NULL CHECK(role IN ('admin', 'customer'))
        );
    """)

    # 기본 admin 계정 없으면 생성
    cur.execute("SELECT COUNT(*) AS c FROM user_account WHERE role = 'admin';")
    row = cur.fetchone()
    if row["c"] == 0:
        print("[INFO] No admin account found. Creating default admin (admin / admin123).")
        cur.execute("""
            INSERT INTO user_account (username, u_custkey, password, role)
            VALUES (?, '1000', ?, 'admin');
        """, ("admin", "admin123"))

    conn.commit()
    conn.close()


# ---------- 라우트: 로그인 / 회원가입 / 로그아웃 / 홈 ----------

@app.route("/", methods=["GET", "POST"])
def login():
    """
    루트(/)를 로그인 페이지로 사용.
    GET  -> login.html 렌더링
    POST -> username/password 체크 후 성공 시 /home 또는 /admin 으로 리다이렉트
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, u_custkey, username, password, role
            FROM user_account
            WHERE username = ?;
        """, (username,))
        user = cur.fetchone()
        conn.close()

        if user is None or user["password"] != password:
            flash("Invalid username or password", "error")
            return render_template("login.html")

        # 로그인 성공 → 세션에 저장
        session["user_id"] = user["user_id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        session["u_custkey"] = user["u_custkey"]

        # role에 따라 다른 페이지로
        if user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))
        else:
            return redirect(url_for("home"))

    # GET 요청일 때 로그인 페이지
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    회원가입 페이지: user_account에 customer 계정 추가
    (customer 테이블과 연결까지 할 수도 있지만 여기서는 user_account만)
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        address = request.form.get("address", "").strip()
        phonenum = request.form.get("phonenum", "").strip()

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        conn = get_db_connection()
        cur = conn.cursor()
        # username 중복 체크
        cur.execute("SELECT 1 FROM user_account WHERE username = ?;", (username,))
        if cur.fetchone():
            conn.close()
            flash("Username already exists.", "error")
            return render_template("register.html")
        
        cur.execute("SELECT COALESCE(MAX(c_custkey), 999) + 1 FROM customer;")
        new_cust_key = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO customer (c_custkey, c_name, c_address, c_citykey, c_phone, c_balance)
            VALUES(?, ?, ?, 1, ?, 100);
        """, (new_cust_key, username, address, phonenum))

        cur.execute("""
            INSERT INTO user_account (username, u_custkey, password, role)
            VALUES (?, ?, ?, 'customer');
        """, (username, new_cust_key, password))
        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))


@app.route("/home")
def home():
    """
    일반 유저(고객)용 메인: 상품 검색 페이지(main.html)
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))
    # admin이 /home 가면 그냥 검색 페이지 보여줘도 되고, 막고 /admin으로 보낼 수도 있음
    return render_template("main.html", customer_id=session.get("u_custkey"))


@app.route("/cart")
def cart():
    """
    장바구니 페이지
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))
    return render_template("cart.html")



# ---------- ADMIN 대시보드 & 관리 페이지들 ----------

def login_required(role=None):
    """간단한 권한 체크용 helper"""
    def decorator(fn):
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in first.", "error")
                return redirect(url_for("login"))
            if role is not None and session.get("role") != role:
                flash("You are not authorized to view this page.", "error")
                # 권한 없으면 home으로
                return redirect(url_for("home"))
            return fn(*args, **kwargs)
        wrapped.__name__ = fn.__name__
        return wrapped
    return decorator


@app.route("/admin")
@login_required(role="admin")
def admin_dashboard():
    """
    관리자 메인 페이지: admin.html 템플릿 사용
    여기서 products/customers/transactions 탭으로 이동
    """
    return render_template("admin.html", section=None)

# ----- 관리자: 상품 관리 -----

@app.route("/admin/products", methods=["GET", "POST"])
@login_required(role="admin")
def admin_products():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")

        # 상품 추가
        if action == "add":
            name = request.form.get("name", "").strip()
            category = request.form.get("category", "").strip().upper()
            size = request.form.get("size", "").strip().upper()
            price = request.form.get("price", "").strip()

            if not name or not category or not size or not price:
                flash("All product fields are required to add.", "error")
            else:
                cur.execute("SELECT COALESCE(MAX(p_productKey), 4999) + 1 AS new_id FROM product;")
                new_pid = cur.fetchone()["new_id"]
                cur.execute("""
                    INSERT INTO product (p_productKey, p_name, p_category, p_size, p_price)
                    VALUES (?, ?, ?, ?, ?);
                """, (new_pid, name, category, size, float(price)))
                conn.commit()
                flash(f"Product {new_pid} added.", "success")

        # 상품 여러 필드 업데이트
        elif action == "update":
            pid = request.form.get("productKey")
            if not pid:
                flash("productKey is required to update.", "error")
            else:
                fields = []
                params = []

                new_name = request.form.get("name", "").strip()
                new_category = request.form.get("category", "").strip().upper()
                new_size = request.form.get("size", "").strip().upper()
                new_price = request.form.get("price", "").strip()

                if new_name:
                    fields.append("p_name = ?")
                    params.append(new_name)
                if new_category:
                    fields.append("p_category = ?")
                    params.append(new_category)
                if new_size:
                    fields.append("p_size = ?")
                    params.append(new_size)
                if new_price:
                    fields.append("p_price = ?")
                    params.append(float(new_price))

                if not fields:
                    flash("No fields provided to update.", "error")
                else:
                    sql = f"UPDATE product SET {', '.join(fields)} WHERE p_productKey = ?"
                    params.append(int(pid))
                    cur.execute(sql, params)
                    if cur.rowcount == 0:
                        flash("No such product.", "error")
                    else:
                        conn.commit()
                        flash("Product updated.", "success")

        # 상품 삭제
        elif action == "delete":
            pid = request.form.get("productKey")
            if not pid:
                flash("productKey is required to delete.", "error")
            else:
                cur.execute("DELETE FROM product WHERE p_productKey = ?;", (int(pid),))
                if cur.rowcount == 0:
                    flash("No such product.", "error")
                else:
                    conn.commit()
                    flash("Product deleted.", "success")

    # 리스트 표시
    cur.execute("SELECT p_productKey, p_name, p_category, p_size, p_price FROM product ORDER BY p_productKey;")
    products = cur.fetchall()
    conn.close()
    return render_template("admin.html", section="products", products=products)


# ----- 관리자: 고객 관리 -----

@app.route("/admin/customers", methods=["GET", "POST"])
@login_required(role="admin")
def admin_customers():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")

        # 고객 추가
        if action == "add":
            name = request.form.get("name", "").strip()
            address = request.form.get("address", "").strip()
            city_key = request.form.get("cityKey", "").strip()
            phone = request.form.get("phone", "").strip()

            if not name or not address or not city_key or not phone:
                flash("All customer fields are required to add.", "error")
            else:
                cur.execute("SELECT COALESCE(MAX(c_custKey), 999) + 1 AS new_id FROM customer;")
                new_cust_id = cur.fetchone()["new_id"]
                cur.execute("""
                    INSERT INTO customer (c_custKey, c_name, c_address, c_cityKey, c_phone, c_balance)
                    VALUES (?, ?, ?, ?, ?, 0.0);
                """, (new_cust_id, name, address, int(city_key), phone))
                conn.commit()
                flash(f"Customer {new_cust_id} added.", "success")

        # 고객 여러 필드 업데이트
        elif action == "update":
            cid = request.form.get("custKey")
            if not cid:
                flash("custKey is required to update.", "error")
            else:
                fields = []
                params = []

                new_name = request.form.get("name", "").strip()
                new_address = request.form.get("address", "").strip()
                new_city = request.form.get("cityKey", "").strip()
                new_phone = request.form.get("phone", "").strip()
                new_balance = request.form.get("balance", "").strip()

                if new_name:
                    fields.append("c_name = ?")
                    params.append(new_name)
                if new_address:
                    fields.append("c_address = ?")
                    params.append(new_address)
                if new_city:
                    fields.append("c_cityKey = ?")
                    params.append(int(new_city))
                if new_phone:
                    fields.append("c_phone = ?")
                    params.append(new_phone)
                if new_balance:
                    fields.append("c_balance = ?")
                    params.append(float(new_balance))

                if not fields:
                    flash("No fields provided to update.", "error")
                else:
                    sql = f"UPDATE customer SET {', '.join(fields)} WHERE c_custKey = ?"
                    params.append(int(cid))
                    cur.execute(sql, params)
                    if cur.rowcount == 0:
                        flash("No such customer.", "error")
                    else:
                        conn.commit()
                        flash("Customer updated.", "success")

        # 고객 삭제
        elif action == "delete":
            cid = request.form.get("custKey")
            if not cid:
                flash("custKey is required to delete.", "error")
            else:
                cur.execute("DELETE FROM customer WHERE c_custKey = ?;", (int(cid),))
                if cur.rowcount == 0:
                    flash("No such customer.", "error")
                else:
                    conn.commit()
                    flash("Customer deleted.", "success")

    # 리스트 표시
    cur.execute("""
        SELECT c.c_custKey, c.c_name, c.c_address, c.c_cityKey, c.c_phone, c.c_balance
        FROM customer c
        ORDER BY c.c_custKey;
    """)
    customers = cur.fetchall()
    conn.close()
    return render_template("admin.html", section="customers", customers=customers)


# ----- 관리자: 트랜잭션 관리 -----

@app.route("/admin/transactions", methods=["GET", "POST"])
@login_required(role="admin")
def admin_transactions():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")

        # 트랜잭션 추가
        if action == "add":
            cust_key = request.form.get("custKey", "").strip()
            store_key = request.form.get("storeKey", "").strip()
            status = request.form.get("status", "").strip().upper() or "U"
            date = request.form.get("date", "").strip()
            total = request.form.get("total", "").strip()

            if not cust_key or not store_key or not date:
                flash("custKey, storeKey, date are required to add.", "error")
            else:
                cur.execute("SELECT COALESCE(MAX(t_transactionKey), 8999) + 1 AS new_id FROM transactions;")
                new_tid = cur.fetchone()["new_id"]
                total_val = float(total) if total else 0.0
                cur.execute("""
                    INSERT INTO transactions
                    (t_transactionKey, t_custKey, t_storeKey, t_transactionstatus, t_totalpayment, t_transactiondate)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (new_tid, int(cust_key), int(store_key), status, total_val, date))
                conn.commit()
                flash(f"Transaction {new_tid} added.", "success")

        # 트랜잭션 여러 필드 업데이트
        elif action == "update":
            tid = request.form.get("transKey")
            if not tid:
                flash("transKey is required to update.", "error")
            else:
                fields = []
                params = []

                new_cust = request.form.get("custKey", "").strip()
                new_store = request.form.get("storeKey", "").strip()
                new_status = request.form.get("status", "").strip().upper()
                new_date = request.form.get("date", "").strip()
                new_total = request.form.get("total", "").strip()

                if new_cust:
                    fields.append("t_custKey = ?")
                    params.append(int(new_cust))
                if new_store:
                    fields.append("t_storeKey = ?")
                    params.append(int(new_store))
                if new_status:
                    fields.append("t_transactionstatus = ?")
                    params.append(new_status)
                if new_date:
                    fields.append("t_transactiondate = ?")
                    params.append(new_date)
                if new_total:
                    fields.append("t_totalpayment = ?")
                    params.append(float(new_total))

                if not fields:
                    flash("No fields provided to update.", "error")
                else:
                    sql = f"UPDATE transactions SET {', '.join(fields)} WHERE t_transactionKey = ?"
                    params.append(int(tid))
                    cur.execute(sql, params)
                    if cur.rowcount == 0:
                        flash("No such transaction.", "error")
                    else:
                        conn.commit()
                        flash("Transaction updated.", "success")

        # 트랜잭션 삭제 (+ transprod도 같이 삭제)
        elif action == "delete":
            tid = request.form.get("transKey")
            if not tid:
                flash("transKey is required to delete.", "error")
            else:
                cur.execute("DELETE FROM transprod WHERE tp_transactionKey = ?;", (int(tid),))
                cur.execute("DELETE FROM transactions WHERE t_transactionKey = ?;", (int(tid),))
                if cur.rowcount == 0:
                    flash("No such transaction.", "error")
                else:
                    conn.commit()
                    flash("Transaction and its items deleted.", "success")

        # 품목 추가: transprod + totalpayment 증가
        elif action == "add_item":
            tid = request.form.get("transKey")
            pid = request.form.get("productKey")
            qty = request.form.get("quantity")

            if not tid or not pid or not qty:
                flash("transKey, productKey, quantity are required to add an item.", "error")
            else:
                qty_val = int(qty)
                # 가격 가져오기
                cur.execute("SELECT p_price FROM product WHERE p_productKey = ?;", (int(pid),))
                row = cur.fetchone()
                if row is None:
                    flash("No such product.", "error")
                else:
                    price = float(row["p_price"])
                    cur.execute("""
                        INSERT INTO transprod (tp_transactionKey, tp_productKey, tp_quantity)
                        VALUES (?, ?, ?);
                    """, (int(tid), int(pid), qty_val))
                    # totalpayment 증가
                    cur.execute("""
                        UPDATE transactions
                        SET t_totalpayment = t_totalpayment + ?
                        WHERE t_transactionKey = ?;
                    """, (price * qty_val, int(tid)))
                    conn.commit()
                    flash("Item added to transaction and total updated.", "success")

        # 해당 트랜잭션의 모든 품목 삭제 + total 0으로
        elif action == "delete_items":
            tid = request.form.get("transKey")
            if not tid:
                flash("transKey is required to delete items.", "error")
            else:
                cur.execute("DELETE FROM transprod WHERE tp_transactionKey = ?;", (int(tid),))
                cur.execute("""
                    UPDATE transactions
                    SET t_totalpayment = 0.0
                    WHERE t_transactionKey = ?;
                """, (int(tid),))
                conn.commit()
                flash("All items removed and total reset to 0.", "success")

        # transprod 기준으로 total 다시 계산
        elif action == "recalc_total":
            tid = request.form.get("transKey")
            if not tid:
                flash("transKey is required to recalc total.", "error")
            else:
                cur.execute("""
                    SELECT SUM(tp.tp_quantity * p.p_price) AS total
                    FROM transprod tp
                    JOIN product p ON p.p_productKey = tp.tp_productKey
                    WHERE tp.tp_transactionKey = ?;
                """, (int(tid),))
                row = cur.fetchone()
                total = row["total"] if row["total"] is not None else 0.0
                cur.execute("""
                    UPDATE transactions
                    SET t_totalpayment = ?
                    WHERE t_transactionKey = ?;
                """, (float(total), int(tid)))
                conn.commit()
                flash(f"Total recomputed to {total}.", "success")

    # 리스트 표시
    cur.execute("""
        SELECT t.t_transactionKey, t.t_custKey, t.t_storeKey,
               t.t_transactionstatus, t.t_totalpayment, t.t_transactiondate
        FROM transactions t
        ORDER BY t.t_transactiondate;
    """)
    transactions = cur.fetchall()
    conn.close()
    return render_template("admin.html", section="transactions", transactions=transactions)


# ---------- 기존 API: 캠퍼스 목록 ----------

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


# ---------- 기존 API: 스토어 + 상품 목록 ----------

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
    init_auth_schema()
    # app.run(debug=True)
    app.run(debug=True, port=5001)
