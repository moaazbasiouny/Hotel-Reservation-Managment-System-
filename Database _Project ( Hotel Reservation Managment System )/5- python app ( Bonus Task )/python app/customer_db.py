import sqlite3

DB = "hotel.db"

def get_conn():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_customers():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT CustomerID, Name, NationalID, Email, Phone
    FROM Customer
    ORDER BY CustomerID DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def add_customer(name, national_id, email, phone):
    conn = get_conn()
    conn.execute("""
    INSERT INTO Customer(Name, NationalID, Email, Phone)
    VALUES (?, ?, ?, ?)
    """, (name, national_id, email, phone))
    conn.commit()
    conn.close()

def delete_customer(customer_id):
    conn = get_conn()
    conn.execute("""
    DELETE FROM Customer
    WHERE CustomerID=?
    """, (customer_id,))
    conn.commit()
    conn.close()

def customer_exists(national_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Customer WHERE NationalID=?", (national_id,))
    exists = cur.fetchone()[0] > 0
    conn.close()
    return exists