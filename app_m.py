import sqlite3
from getpass import getpass  # 비밀번호 입력 시 화면에 안 보이게 (터미널에서만)

DB_PATH = "project.db"  # 여기 DB 파일 이름 맞춰줘


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# =========================
# 초기 설정: user_account 테이블 & 기본 admin 계정
# =========================

def init_auth_schema():
    conn = get_connection()
    cur = conn.cursor()

    # 스키마 변경을 위해 user_account 테이블이 있으면 삭제
    cur.execute("DROP TABLE IF EXISTS user_account;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_account (
            user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            role        TEXT NOT NULL CHECK(role IN ('admin','customer')),
            customer_id INTEGER
            -- customer_id에는 customer.c_custKey를 저장 (FK 제약은 생략)
        );
    """)

    # admin 계정 없으면 기본 admin 생성
    cur.execute("SELECT COUNT(*) AS c FROM user_account WHERE role = 'admin';")
    row = cur.fetchone()
    if row is None or row["c"] == 0:
        print("[INFO] No admin account found. Creating default admin (username: admin, password: admin123).")
        cur.execute("""
            INSERT INTO user_account (username, password, role, customer_id)
            VALUES (?, ?, 'admin', NULL);
        """, ("admin", "admin123"))

    conn.commit()
    conn.close()


# =========================
# 로그인 / 회원가입
# =========================

def register_user():
    conn = get_connection()
    cur = conn.cursor()

    print("\n=== User Registration ===")
    # username 중복 확인
    while True:
        username = input("Choose a username: ").strip()
        if not username:
            print("Username cannot be empty.")
            continue

        cur.execute("SELECT 1 FROM user_account WHERE username = ?;", (username,))
        if cur.fetchone():
            print("Username already exists. Try another.")
        else:
            break

    password = getpass("Choose a password: ").strip()
    if not password:
        print("Password cannot be empty.")
        conn.close()
        return

    print("\nNow let's create the customer profile.")

    # customer(c_custKey, c_name, c_address, c_cityKey, c_phone, c_balance)
    name = input("Name: ").strip()
    address = input("Address: ").strip()
    phone = input("Phone: ").strip()

    print("\nAvailable cities:")
    cur.execute("SELECT ci_cityKey, ci_name FROM city;")
    cities = cur.fetchall()
    for row in cities:
        print(f"{int(row['ci_cityKey'])} - {row['ci_name']}")
    city_id = int(input("Enter ci_cityKey for your address: ").strip())

    # 새로운 c_custKey 생성 (MAX + 1)
    cur.execute("SELECT COALESCE(MAX(c_custKey), 999) + 1 AS new_id FROM customer;")
    new_cust_id = cur.fetchone()["new_id"]

    cur.execute("""
        INSERT INTO customer (c_custKey, c_name, c_address, c_cityKey, c_phone, c_balance)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (new_cust_id, name, address, city_id, phone, 0.0))

    # user_account에 customer 연결
    cur.execute("""
        INSERT INTO user_account (username, password, role, customer_id)
        VALUES (?, ?, 'customer', ?);
    """, (username, password, new_cust_id))

    conn.commit()
    conn.close()
    print("\n[SUCCESS] Registration completed. You can now log in.")


