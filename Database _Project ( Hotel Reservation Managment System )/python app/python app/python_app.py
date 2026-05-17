# pyrefly: ignore [missing-import]
import customtkinter as ctk
import sqlite3
from datetime import datetime, date
import tkinter as tk
from tkinter import messagebox, ttk
import re
from tkcalendar import DateEntry
from customer_db import *

# ─── Theme ───────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ─── Colors ──────────────────────────────────────────────────────────────────
BG       = "#080f0b"
SIDEBAR  = "#0d1710"
SURFACE  = "#101e14"
CARD     = "#152a1b"
CARD_ALT = "#1c3322"
GREEN    = "#2d6a4f"
LGREEN   = "#40916c"
ACCENT   = "#74c69d"
TEXT     = "#e0f5e4"
TEXT_DIM = "#a3c9ad"
MUTED    = "#5e856a"
DANGER   = "#c1292e"
DANGER_H = "#e63946"
GOLD     = "#e6b44c"
INFO     = "#5eaed4"
WHITE    = "#ffffff"
SUCCESS  = "#52b788"

# ─── Database Initialization ─────────────────────────────────────────────────
DB = "hotel.db"

def get_conn():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS Customer (
        CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Email TEXT,
        Phone TEXT,
        image TEXT
    );
    CREATE TABLE IF NOT EXISTS Room (
        RoomID INTEGER PRIMARY KEY AUTOINCREMENT,
        Type TEXT NOT NULL,
        Price REAL NOT NULL,
        Status TEXT DEFAULT 'Available',
        Room_image TEXT
    );
    CREATE TABLE IF NOT EXISTS Staff (
        StaffID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Role TEXT,
        Phone TEXT,
        Salary REAL
    );
    CREATE TABLE IF NOT EXISTS Reservation (
        ReservationID INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerID INTEGER,
        RoomID INTEGER,
        StaffID INTEGER,
        CheckInDate TEXT,
        CheckOutDate TEXT,
        Status TEXT DEFAULT 'Confirmed',
        FOREIGN KEY(CustomerID) REFERENCES Customer(CustomerID),
        FOREIGN KEY(RoomID) REFERENCES Room(RoomID),
        FOREIGN KEY(StaffID) REFERENCES Staff(StaffID)
    );
    CREATE TABLE IF NOT EXISTS Payment (
        PaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
        ReservationID INTEGER,
        Amount REAL,
        Method TEXT,
        PaymentDate TEXT,
        Status TEXT DEFAULT 'Paid',
        FOREIGN KEY(ReservationID) REFERENCES Reservation(ReservationID)
    );
    """)
    
    # Add NationalID column safely
    c.execute("PRAGMA table_info(Customer)")
    columns = [col[1] for col in c.fetchall()]
    if 'NationalID' not in columns:
        c.execute("ALTER TABLE Customer ADD COLUMN NationalID TEXT")
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_customer_nationalid ON Customer(NationalID)")

    # Seed demo data
    c.execute("SELECT COUNT(*) FROM Room")
    if c.fetchone()[0] == 0:
        rooms = [
            ("Single", 50.0, "Available"),
            ("Double", 90.0, "Available"),
            ("Suite",  200.0, "Available"),
            ("Deluxe", 150.0, "Occupied"),
            ("Twin",   80.0,  "Available"),
        ]
        c.executemany("INSERT INTO Room(Type,Price,Status) VALUES(?,?,?)", rooms)

    c.execute("SELECT COUNT(*) FROM Customer")
    if c.fetchone()[0] == 0:
        customers = [
            ("Ahmed Ali", "30201012345678", "ahmed@mail.com", "0100000001"),
            ("Sara Mostafa", "30201012345679", "sara@mail.com", "0100000002"),
            ("Mohamed Hassan", "30201012345680", "moh@mail.com", "0100000003"),
        ]
        c.executemany("INSERT INTO Customer(Name,NationalID,Email,Phone) VALUES(?,?,?,?)", customers)

    c.execute("SELECT COUNT(*) FROM Staff")
    if c.fetchone()[0] == 0:
        staff = [
            ("Khaled Nour", "Manager", "0111111111", 8000),
            ("Dina Samir",  "Receptionist", "0122222222", 4000),
        ]
        c.executemany("INSERT INTO Staff(Name,Role,Phone,Salary) VALUES(?,?,?,?)", staff)

    conn.commit()
    conn.close()

# ─── Helpers ─────────────────────────────────────────────────────────────────
FONT = "Segoe UI"

def label(parent, text, size=13, color=TEXT, bold=False, anchor="w"):
    weight = "bold" if bold else "normal"
    return ctk.CTkLabel(parent, text=text, font=(FONT, size, weight), text_color=color, anchor=anchor)

def section_header(parent, icon, title, subtitle=""):
    hdr = ctk.CTkFrame(parent, fg_color="transparent")
    hdr.pack(fill="x", padx=32, pady=(24, 0))
    ctk.CTkFrame(hdr, height=3, width=48, fg_color=ACCENT, corner_radius=2).pack(anchor="w", pady=(0, 6))
    label(hdr, f"{icon}  {title}", 24, TEXT, bold=True).pack(anchor="w")
    if subtitle:
        label(hdr, subtitle, 12, MUTED).pack(anchor="w", pady=(2, 0))
    return hdr

def entry(parent, placeholder="", width=220):
    return ctk.CTkEntry(parent, placeholder_text=placeholder, width=width,
                        fg_color=SURFACE, border_color=GREEN, text_color=TEXT,
                        placeholder_text_color=MUTED, border_width=1, corner_radius=10, height=38, font=(FONT, 12))

def dropdown(parent, values, variable, width=160, command=None):
    return ctk.CTkOptionMenu(parent, values=values, variable=variable,
                             fg_color=GREEN, button_color=LGREEN, dropdown_fg_color=CARD, dropdown_hover_color=LGREEN,
                             dropdown_text_color=TEXT, font=(FONT, 12), dropdown_font=(FONT, 11),
                             corner_radius=10, width=width, height=36, command=command)

def btn(parent, text, cmd=None, color=GREEN, width=140, size=12):
    hover = LGREEN if color == GREEN else DANGER_H
    return ctk.CTkButton(parent, text=text, command=cmd, fg_color=color, hover_color=hover,
                         font=(FONT, size, "bold"), corner_radius=10, width=width, height=38)

def card(parent, **kwargs):
    return ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16, border_width=1, border_color=CARD_ALT, **kwargs)

def show_toast(parent, message, color=SUCCESS):
    toast = ctk.CTkLabel(parent, text=f"  ✓  {message}  ", font=(FONT, 12, "bold"), fg_color=color, text_color=WHITE, corner_radius=18, height=36)
    toast.place(relx=0.5, rely=0.02, anchor="n")
    parent.after(2500, toast.destroy)

def make_table(parent, columns, rows, col_widths=None):
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Hotel.Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, rowheight=44, font=(FONT, 11), borderwidth=0)
    style.configure("Hotel.Treeview.Heading", background="#1f4a36", foreground=WHITE, font=(FONT, 12, "bold"), relief="flat", padding=(10, 10))
    style.map("Hotel.Treeview", background=[("selected", LGREEN)], foreground=[("selected", WHITE)])

    frame = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=14, border_width=1, border_color=CARD_ALT)
    frame.pack(fill="both", expand=True, padx=12, pady=(12, 16))

    tree = ttk.Treeview(frame, columns=columns, show="headings", style="Hotel.Treeview")
    for i, col in enumerate(columns):
        w = col_widths[i] if col_widths else 130
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")

    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)
    sb.pack(side="right", fill="y", padx=(0, 4), pady=4)

    tree.tag_configure("odd", background="#182c1e")
    tree.tag_configure("even", background=CARD)
    tree.tag_configure("hover", background="#21402c")
    
    for i, row in enumerate(rows):
        tag = "odd" if i % 2 else "even"
        tree.insert("", "end", values=row, tags=(tag,))
        
    prev_hover = [None]
    def on_hover(event):
        item = tree.identify_row(event.y)
        if item == prev_hover[0]: return
        if prev_hover[0]:
            try:
                tags = list(tree.item(prev_hover[0], "tags"))
                if "hover" in tags: tags.remove("hover")
                tree.item(prev_hover[0], tags=tags)
            except tk.TclError: pass
        if item:
            tags = list(tree.item(item, "tags"))
            if "hover" not in tags: tags.append("hover")
            tree.item(item, tags=tags)
        prev_hover[0] = item

    def on_leave(event):
        if prev_hover[0]:
            try:
                tags = list(tree.item(prev_hover[0], "tags"))
                if "hover" in tags: tags.remove("hover")
                tree.item(prev_hover[0], tags=tags)
            except tk.TclError: pass
        prev_hover[0] = None

    tree.bind("<Motion>", on_hover)
    tree.bind("<Leave>", on_leave)
    return tree

# ─── Pages ───────────────────────────────────────────────────────────────────

class Dashboard(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.build()

    def build(self):
        section_header(self, "🏨", "Hotel Dashboard", f"Welcome back — {date.today().strftime('%A, %d %B %Y')}")

        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=28, pady=(20, 12))

        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM Customer"); custs = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM Room"); rooms = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM Room WHERE Status='Available'"); avail = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM Reservation WHERE Status='Confirmed'"); res = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(Amount),0) FROM Payment"); rev = c.fetchone()[0]
        conn.close()

        stats = [
            ("👥  Customers", custs, ACCENT),
            ("🛏  Total Rooms", rooms, GOLD),
            ("✅  Available", avail, SUCCESS),
            ("📋  Reservations", res, INFO),
            ("💰  Revenue", f"${rev:,.0f}", "#f4a261"),
        ]
        for title, val, col in stats:
            c_frame = card(stats_row, width=180, height=130)
            c_frame.pack(side="left", expand=True, fill="x", padx=8, pady=4)
            c_frame.pack_propagate(False)
            
            def make_hover(f, c):
                def on_enter(e): f.configure(border_color=c)
                def on_leave(e): f.configure(border_color=CARD_ALT)
                for w in [f] + f.winfo_children():
                    w.bind("<Enter>", on_enter)
                    w.bind("<Leave>", on_leave)
            
            bar = ctk.CTkFrame(c_frame, height=5, fg_color=col, corner_radius=2)
            bar.pack(fill="x", padx=16, pady=(12,0))
            l1 = label(c_frame, str(val), 36, col, bold=True, anchor="center")
            l1.pack(expand=True)
            l2 = label(c_frame, title, 12, TEXT_DIM, anchor="center")
            l2.pack(pady=(0, 14))
            
            make_hover(c_frame, col)

        ctk.CTkFrame(self, height=1, fg_color=CARD_ALT).pack(fill="x", padx=32, pady=(8, 0))
        label(self, "📋  Recent Reservations", 15, TEXT, bold=True).pack(anchor="w", padx=34, pady=(12,0))
        conn = get_conn(); c = conn.cursor()
        c.execute("""
            SELECT r.ReservationID, cu.Name, ro.Type || ' Room', r.CheckInDate, r.CheckOutDate, r.Status
            FROM Reservation r
            JOIN Customer cu ON r.CustomerID=cu.CustomerID
            JOIN Room ro ON r.RoomID=ro.RoomID
            ORDER BY r.ReservationID DESC LIMIT 8
        """)
        rows = c.fetchall(); conn.close()
        cols = ("Res ID", "Customer", "Room Type", "Check-In", "Check-Out", "Status")
        make_table(self, cols, rows, [60,180,140,110,110,100])


class CustomersPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.build()

    def build(self):
        section_header(self, "👥", "Customers", "Manage hotel guests and contacts")
        f = card(self)
        f.pack(fill="x", padx=30, pady=(10, 20))

        row1 = ctk.CTkFrame(f, fg_color=CARD)
        row1.pack(expand=True, pady=16)

        self.e_name = entry(row1, "Full Name", width=180)
        self.e_name.pack(side="left", padx=10)

        self.e_nid = entry(row1, "National ID", width=160)
        self.e_nid.pack(side="left", padx=10)

        self.e_email = entry(row1, "Email", width=180)
        self.e_email.pack(side="left", padx=10)

        self.e_phone = entry(row1, "Phone", width=140)
        self.e_phone.pack(side="left", padx=10)

        btn(row1, "➕ Add", self.add, width=120).pack(side="left", padx=10)
        btn(row1, "🗑 Delete", self.delete, color=DANGER, width=120).pack(side="left", padx=10)

        self.load_table()

    def load_table(self):
        if hasattr(self, "_tframe"):
            self._tframe.destroy()
        self._tframe = ctk.CTkFrame(self, fg_color=BG)
        self._tframe.pack(fill="both", expand=True, padx=20)
        rows = get_customers()
        self.tree = make_table(self._tframe, ("Customer ID", "Name", "National ID", "Email", "Phone"), rows, [80, 180, 140, 180, 120])

    def add(self):
        n = self.e_name.get().strip()
        nid = self.e_nid.get().strip()
        e = self.e_email.get().strip()
        p = self.e_phone.get().strip()

        if not n:
            messagebox.showwarning("Missing", "Name is required.")
            return
        if not re.match(r"^[A-Za-z\s]+$", n):
            messagebox.showerror("Invalid Name", "Name must contain letters and spaces only.")
            return
        if not nid or not nid.isdigit() or len(nid) != 14:
            messagebox.showerror("Invalid National ID", "National ID must be exactly 14 digits.")
            return
        if not e:
            messagebox.showerror("Missing", "Email is required.")
            return
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', e):
            messagebox.showerror("Invalid Email", "Please enter a valid email.")
            return
        if p and (not p.isdigit() or len(p) < 11):
            messagebox.showerror("Invalid Phone", "Phone must be at least 11 digits.")
            return

        try:
            if customer_exists(nid):
                messagebox.showerror("Duplicate", "This National ID is already registered.")
                return
            add_customer(n, nid, e, p)
            for entry_field in [self.e_name, self.e_nid, self.e_email, self.e_phone]:
                entry_field.delete(0, "end")
            self.load_table()
            show_toast(self, "Customer added successfully")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def delete(self):
        sel = self.tree.selection()
        if not sel: return
        cid = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete", f"Delete customer #{cid}? This will also delete all related reservations and payments."):
            try:
                delete_customer(cid)
                show_toast(self, "Customer and related records deleted", DANGER)
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to delete customer: {str(ex)}")
        self.load_table()


class RoomsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.build()

    def build(self):
        section_header(self, "🛏", "Rooms", "Manage room pricing and statuses")
        f = card(self); f.pack(fill="x", padx=30, pady=(10, 20))
        row = ctk.CTkFrame(f, fg_color=CARD); row.pack(expand=True, pady=16)

        self.type_var = ctk.StringVar(value="Single")
        dropdown(row, ["Single", "Double", "Suite", "Deluxe", "Twin"], self.type_var, width=140).pack(side="left", padx=10)

        self.e_price = entry(row, "Price per Night", width=140); self.e_price.pack(side="left", padx=10)

        self.status_var = ctk.StringVar(value="Available")
        dropdown(row, ["Available", "Occupied", "Maintenance"], self.status_var, width=140).pack(side="left", padx=10)

        btn(row, "➕ Add Room", self.add, width=130).pack(side="left", padx=10)
        btn(row, "🗑 Delete", self.delete, color=DANGER, width=110).pack(side="left", padx=10)
        self.load_table()

    def load_table(self):
        if hasattr(self, "_tframe"): self._tframe.destroy()
        self._tframe = ctk.CTkFrame(self, fg_color=BG); self._tframe.pack(fill="both", expand=True, padx=20)
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT RoomID, Type, Price, Status FROM Room ORDER BY RoomID DESC")
        rows = c.fetchall(); conn.close()
        self.tree = make_table(self._tframe, ("Room ID", "Type", "Price", "Status"), rows, [100, 200, 150, 150])

    def add(self):
        t, p, s = self.type_var.get(), self.e_price.get().strip(), self.status_var.get()
        if not p: messagebox.showwarning("Missing", "Price is required."); return
        try: p = float(p)
        except: messagebox.showerror("Error", "Price must be a number."); return
        conn = get_conn()
        conn.execute("INSERT INTO Room(Type, Price, Status) VALUES(?,?,?)", (t, p, s))
        conn.commit(); conn.close()
        self.e_price.delete(0, "end")
        self.load_table()
        show_toast(self, "Room added successfully")

    def delete(self):
        sel = self.tree.selection()
        if not sel: return
        rid = self.tree.item(sel[0])["values"][0]
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM Reservation WHERE RoomID=? AND Status='Confirmed'", (rid,))
        if c.fetchone()[0] > 0:
            conn.close(); messagebox.showwarning("Error", "Cannot delete an actively reserved room."); return
        if messagebox.askyesno("Delete", f"Delete room #{rid}?"):
            conn.execute("DELETE FROM Room WHERE RoomID=?", (rid,))
            conn.commit(); show_toast(self, "Room deleted", DANGER)
        conn.close(); self.load_table()


class ReservationsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.build()

    def build(self):
        section_header(self, "📋", "Reservations", "Book and manage guest stays")
        f = card(self); f.pack(fill="x", padx=30, pady=(10, 20))
        row = ctk.CTkFrame(f, fg_color=CARD); row.pack(expand=True, pady=16)

        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT CustomerID, Name FROM Customer")
        self.cust_map = {f"{r[1]} (#{r[0]})": r[0] for r in c.fetchall()}
        c.execute("SELECT RoomID, Type || ' ($' || Price || ')' FROM Room WHERE Status='Available'")
        self.room_map = {r[1]: r[0] for r in c.fetchall()}
        c.execute("SELECT StaffID, Name FROM Staff")
        self.staff_map = {f"{r[1]} (#{r[0]})": r[0] for r in c.fetchall()}
        conn.close()

        cust_opts = list(self.cust_map.keys()) or ["No customers"]
        room_opts = list(self.room_map.keys()) or ["No available rooms"]
        staff_opts = list(self.staff_map.keys()) or ["No staff"]

        self.cust_var = ctk.StringVar(value=cust_opts[0])
        self.room_var = ctk.StringVar(value=room_opts[0])
        self.staff_var = ctk.StringVar(value=staff_opts[0])

        dropdown(row, cust_opts, self.cust_var, width=150).pack(side="left", padx=6)
        dropdown(row, room_opts, self.room_var, width=140).pack(side="left", padx=6)
        dropdown(row, staff_opts, self.staff_var, width=120).pack(side="left", padx=6)

        label(row, "In:", 12, MUTED).pack(side="left", padx=2)
        self.de_cin = DateEntry(row, width=11, background=GREEN, foreground=WHITE, date_pattern='yyyy-mm-dd')
        self.de_cin.pack(side="left", padx=6)

        label(row, "Out:", 12, MUTED).pack(side="left", padx=2)
        self.de_cout = DateEntry(row, width=11, background=GREEN, foreground=WHITE, date_pattern='yyyy-mm-dd')
        self.de_cout.pack(side="left", padx=6)

        btn(row, "➕ Book", self.add, width=100).pack(side="left", padx=6)
        btn(row, "❌ Cancel", self.cancel, color=DANGER, width=100).pack(side="left", padx=6)
        self.load_table()

    def load_table(self):
        if hasattr(self, "_tframe"): self._tframe.destroy()
        self._tframe = ctk.CTkFrame(self, fg_color=BG); self._tframe.pack(fill="both", expand=True, padx=20)
        conn = get_conn(); c = conn.cursor()
        c.execute("""
            SELECT r.ReservationID, cu.Name, ro.Type || ' Room', COALESCE(s.Name, 'None'), r.CheckInDate, r.CheckOutDate, r.Status
            FROM Reservation r
            JOIN Customer cu ON r.CustomerID=cu.CustomerID
            JOIN Room ro ON r.RoomID=ro.RoomID
            LEFT JOIN Staff s ON r.StaffID=s.StaffID
            ORDER BY r.ReservationID DESC
        """)
        rows = c.fetchall(); conn.close()
        self.tree = make_table(self._tframe, ("Res ID","Customer","Room","Staff","Check-In","Check-Out","Status"), rows, [60,180,140,140,110,110,100])

    def add(self):
        try:
            d_in, d_out = self.de_cin.get_date(), self.de_cout.get_date()
        except ValueError:
            messagebox.showwarning("Missing", "Please select valid check-in and check-out dates."); return
        if d_out <= d_in:
            messagebox.showwarning("Invalid", "Check-out must be after check-in."); return
        
        cin, cout = d_in.isoformat(), d_out.isoformat()
        cid, rid, stid = self.cust_map.get(self.cust_var.get()), self.room_map.get(self.room_var.get()), self.staff_map.get(self.staff_var.get())
        if not cid or not rid:
            messagebox.showwarning("Error","Select valid customer and room."); return
            
        conn = get_conn(); c = conn.cursor()
        c.execute("""SELECT COUNT(*) FROM Reservation WHERE RoomID=? AND Status='Confirmed' AND (CheckInDate < ? AND CheckOutDate > ?)""", (rid, cout, cin))
        if c.fetchone()[0] > 0:
            conn.close(); messagebox.showerror("Error", "Room is already booked for these dates."); return


        conn.execute("""INSERT INTO Reservation(CustomerID, RoomID, StaffID, CheckInDate, CheckOutDate)
                        VALUES(?,?,?,?,?)""", (cid, rid, stid, cin, cout))
        
   
        today = date.today().isoformat()
        if cin <= today <= cout:
            conn.execute("UPDATE Room SET Status='Occupied' WHERE RoomID=?", (rid,))
            
        conn.commit(); conn.close()
        self.load_table()
        show_toast(self, "Reservation booked successfully")

    def cancel(self):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])["values"]
        rid_res, status = vals[0], vals[6]
        if status == "Cancelled":
            messagebox.showinfo("Info", "This reservation is already cancelled."); return
        if messagebox.askyesno("Cancel","Cancel this reservation?"):
            conn = get_conn(); c = conn.cursor()
            c.execute("SELECT RoomID FROM Reservation WHERE ReservationID=?",(rid_res,))
            room = c.fetchone()
            conn.execute("UPDATE Reservation SET Status='Cancelled' WHERE ReservationID=?",(rid_res,))
            if room:
                room_id = room[0]
                today = date.today().isoformat()
                c.execute("""SELECT COUNT(*) FROM Reservation WHERE RoomID=? AND Status='Confirmed' AND CheckInDate <= ? AND CheckOutDate >= ?""", (room_id, today, today))
                if c.fetchone()[0] == 0:
                    conn.execute("UPDATE Room SET Status='Available' WHERE RoomID=?",(room_id,))
            conn.commit(); conn.close()
            self.load_table()
            show_toast(self, "Reservation cancelled", GOLD)


class PaymentsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.build()

    def build(self):
        section_header(self, "💰", "Payments", "Track and record transactions")
        f = card(self); f.pack(fill="x", padx=30, pady=(10, 20))
        row = ctk.CTkFrame(f, fg_color=CARD); row.pack(expand=True, pady=16)

        conn = get_conn(); c = conn.cursor()
        c.execute("""SELECT r.ReservationID, cu.Name, ro.Type, ro.Price, r.CheckInDate, r.CheckOutDate 
                     FROM Reservation r
                     JOIN Customer cu ON r.CustomerID=cu.CustomerID
                     JOIN Room ro ON r.RoomID=ro.RoomID
                     WHERE r.Status='Confirmed'""")
        res = c.fetchall(); conn.close()

        self.res_map = {f"{r[1]} ({r[2]} Room)": (r[0], r[3], r[4], r[5]) for r in res}
        res_opts = list(self.res_map.keys()) or ["No active reservations"]
        self.res_var = ctk.StringVar(value=res_opts[0])

        label(row,"Reservation:",12,MUTED).pack(side="left",padx=(12,2))
        dropdown(row, res_opts, self.res_var, width=260, command=self.update_amount).pack(side="left",padx=8)

        self.e_amount = entry(row,"Amount",width=140); self.e_amount.pack(side="left",padx=8)

        self.method_var = ctk.StringVar(value="Cash")
        dropdown(row, ["Cash","Card","Online Transfer"], self.method_var, width=180).pack(side="left",padx=8)

        btn(row,"➕ Record Payment",self.add,width=180).pack(side="left",padx=(16,8))
        self.update_amount(self.res_var.get())
        self.load_table()

    def update_amount(self, choice):
        if choice not in self.res_map: return
        _, price, cin, cout = self.res_map[choice]
        d_in = datetime.strptime(cin, "%Y-%m-%d").date()
        d_out = datetime.strptime(cout, "%Y-%m-%d").date()
        nights = max(1, (d_out - d_in).days)
        total = nights * price
        self.e_amount.delete(0, "end")
        self.e_amount.insert(0, f"{total:.2f}")

    def load_table(self):
        if hasattr(self, "_tframe"): self._tframe.destroy()
        self._tframe = ctk.CTkFrame(self, fg_color=BG); self._tframe.pack(fill="both", expand=True, padx=20)
        conn = get_conn(); c = conn.cursor()
        c.execute("""
            SELECT p.PaymentID, cu.Name, p.Amount, p.Method, p.PaymentDate, p.Status
            FROM Payment p
            JOIN Reservation r ON p.ReservationID=r.ReservationID
            JOIN Customer cu ON r.CustomerID=cu.CustomerID
            ORDER BY p.PaymentID DESC
        """)
        rows = c.fetchall(); conn.close()
        self.tree = make_table(self._tframe, ("Payment ID","Reservation","Amount","Method","Date","Status"), rows,[80,220,100,130,130,100])

    def add(self):
        choice = self.res_var.get()
        if choice not in self.res_map:
            messagebox.showwarning("Missing","Select reservation and enter amount."); return
        rid = self.res_map[choice][0]
        amt = self.e_amount.get()
        if not amt: messagebox.showwarning("Missing","Enter amount."); return
        try: amt = float(amt)
        except: messagebox.showerror("Error","Amount must be a number."); return
        if amt <= 0: messagebox.showwarning("Invalid","Amount must be greater than zero."); return
        
        conn = get_conn()
        conn.execute("""INSERT INTO Payment(ReservationID,Amount,Method,PaymentDate,Status) VALUES(?,?,?,?,'Paid')""",
                     (rid, amt, self.method_var.get(), date.today().isoformat()))
        conn.commit(); conn.close()
        self.e_amount.delete(0,"end")
        self.load_table()
        show_toast(self, "Payment recorded successfully")


class StaffPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.build()

    def build(self):
        section_header(self, "👔", "Staff", "Manage employees and roles")
        f = card(self); f.pack(fill="x", padx=30, pady=(10, 20))
        row = ctk.CTkFrame(f, fg_color=CARD); row.pack(expand=True, pady=16)

        self.e_name   = entry(row,"Full Name",width=200); self.e_name.pack(side="left",padx=10)
        self.e_role   = entry(row,"Role",width=160); self.e_role.pack(side="left",padx=10)
        self.e_phone  = entry(row,"Phone",width=160); self.e_phone.pack(side="left",padx=10)
        self.e_salary = entry(row,"Salary",width=140); self.e_salary.pack(side="left",padx=10)
        btn(row,"➕ Add",self.add,width=130).pack(side="left",padx=10)
        btn(row,"🗑 Delete",self.delete,color=DANGER,width=130).pack(side="left",padx=10)
        self.load_table()

    def load_table(self):
        if hasattr(self, "_tframe"): self._tframe.destroy()
        self._tframe = ctk.CTkFrame(self, fg_color=BG); self._tframe.pack(fill="both", expand=True, padx=20)
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT StaffID,Name,Role,Phone,Salary FROM Staff ORDER BY StaffID DESC")
        rows = c.fetchall(); conn.close()
        self.tree = make_table(self._tframe, ("Staff ID","Name","Role","Phone","Salary"), rows,[80,200,150,150,100])

    def add(self):
        n,r,p,s = self.e_name.get().strip(), self.e_role.get(), self.e_phone.get(), self.e_salary.get()
        if not n: messagebox.showwarning("Missing","Name is required."); return
        if not re.match(r"^[A-Za-z\s]+$", n):
            messagebox.showerror("Invalid Name", "Name must contain letters and spaces only."); return
        try: s = float(s) if s else 0
        except: messagebox.showerror("Error","Salary must be a number."); return
        
        conn = get_conn()
        conn.execute("INSERT INTO Staff(Name,Role,Phone,Salary) VALUES(?,?,?,?)",(n,r,p,s))
        conn.commit(); conn.close()
        for e in [self.e_name,self.e_role,self.e_phone,self.e_salary]: e.delete(0,"end")
        self.load_table()
        show_toast(self, "Staff member added")

    def delete(self):
        sel = self.tree.selection()
        if not sel: return
        sid = self.tree.item(sel[0])["values"][0]
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM Reservation WHERE StaffID=? AND Status='Confirmed'", (sid,))
        if c.fetchone()[0] > 0:
            conn.close(); messagebox.showwarning("Error", "Cannot delete staff assigned to active reservations."); return
        if messagebox.askyesno("Delete",f"Delete staff #{sid}?"):
            conn.execute("DELETE FROM Staff WHERE StaffID=?",(sid,))
            conn.commit(); show_toast(self, "Staff deleted", DANGER)
        conn.close(); self.load_table()


# ─── Main App ─────────────────────────────────────────────────────────────────
class HotelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🏨  Grand Hotel — Management System")
        self.geometry("1280x780")
        self.minsize(1150, 700)
        self.configure(fg_color=BG)

        init_db()
        self._active_btn = None
        self._build_ui()
        self._show("Dashboard")

    def _build_ui(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR, width=250, corner_radius=0, border_width=1, border_color=CARD_ALT)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_f = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_f.pack(fill="x", pady=(26, 6), padx=20)
        ctk.CTkLabel(logo_f, text="🏨", font=(FONT, 44)).pack()
        ctk.CTkLabel(logo_f, text="Grand Hotel", font=(FONT, 18, "bold"), text_color=ACCENT).pack(pady=(6, 0))
        ctk.CTkLabel(logo_f, text="Management System", font=(FONT, 10), text_color=MUTED).pack(pady=(0, 4))

        ctk.CTkFrame(self.sidebar, height=1, fg_color=CARD_ALT).pack(fill="x", padx=20, pady=(8, 12))
        label(self.sidebar, "    MENU", 10, MUTED, bold=True).pack(anchor="w", padx=16, pady=(0, 6))

        nav = [
            ("🏠  Dashboard",   "Dashboard"),
            ("👥  Customers",   "Customers"),
            ("🛏  Rooms",       "Rooms"),
            ("📋  Reservations","Reservations"),
            ("💰  Payments",    "Payments"),
            ("👔  Staff",       "Staff"),
        ]
        self._nav_btns = {}
        for label_txt, page in nav:
            b = ctk.CTkButton(self.sidebar, text=label_txt, command=lambda p=page: self._show(p),
                              fg_color="transparent", hover_color=SURFACE, text_color=TEXT_DIM,
                              font=(FONT, 13), anchor="w", corner_radius=10, height=46)
            b.pack(fill="x", padx=14, pady=2)
            self._nav_btns[page] = b

        ctk.CTkFrame(self.sidebar, height=1, fg_color=CARD_ALT).pack(fill="x", padx=20, pady=8, side="bottom")
        foot = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        foot.pack(side="bottom", pady=(0, 14))
        ctk.CTkLabel(foot, text="Innovation University", font=(FONT, 10), text_color=MUTED).pack()
        ctk.CTkLabel(foot, text="v2.0  •  2026", font=(FONT, 9), text_color=MUTED).pack(pady=(2, 0))

        self.content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)

    def _show(self, page):
        if self._active_btn:
            self._active_btn.configure(fg_color="transparent", text_color=TEXT_DIM)
        self._active_btn = self._nav_btns[page]
        self._active_btn.configure(fg_color=GREEN, text_color=WHITE)

        for w in self.content.winfo_children(): w.destroy()

        pages = {
            "Dashboard":  Dashboard,
            "Customers":  CustomersPage,
            "Rooms":      RoomsPage,
            "Reservations": ReservationsPage,
            "Payments":   PaymentsPage,
            "Staff":      StaffPage,
        }
        pages[page](self.content).pack(fill="both", expand=True)

if __name__ == "__main__":
    app = HotelApp()
    app.mainloop()