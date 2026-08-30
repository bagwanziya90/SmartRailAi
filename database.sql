CREATE DATABASE smartrail;
USE smartrail;

CREATE TABLE passengers (
    passenger_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(10),
    phone VARCHAR(15)
);

CREATE TABLE trains (
    train_id INT AUTO_INCREMENT PRIMARY KEY,
    train_name VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    departure_time TIME,
    arrival_time TIME
);

CREATE TABLE train_classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT,
    class_name VARCHAR(20),
    fare DECIMAL(10,2),
    total_seats INT,
    available_seats INT,
    FOREIGN KEY (train_id) REFERENCES trains(train_id)
);

CREATE TABLE reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    passenger_id INT,
    train_id INT,
    class_id INT,
    journey_date DATE,
    seat_no VARCHAR(10),
    status VARCHAR(20),
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
    FOREIGN KEY (train_id) REFERENCES trains(train_id),
    FOREIGN KEY (class_id) REFERENCES train_classes(class_id)
);

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT,
    amount DECIMAL(10,2),
    payment_mode VARCHAR(20),
    payment_status VARCHAR(20),

    FOREIGN KEY (reservation_id)
    REFERENCES reservations(reservation_id)
);

INSERT INTO trains
(train_name, source, destination, departure_time, arrival_time)
VALUES
('Deccan Queen', 'Pune', 'Mumbai', '07:15:00', '10:25:00'),
('Sinhagad Express', 'Pune', 'Mumbai', '06:05:00', '09:55:00'),
('Intercity Express', 'Pune', 'Mumbai', '17:55:00', '21:20:00'),
('Pragati Express', 'Pune', 'Mumbai', '16:30:00', '20:05:00');

INSERT INTO train_classes
(train_id, class_name, fare, total_seats, available_seats)
VALUES
(1, 'CC', 450, 100, 40),
(1, '2S', 180, 200, 120),
(2, 'CC', 400, 100, 25),
(2, '2S', 160, 200, 80),
(3, 'CC', 500, 100, 70),
(3, '2S', 200, 200, 150),
(4, 'CC', 480, 100, 15),
(4, '2S', 190, 200, 60);