def login():
    conn = get_connection()
    cur = conn.cursor()

    print("\n=== Login ===")
    username = input("Username: ").strip()
    password = getpass("Password: ").strip()

    cur.execute("""
        SELECT user_id, username, password, role, customer_id
        FROM user_account
        WHERE username = ?;
    """, (username,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        print("Invalid username.")
        return None

    if password != row["password"]:
        print("Invalid password.")
        return None

    print(f"\n[WELCOME] {row['username']} ({row['role']})")
    return dict(row)


# =========================
# 관리자 메뉴
# =========================

def admin_menu(user):
    while True:
        print("""
=== Admin Menu ===
1. List all products
2. Add product
3. Update product (name/category/size/price)
4. Delete product

5. List customers
6. Add customer
7. Update customer
8. Delete customer

9. List transactions
10. Add transaction
11. Update transaction
12. Delete transaction

0. Logout
""")
        choice = input("Select an option: ").strip()

        if choice == "1":
            admin_list_products()
        elif choice == "2":
            admin_add_product()
        elif choice == "3":
            admin_update_product()
        elif choice == "4":
            admin_delete_product()
        elif choice == "5":
            admin_list_customers()
        elif choice == "6":
            admin_add_customer()
        elif choice == "7":
            admin_update_customer()
        elif choice == "8":
            admin_delete_customer()
        elif choice == "9":
            admin_list_transactions()
        elif choice == "10":
            admin_add_transaction()
        elif choice == "11":
            admin_update_transaction()
        elif choice == "12":
            admin_delete_transaction()
        elif choice == "0":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Try again.")


# =========================
# 관리자 기능 - PRODUCT
# =========================

def admin_list_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT p_productKey, p_name, p_category, p_size, p_price FROM product;")
    rows = cur.fetchall()
    print("\n--- Product List ---")
    for r in rows:
        print(f"{int(r['p_productKey']):5d} | {r['p_name']:<20} | {r['p_category']:<8} | "
              f"{r['p_size']} | ${float(r['p_price']):.2f}")
    conn.close()


def admin_add_product():
    conn = get_connection()
    cur = conn.cursor()

    print("\n=== Add Product ===")
    name = input("Product name: ").strip()
    category = input("Category (e.g., APPAREL, MERCH, STAT, TECH): ").strip().upper()
    size = input("Size (S/M/L): ").strip().upper()
    price = float(input("Price: ").strip())

    # 새 p_productKey 생성
    cur.execute("SELECT COALESCE(MAX(p_productKey), 4999) + 1 AS new_id FROM product;")
    new_pid = cur.fetchone()["new_id"]

    cur.execute("""
        INSERT INTO product (p_productKey, p_name, p_category, p_size, p_price)
        VALUES (?, ?, ?, ?, ?);
    """, (new_pid, name, category, size, price))
    conn.commit()
    conn.close()
    print(f"[SUCCESS] Product added with p_productKey={new_pid}.")


def admin_update_product():
    conn = get_connection()
    cur = conn.cursor()

    pid = int(input("Enter p_productKey to update: ").strip())

    cur.execute("SELECT * FROM product WHERE p_productKey = ?;", (pid,))
    row = cur.fetchone()
    if row is None:
        print("No such product.")
        conn.close()
        return

    print("\nCurrent product info:")
    print(f"ID: {int(row['p_productKey'])}")
    print(f"Name: {row['p_name']}")
    print(f"Category: {row['p_category']}")
    print(f"Size: {row['p_size']}")
    print(f"Price: {float(row['p_price']):.2f}")

    print("""
What do you want to update?
1. Name
2. Category
3. Size
4. Price
5. All
0. Cancel
""")
    choice = input("Select: ").strip()

    if choice == "0":
        print("Cancelled.")
        conn.close()
        return

    new_name = row["p_name"]
    new_cat = row["p_category"]
    new_size = row["p_size"]
    new_price = row["p_price"]

    if choice in ("1", "5"):
        new_name = input("New name: ").strip() or new_name
    if choice in ("2", "5"):
        new_cat = input("New category: ").strip().upper() or new_cat
    if choice in ("3", "5"):
        new_size = input("New size (S/M/L): ").strip().upper() or new_size
    if choice in ("4", "5"):
        price_str = input("New price: ").strip()
        if price_str:
            new_price = float(price_str)

    cur.execute("""
        UPDATE product
        SET p_name = ?, p_category = ?, p_size = ?, p_price = ?
        WHERE p_productKey = ?;
    """, (new_name, new_cat, new_size, new_price, pid))

    conn.commit()
    conn.close()
    print("[SUCCESS] Product updated.")


def admin_delete_product():
    conn = get_connection()
    cur = conn.cursor()

    pid = int(input("Enter p_productKey to delete: ").strip())

    # transprod, stock에서 같이 지우는 게 좋지만, 여기선 단순하게 product만 삭제
    cur.execute("DELETE FROM product WHERE p_productKey = ?;", (pid,))
    if cur.rowcount == 0:
        print("No such product.")
    else:
        print("[SUCCESS] Product deleted.")
    conn.commit()
    conn.close()


# =========================
# 관리자 기능 - CUSTOMER
# =========================

def admin_list_customers():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.c_custKey, c.c_name, c.c_address, ci.ci_name AS city_name,
               c.c_phone, c.c_balance
        FROM customer c
        JOIN city ci ON c.c_cityKey = ci.ci_cityKey;
    """)
    rows = cur.fetchall()
    print("\n--- Customers ---")
    for r in rows:
        print(f"{int(r['c_custKey']):4d} | {r['c_name']:<10} | {r['city_name']:<12} | "
              f"{r['c_phone']:<15} | balance=${float(r['c_c_balance']) if 'c_c_balance' in r.keys() else float(r['c_balance']):.2f}")
    conn.close()


def admin_add_customer():
    conn = get_connection()
    cur = conn.cursor()

    print("\n=== Add Customer ===")
    name = input("Name: ").strip()
    address = input("Address: ").strip()
    phone = input("Phone: ").strip()

    print("\nAvailable cities:")
    cur.execute("SELECT ci_cityKey, ci_name FROM city;")
    cities = cur.fetchall()
    for row in cities:
        print(f"{int(row['ci_cityKey'])} - {row['ci_name']}")
    city_id = int(input("Enter ci_cityKey: ").strip())

    cur.execute("SELECT COALESCE(MAX(c_custKey), 999) + 1 AS new_id FROM customer;")
    new_cust_id = cur.fetchone()["new_id"]

    cur.execute("""
        INSERT INTO customer (c_custKey, c_name, c_address, c_cityKey, c_phone, c_balance)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (new_cust_id, name, address, city_id, phone, 0.0))

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Customer added with c_custKey={new_cust_id}.")


def admin_update_customer():
    conn = get_connection()
    cur = conn.cursor()

    cid = int(input("Enter c_custKey to update: ").strip())

    cur.execute("SELECT * FROM customer WHERE c_custKey = ?;", (cid,))
    row = cur.fetchone()
    if row is None:
        print("No such customer.")
        conn.close()
        return

    print("\nCurrent customer info:")
    print(f"ID: {int(row['c_custKey'])}")
    print(f"Name: {row['c_name']}")
    print(f"Address: {row['c_address']}")
    print(f"City key: {int(row['c_cityKey'])}")
    print(f"Phone: {row['c_phone']}")
    print(f"Balance: {float(row['c_balance']):.2f}")

    print("""
What do you want to update?
1. Name
2. Address
3. City
4. Phone
5. Balance
6. All
0. Cancel
""")
    choice = input("Select: ").strip()

    if choice == "0":
        print("Cancelled.")
        conn.close()
        return

    new_name = row["c_name"]
    new_addr = row["c_address"]
    new_city = row["c_cityKey"]
    new_phone = row["c_phone"]
    new_balance = row["c_balance"]

    if choice in ("1", "6"):
        tmp = input("New name: ").strip()
        if tmp:
            new_name = tmp
    if choice in ("2", "6"):
        tmp = input("New address: ").strip()
        if tmp:
            new_addr = tmp
    if choice in ("3", "6"):
        print("\nAvailable cities:")
        cur.execute("SELECT ci_cityKey, ci_name FROM city;")
        cities = cur.fetchall()
        for r in cities:
            print(f"{int(r['ci_cityKey'])} - {r['ci_name']}")
        tmp = input("New ci_cityKey: ").strip()
        if tmp:
            new_city = int(tmp)
    if choice in ("4", "6"):
        tmp = input("New phone: ").strip()
        if tmp:
            new_phone = tmp
    if choice in ("5", "6"):
        tmp = input("New balance: ").strip()
        if tmp:
            new_balance = float(tmp)

    cur.execute("""
        UPDATE customer
        SET c_name = ?, c_address = ?, c_cityKey = ?, c_phone = ?, c_balance = ?
        WHERE c_custKey = ?;
    """, (new_name, new_addr, new_city, new_phone, new_balance, cid))

    conn.commit()
    conn.close()
    print("[SUCCESS] Customer updated.")


def admin_delete_customer():
    conn = get_connection()
    cur = conn.cursor()

    cid = int(input("Enter c_custKey to delete: ").strip())

    # 관련 transactions, transprod 이 있다면 논리적으로 먼저 삭제하는 게 맞음
    # 여기서는 간단히 customer만 삭제 (제약 없으므로 가능)
    cur.execute("DELETE FROM customer WHERE c_custKey = ?;", (cid,))
    if cur.rowcount == 0:
        print("No such customer.")
    else:
        print("[SUCCESS] Customer deleted.")
    conn.commit()
    conn.close()


# =========================
# 관리자 기능 - TRANSACTIONS
# =========================

def admin_list_transactions():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT t.t_transactionKey, t.t_custKey, c.c_name,
               t.t_storeKey, s.s_name,
               t.t_transactionstatus, t.t_totalpayment, t.t_transactiondate
        FROM transactions t
        JOIN customer c ON t.t_custKey = c.c_custKey
        JOIN store s ON t.t_storeKey = s.s_storeKey
        ORDER BY t.t_transactiondate;
    """)
    rows = cur.fetchall()

    print("\n--- Transactions ---")
    for r in rows:
        print(f"{int(r['t_transactionKey'])} | cust {int(r['t_custKey'])} ({r['c_name']}) | "
              f"store {int(r['t_storeKey'])} ({r['s_name']}) | "
              f"status={r['t_transactionstatus']} | total=${float(r['t_totalpayment']):.2f} | "
              f"date={r['t_transactiondate']}")
    conn.close()


def admin_add_transaction():
    conn = get_connection()
    cur = conn.cursor()

    print("\n=== Add Transaction ===")

    # 고객 선택
    cur.execute("SELECT c_custKey, c_name FROM customer;")
    customers = cur.fetchall()
    print("\nCustomers:")
    for c in customers:
        print(f"{int(c['c_custKey'])} - {c['c_name']}")
    cust_key = int(input("Enter c_custKey: ").strip())

    # 스토어 선택
    cur.execute("SELECT s_storeKey, s_name FROM store;")
    stores = cur.fetchall()
    print("\nStores:")
    for s in stores:
        print(f"{int(s['s_storeKey'])} - {s['s_name']}")
    store_key = int(input("Enter s_storeKey: ").strip())

    status = input("Transaction status (R/S/C/D/U): ").strip().upper()
    if status == "":
        status = "U"

    date = input("Transaction date (YYYY-MM-DD): ").strip()

    # 새 transaction key 생성
    cur.execute("SELECT COALESCE(MAX(t_transactionKey), 8999) + 1 AS new_id FROM transactions;")
    new_tid = cur.fetchone()["new_id"]

    # 상품들 추가 (transprod)
    print("\nNow add products to this transaction.")
    print("Enter 0 as product key when you are done.")
    total = 0.0
    while True:
        pid_str = input("Product key (p_productKey, 0 to finish): ").strip()
        if not pid_str:
            continue
        pid = int(pid_str)
        if pid == 0:
            break
        qty = int(input("Quantity: ").strip())

        # 가격 가져오기
        cur.execute("SELECT p_price, p_name FROM product WHERE p_productKey = ?;", (pid,))
        row = cur.fetchone()
        if row is None:
            print("No such product, skipping.")
            continue
        price = float(row["p_price"])
        total += price * qty

        cur.execute("""
            INSERT INTO transprod (tp_transactionKey, tp_productKey, tp_quantity)
            VALUES (?, ?, ?);
        """, (new_tid, pid, qty))
        print(f"  Added {qty} x {row['p_name']} (${price:.2f} each).")

    # transactions 테이블에 삽입
    cur.execute("""
        INSERT INTO transactions
        (t_transactionKey, t_custKey, t_storeKey, t_transactionstatus, t_totalpayment, t_transactiondate)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (new_tid, cust_key, store_key, status, total, date))

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Transaction {new_tid} created, total=${total:.2f}.")


