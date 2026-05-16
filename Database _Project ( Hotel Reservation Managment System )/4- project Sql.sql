CREATE DATABASE Hotel_Reservation_System;
USE Hotel_Reservation_System;

------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE Customer
(
NationalID BIGINT PRIMARY KEY,
CustomerID INT UNIQUE NOT NULL,
Name VARCHAR(50) NOT NULL,
Email VARCHAR(100) UNIQUE NOT NULL,
Phone VARCHAR(15) NOT NULL
);

------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE Staff
(
StaffID INT PRIMARY KEY,
Name VARCHAR(50) NOT NULL,
Role VARCHAR(50) NOT NULL,
Phone VARCHAR(15) UNIQUE NOT NULL,
Salary DECIMAL(10,2) CHECK (Salary > 0)
);

------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE Room
(
RoomID INT PRIMARY KEY,
Type VARCHAR(30) NOT NULL,
Price DECIMAL(10,2) CHECK (Price > 0),
Status VARCHAR(20) CHECK (Status IN('Available','Pending','Booked'))
);

------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE Reservation
(
ReservationID INT PRIMARY KEY,
Status VARCHAR(20) NOT NULL,
CheckInDate DATETIME NOT NULL,
CheckOutDate DATETIME NOT NULL,
StaffID INT NOT NULL,
RoomID INT NOT NULL,
NationalID BIGINT NOT NULL,
CHECK (CheckOutDate > CheckInDate),
FOREIGN KEY (StaffID) REFERENCES Staff(StaffID),
FOREIGN KEY (RoomID) REFERENCES Room(RoomID),
FOREIGN KEY (NationalID) REFERENCES Customer(NationalID)
);

------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE Payment
(
PaymentID INT PRIMARY KEY,
Amount DECIMAL(10,2) CHECK (Amount > 0),
PaymentDate DATETIME DEFAULT GETDATE(),
Method VARCHAR(30) NOT NULL,
NationalID BIGINT NOT NULL,
FOREIGN KEY (NationalID) REFERENCES Customer(NationalID)
);

------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE FamilyMember
(
MemberID INT PRIMARY KEY,
Name VARCHAR(50) NOT NULL,
Age INT CHECK (Age > 0),
Relationship VARCHAR(30) NOT NULL
);

------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE Stays_In
(
ReservationID INT,
RoomID INT,
MemberID INT,
PRIMARY KEY (ReservationID,RoomID,MemberID),
FOREIGN KEY (ReservationID) REFERENCES Reservation(ReservationID),
FOREIGN KEY (RoomID) REFERENCES Room(RoomID),
FOREIGN KEY (MemberID) REFERENCES FamilyMember(MemberID)
);

------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE Room_Image
(
Image_No INT,
RoomID INT,
Image_URL VARCHAR(255) NOT NULL,
PRIMARY KEY (Image_No,RoomID),
FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
);

------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO Customer VALUES (30201010101010,1,'Mark Amir','mark@gmail.com','01011111111');
INSERT INTO Customer VALUES (30202020202020,2,'Moaz Ahmed','moaz@gmail.com','01022222222');

INSERT INTO Staff VALUES (1,'Mohamed','Receptionist','01111111111',7000);
INSERT INTO Staff VALUES (2,'Mostafa','Manager','01122222222',12000);

INSERT INTO Room VALUES (1,'Single',1200,'Available');
INSERT INTO Room VALUES (2,'Double',2200,'Pending');
INSERT INTO Room VALUES (3,'Suite',5000,'Booked');

INSERT INTO Reservation VALUES (1,'Confirmed','2026-05-20 14:30:45','2026-05-25 12:00:00',1,1,30201010101010);
INSERT INTO Reservation VALUES (2,'Pending','2026-05-21 15:00:00','2026-05-24 11:00:00',2,2,30202020202020);

INSERT INTO Payment VALUES (1,6000,GETDATE(),'Cash',30201010101010);
INSERT INTO Payment VALUES (2,2200,GETDATE(),'Visa',30202020202020);

INSERT INTO FamilyMember VALUES (1,'Youssef',15,'Son');
INSERT INTO FamilyMember VALUES (2,'Mariam',35,'Wife');

INSERT INTO Stays_In VALUES (1,1,1);
INSERT INTO Stays_In VALUES (1,1,2);

INSERT INTO Room_Image VALUES (1,1,'room1.jpg');
INSERT INTO Room_Image VALUES (2,2,'room2.jpg');

------------------------------------------------------------------------------------------------------------------------------------------------------------

UPDATE Room
SET Status='Booked'
WHERE RoomID=1;

------------------------------------------------------------------------------------------------------------------------------------------------------------

DELETE FROM Room_Image
WHERE Image_No=2;

------------------------------------------------------------------------------------------------------------------------------------------------------------

SELECT * FROM Customer;
SELECT * FROM Room;
SELECT * FROM Reservation;

------------------------------------------------------------------------------------------------------------------------------------------------------------

SELECT *
FROM Room
WHERE Price>1500;

------------------------------------------------------------------------------------------------------------------------------------------------------------

SELECT *
FROM Room
ORDER BY Price DESC;

------------------------------------------------------------------------------------------------------------------------------------------------------------

SELECT Status,COUNT(*) AS TotalRooms
FROM Room
GROUP BY Status
HAVING COUNT(*)>=1;

------------------------------------------------------------------------------------------------------------------------------------------------------------

SELECT Customer.Name,Room.Type,Reservation.CheckInDate,Reservation.CheckOutDate
FROM Reservation
INNER JOIN Customer
ON Reservation.NationalID=Customer.NationalID
INNER JOIN Room
ON Reservation.RoomID=Room.RoomID;

------------------------------------------------------------------------------------------------------------------------------------------------------------

SELECT MAX(Price) AS HighestPrice
FROM Room;

SELECT MIN(Price) AS LowestPrice
FROM Room;

SELECT AVG(Price) AS AveragePrice
FROM Room;

SELECT COUNT(*) AS TotalRooms
FROM Room;

------------------------------------------------------------------------------------------------------------------------------------------------------------

SELECT *
FROM Customer
WHERE Name LIKE 'M%';

------------------------------------------------------------------------------------------------------------------------------------------------------------

SELECT TOP 1 *
FROM Room
ORDER BY Price DESC;

------------------------------------------------------------------------------------------------------------------------------------------------------------

GO

DROP VIEW IF EXISTS ReservationDetails;

GO

CREATE VIEW ReservationDetails AS

SELECT Customer.Name,Room.Type,Reservation.CheckInDate,Reservation.CheckOutDate,Reservation.Status
FROM Reservation
INNER JOIN Customer
ON Reservation.NationalID=Customer.NationalID
INNER JOIN Room
ON Reservation.RoomID=Room.RoomID;

GO

------------------------------------------------------------------------------------------------------------------------------------------------------------

SELECT * FROM ReservationDetails;

GO

------------------------------------------------------------------------------------------------------------------------------------------------------------

DROP PROCEDURE IF EXISTS GetRooms;

GO

CREATE PROCEDURE GetRooms

AS
BEGIN
SELECT *
FROM Room;
END;

GO

EXEC GetRooms;