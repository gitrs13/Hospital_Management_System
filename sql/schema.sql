-- ============================================================
--  Hospital Management System  |  schema.sql
--  Compatible with MySQL 5.7 and 8.x
-- ============================================================

DROP DATABASE IF EXISTS hospital_db;
CREATE DATABASE hospital_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hospital_db;

-- ─────────────────────────────────────────────
--  1. USERS
-- ─────────────────────────────────────────────
CREATE TABLE users (
    user_id    INT          NOT NULL AUTO_INCREMENT,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(100) NOT NULL,
    role       ENUM('admin','staff') NOT NULL DEFAULT 'staff',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

-- ─────────────────────────────────────────────
--  2. DOCTORS
-- ─────────────────────────────────────────────
CREATE TABLE doctors (
    doctor_id      INT          NOT NULL AUTO_INCREMENT,
    name           VARCHAR(100) NOT NULL,
    age            INT          NOT NULL,
    gender         ENUM('Male','Female','Other') NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    phone          VARCHAR(15)  NOT NULL,
    email          VARCHAR(100),
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (doctor_id),
    CONSTRAINT chk_doctor_age CHECK (age BETWEEN 22 AND 80)
);

-- ─────────────────────────────────────────────
--  3. PATIENTS
-- ─────────────────────────────────────────────
CREATE TABLE patients (
    patient_id         INT          NOT NULL AUTO_INCREMENT,
    name               VARCHAR(100) NOT NULL,
    age                INT          NOT NULL,
    gender             ENUM('Male','Female','Other') NOT NULL,
    disease            VARCHAR(150) NOT NULL,
    admission_date     DATE         NOT NULL,
    status             ENUM('Admitted','Discharged') NOT NULL DEFAULT 'Admitted',
    assigned_doctor_id INT,
    created_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (patient_id),
    CONSTRAINT chk_patient_age CHECK (age > 0),
    CONSTRAINT fk_patient_doctor
        FOREIGN KEY (assigned_doctor_id) REFERENCES doctors(doctor_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- ─────────────────────────────────────────────
--  4. APPOINTMENTS
-- ─────────────────────────────────────────────
CREATE TABLE appointments (
    appt_id    INT          NOT NULL AUTO_INCREMENT,
    patient_id INT          NOT NULL,
    doctor_id  INT          NOT NULL,
    appt_date  DATE         NOT NULL,
    reason     VARCHAR(200),
    status     ENUM('Scheduled','Completed','Cancelled') NOT NULL DEFAULT 'Scheduled',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (appt_id),
    CONSTRAINT fk_appt_patient
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_appt_doctor
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        ON DELETE CASCADE
);

-- ─────────────────────────────────────────────
--  5. BILLING
-- ─────────────────────────────────────────────
CREATE TABLE billing (
    bill_id         INT           NOT NULL AUTO_INCREMENT,
    patient_id      INT           NOT NULL,
    days_admitted   INT           NOT NULL,
    daily_charge    DECIMAL(10,2) NOT NULL,
    medicine_charge DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_amount    DECIMAL(10,2),
    bill_date       DATE          NOT NULL,
    PRIMARY KEY (bill_id),
    CONSTRAINT chk_days CHECK (days_admitted > 0),
    CONSTRAINT chk_daily CHECK (daily_charge >= 0),
    CONSTRAINT chk_medicine CHECK (medicine_charge >= 0),
    CONSTRAINT fk_bill_patient
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        ON DELETE CASCADE
);

-- ─────────────────────────────────────────────
--  6. AUDIT LOG
-- ─────────────────────────────────────────────
CREATE TABLE audit_log (
    log_id     INT          NOT NULL AUTO_INCREMENT,
    table_name VARCHAR(50)  NOT NULL,
    action     VARCHAR(20)  NOT NULL,
    record_id  INT          NOT NULL,
    details    VARCHAR(300),
    changed_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id)
);