def admin_update_transaction():
    conn = get_connection()
    cur = conn.cursor()

    tid = int(input("Enter t_transactionKey to update: ").strip())

    cur.execute("""
        SELECT * FROM transactions WHERE t_transactionKey = ?;
    """, (tid,))
    row = cur.fetchone()
    if row is None:
        print("No such transaction.")
        conn.close()
        return

    print("\nCurrent transaction info:")
    print(f"ID: {int(row['t_transactionKey'])}")
    print(f"custKey: {int(row['t_custKey'])}")
    print(f"storeKey: {int(row['t_storeKey'])}")
    print(f"status: {row['t_transactionstatus']}")
    print(f"total: {float(row['t_totalpayment']):.2f}")
    print(f"date: {row['t_transactiondate']}")

    print("""
What do you want to update?
1. Status
2. Date
3. Store
0. Cancel
""")
    choice = input("Select: ").strip()

    if choice == "0":
        print("Cancelled.")
        conn.close()
        return

    new_status = row["t_transactionstatus"]
    new_date = row["t_transactiondate"]
    new_store = row["t_storeKey"]

    if choice == "1":
        tmp = input("New status (R/S/C/D/U): ").strip().upper()
        if tmp:
            new_status = tmp
    elif choice == "2":
        tmp = input("New date (YYYY-MM-DD): ").strip()
        if tmp:
            new_date = tmp
    elif choice == "3":
        cur.execute("SELECT s_storeKey, s_name FROM store;")
        stores = cur.fetchall()
        print("\nStores:")
        for s in stores:
            print(f"{int(s['s_storeKey'])} - {s['s_name']}")
        tmp = input("New s_storeKey: ").strip()
        if tmp:
            new_store = int(tmp)

    cur.execute("""
        UPDATE transactions
        SET t_transactionstatus = ?, t_transactiondate = ?, t_storeKey = ?
        WHERE t_transactionKey = ?;
    """, (new_status, new_date, new_store, tid))

    conn.commit()
    conn.close()
    print("[SUCCESS] Transaction updated.")


