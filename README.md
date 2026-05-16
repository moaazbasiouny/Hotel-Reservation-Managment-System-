# 🏨 Hotel Reservation Management System

## 📌 Overview
The **Hotel Reservation Management System** is a database management project designed to simplify hotel operations such as room booking, customer management, and reservation tracking.

This project was developed as part of a **Database Systems course** to apply core database concepts including:

- Entity-Relationship Diagram (ERD) design
- Database normalization
- SQL queries and operations
- Relational schema modeling

---

## 🎯 Features

- 🛏️ Room management (add, update, delete rooms)
- 👤 Customer management
- 📅 Reservation handling
- 💳 Payment tracking
- 📊 Room availability status (Available / Booked / Maintenance)
- 🔍 Search functionality for customers and reservations

---

## 🗄️ Database Design

### 📐 ERD Structure
The database is designed based on the following relationships:

- Customer → Reservation (One-to-Many)
- Room → Reservation (One-to-Many)
- Reservation → Payment (One-to-One)

---

## 🧩 Tables Schema

### 1. Customers
- CustomerID (Primary Key)
- FullName
- Phone
- Email
- NationalID

### 2. Rooms
- RoomID (Primary Key)
- RoomNumber
- RoomType
- PricePerNight
- Status

### 3. Reservations
- ReservationID (Primary Key)
- CustomerID (Foreign Key)
- RoomID (Foreign Key)
- CheckInDate
- CheckOutDate
- TotalPrice

### 4. Payments
- PaymentID (Primary Key)
- ReservationID (Foreign Key)
- PaymentMethod
- PaymentDate
- Amount

---

## ⚙️ Technologies Used

- SQL (MySQL / SQLite / PostgreSQL)
- Database Design (ERD tools)
- Optional backend: Python / Java / C#

---

## 🚀 How to Run

1. Import the `.sql` database file into your DBMS
2. Execute the schema creation script
3. Insert sample data (optional)
4. Run SQL queries for testing

---

## 📂 Project Structure
