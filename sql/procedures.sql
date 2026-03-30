-- ============================================================
--  Hospital Management System  |  procedures.sql
--  Run AFTER functions.sql:
--      mysql -u root -p hospital_db < sql/procedures.sql
-- ============================================================

USE hospital_db;

DELIMITER $$

-- ─────────────────────────────────────────────
--  sp_add_doctor
--  Inserts a new doctor record
-- ─────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_add_doctor$$

CREATE PROCEDURE sp_add_doctor(
    IN p_name           VARCHAR(100),
    IN p_age            INT,
    IN p_gender         VARCHAR(10),
    IN p_specialization VARCHAR(100),
    IN p_phone          VARCHAR(15),
    IN p_email          VARCHAR(100)
)
BEGIN
    INSERT INTO doctors (name, age, gender, specialization, phone, email)
    VALUES (p_name, p_age, p_gender, p_specialization, p_phone, p_email);

    SELECT LAST_INSERT_ID() AS new_doctor_id;
END$$


-- ─────────────────────────────────────────────
--  sp_add_patient
--  Inserts a new patient record
-- ─────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_add_patient$$

CREATE PROCEDURE sp_add_patient(
    IN p_name      VARCHAR(100),
    IN p_age       INT,
    IN p_gender    VARCHAR(10),
    IN p_disease   VARCHAR(150),
    IN p_doctor_id INT          -- may be NULL
)
BEGIN
    INSERT INTO patients (name, age, gender, disease, admission_date, assigned_doctor_id)
    VALUES (p_name, p_age, p_gender, p_disease, CURDATE(), p_doctor_id);

    SELECT LAST_INSERT_ID() AS new_patient_id;
END$$


-- ─────────────────────────────────────────────
--  sp_discharge_patient
--  Sets a patient's status to 'Discharged'
-- ─────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_discharge_patient$$

CREATE PROCEDURE sp_discharge_patient(
    IN p_patient_id INT
)
BEGIN
    DECLARE v_exists INT DEFAULT 0;

    SELECT COUNT(*) INTO v_exists
    FROM   patients
    WHERE  patient_id = p_patient_id;

    IF v_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Patient not found.';
    ELSE
        UPDATE patients
        SET    status = 'Discharged'
        WHERE  patient_id = p_patient_id;

        SELECT ROW_COUNT() AS rows_affected;
    END IF;
END$$


-- ─────────────────────────────────────────────
--  sp_assign_doctor
--  Assigns / re-assigns a doctor to a patient
-- ─────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_assign_doctor$$

CREATE PROCEDURE sp_assign_doctor(
    IN p_patient_id INT,
    IN p_doctor_id  INT
)
BEGIN
    DECLARE v_patient INT DEFAULT 0;
    DECLARE v_doctor  INT DEFAULT 0;

    SELECT COUNT(*) INTO v_patient FROM patients WHERE patient_id = p_patient_id;
    SELECT COUNT(*) INTO v_doctor  FROM doctors  WHERE doctor_id  = p_doctor_id;

    IF v_patient = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Patient not found.';
    ELSEIF v_doctor = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Doctor not found.';
    ELSE
        UPDATE patients
        SET    assigned_doctor_id = p_doctor_id
        WHERE  patient_id = p_patient_id;

        SELECT ROW_COUNT() AS rows_affected;
    END IF;
END$$


-- ─────────────────────────────────────────────
--  sp_book_appointment
--  Books a new appointment for a patient
-- ─────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_book_appointment$$

CREATE PROCEDURE sp_book_appointment(
    IN p_patient_id INT,
    IN p_doctor_id  INT,
    IN p_appt_date  DATE,
    IN p_reason     VARCHAR(200)
)
BEGIN
    INSERT INTO appointments (patient_id, doctor_id, appt_date, reason)
    VALUES (p_patient_id, p_doctor_id, p_appt_date, p_reason);

    SELECT LAST_INSERT_ID() AS new_appt_id;
END$$


-- ─────────────────────────────────────────────
--  sp_generate_bill
--  Creates a billing record for a patient
--  (total_amount is auto-calculated by trigger)
-- ─────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_generate_bill$$

CREATE PROCEDURE sp_generate_bill(
    IN p_patient_id      INT,
    IN p_days            INT,
    IN p_daily_charge    DECIMAL(10,2),
    IN p_medicine_charge DECIMAL(10,2)
)
BEGIN
    INSERT INTO billing (patient_id, days_admitted, daily_charge, medicine_charge, bill_date)
    VALUES (p_patient_id, p_days, p_daily_charge, p_medicine_charge, CURDATE());

    -- Return the generated bill with total (set by trigger)
    SELECT b.bill_id,
           b.patient_id,
           p.name          AS patient_name,
           b.days_admitted,
           b.daily_charge,
           b.medicine_charge,
           b.total_amount,
           b.bill_date
    FROM   billing  b
    JOIN   patients p ON p.patient_id = b.patient_id
    WHERE  b.bill_id = LAST_INSERT_ID();
END$$


-- ─────────────────────────────────────────────
--  sp_update_appointment_status
--  Changes appointment status
-- ─────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_update_appointment_status$$

CREATE PROCEDURE sp_update_appointment_status(
    IN p_appt_id INT,
    IN p_status  VARCHAR(20)
)
BEGIN
    UPDATE appointments
    SET    status = p_status
    WHERE  appt_id = p_appt_id;

    SELECT ROW_COUNT() AS rows_affected;
END$$

DELIMITER ;