def admin_delete_transaction():
    conn = get_connection()
    cur = conn.cursor()

    tid = int(input("Enter t_transactionKey to delete: ").strip())

    # 먼저 transprod 삭제
    cur.execute("DELETE FROM transprod WHERE tp_transactionKey = ?;", (tid,))
    # 그 다음 transactions 삭제
    cur.execute("DELETE FROM transactions WHERE t_transactionKey = ?;", (tid,))

    if cur.rowcount == 0:
        print("No such transaction.")
    else:
        print("[SUCCESS] Transaction (and its products) deleted.")
    conn.commit()
    conn.close()


# =========================
# 고객 메뉴 및 기능
# =========================

def customer_menu(user):
    while True:
        print(f"""
=== Customer Menu ({user['username']}) ===
1. Search products
2. View my transactions
0. Logout
""")
        choice = input("Select an option: ").strip()

        if choice == "1":
            customer_search_products()
        elif choice == "2":
            customer_view_transactions(user)
        elif choice == "0":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Try again.")


def customer_search_products():
    conn = get_connection()
    cur = conn.cursor()

    print("\n=== Product Search ===")
    name_kw = input("Name keyword (press Enter to skip): ").strip()
    category = input("Category (APPAREL/MERCH/STAT/TECH, Enter=any): ").strip().upper()
    store_id_input = input("Store Key (s_storeKey, Enter=any): ").strip()

    query = """
        SELECT p.p_productKey, p.p_name, p.p_category, p.p_size, p.p_price,
               s.s_storeKey, s.s_name, st.ps_quantity
        FROM product p
        JOIN stock st ON p.p_productKey = st.ps_productKey
        JOIN store s ON st.ps_storeKey = s.s_storeKey
        WHERE 1=1
    """
    params = []

    if name_kw:
        query += " AND p.p_name LIKE ?"
        params.append(f"%{name_kw}%")

    if category:
        query += " AND p.p_category = ?"
        params.append(category)

    if store_id_input:
        query += " AND s.s_storeKey = ?"
        params.append(int(store_id_input))

    query += " ORDER BY s.s_storeKey, p.p_productKey;"

    cur.execute(query, params)
    rows = cur.fetchall()

    print("\n--- Search Results ---")
    for r in rows:
        print(f"Store {int(r['s_storeKey']):3d} ({r['s_name']:<20}) | "
              f"{int(r['p_productKey']):5d} {r['p_name']:<20} | {r['p_category']:<8} | {r['p_size']} | "
              f"${float(r['p_price']):.2f} | qty={int(r['ps_quantity'])}")
    conn.close()


