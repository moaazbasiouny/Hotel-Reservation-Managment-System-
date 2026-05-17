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

def reset_customer_ids():
    """Reset Customer ID sequence when table is empty"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM Customer")
    if c.fetchone()[0] == 0:
        c.execute("DELETE FROM sqlite_sequence WHERE name='Customer'")
        conn.commit()
    conn.close()

def delete_customer(customer_id):
    conn = get_conn()
    try:
        # Delete payments associated with customer's reservations
        conn.execute("""
        DELETE FROM Payment
        WHERE ReservationID IN (
            SELECT ReservationID FROM Reservation WHERE CustomerID=?
        )
        """, (customer_id,))
        
        # Delete reservations associated with customer
        conn.execute("""
        DELETE FROM Reservation
        WHERE CustomerID=?
        """, (customer_id,))
        
        # Delete the customer
        conn.execute("""
        DELETE FROM Customer
        WHERE CustomerID=?
        """, (customer_id,))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
    
    # Reset ID sequence if no customers remain
    reset_customer_ids()

def customer_exists(national_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Customer WHERE NationalID=?", (national_id,))
    exists = cur.fetchone()[0] > 0
    conn.close()
    return exists

def customer_has_reservations(customer_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Reservation WHERE CustomerID=? AND Status='Confirmed'", (customer_id,))
    has_reservations = cur.fetchone()[0] > 0
    conn.close()
    return has_reservations