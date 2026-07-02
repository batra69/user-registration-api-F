-- Run this once in MySQL to create the database and table
CREATE DATABASE IF NOT EXISTS registration_db;
USE registration_db;

CREATE TABLE IF NOT EXISTS employees (
    reg_no      INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(25) NOT NULL,
    gender      ENUM('Male', 'Female') NOT NULL,
    dob         DATE NOT NULL,
    email       VARCHAR(100),
    mobile      VARCHAR(15),
    phone       VARCHAR(15),
    state       VARCHAR(50) NOT NULL,
    city        VARCHAR(50),
    hobbies     VARCHAR(100),
    photo       VARCHAR(255),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);