def customer_view_transactions(user):
    if user["customer_id"] is None:
        print("This account is not linked to a customer profile.")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT t.t_transactionKey, t.t_storeKey, s.s_name,
               t.t_transactionstatus, t.t_totalpayment, t.t_transactiondate
        FROM transactions t
        JOIN store s ON t.t_storeKey = s.s_storeKey
        WHERE t.t_custKey = ?
        ORDER BY t.t_transactiondate;
    """, (user["customer_id"],))
    trans = cur.fetchall()

    if not trans:
        print("\nNo transactions found.")
        conn.close()
        return

    print("\n--- My Transactions ---")
    for t in trans:
        print(f"\nTransaction {t['t_transactionKey']} at store {t['t_storeKey']} ({t['s_name']}) "
              f"on {t['t_transactiondate']} | status={t['t_transactionstatus']} | "
              f"total=${float(t['t_totalpayment']):.2f}")
        cur.execute("""
            SELECT tp.tp_productKey, p.p_name, tp.tp_quantity, p.p_price
            FROM transprod tp
            JOIN product p ON tp.tp_productKey = p.p_productKey
            WHERE tp.tp_transactionKey = ?;
        """, (t["t_transactionKey"],))
        items = cur.fetchall()
        for it in items:
            print(f"   - {int(it['tp_productKey']):5d} {it['p_name']:<20} x{int(it['tp_quantity'])} "
                  f"@ ${float(it['p_price']):.2f}")

    conn.close()


# =========================
# 메인 루프
# =========================

def main():
    init_auth_schema()

    while True:
        print("""
=== UC Campus Store System ===
1. Login
2. Register
0. Exit
""")
        choice = input("Select an option: ").strip()

        if choice == "1":
            user = login()
            if user is None:
                continue
            if user["role"] == "admin":
                admin_menu(user)
            else:
                customer_menu(user)

        elif choice == "2":
            register_user()

        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
