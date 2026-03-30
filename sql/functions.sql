-- ============================================================
--  Hospital Management System  |  functions.sql
--  Run AFTER schema.sql:
--      mysql -u root -p hospital_db < sql/functions.sql
-- ============================================================

USE hospital_db;

DELIMITER $$

-- ─────────────────────────────────────────────
--  fn_calculate_bill
--  Returns the total bill amount
--  total = (days × daily_charge) + medicine_charge
-- ─────────────────────────────────────────────
DROP FUNCTION IF EXISTS fn_calculate_bill$$

CREATE FUNCTION fn_calculate_bill(
    p_days          INT,
    p_daily_charge  DECIMAL(10,2),
    p_medicine      DECIMAL(10,2)
)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    RETURN (p_days * p_daily_charge) + p_medicine;
END$$


-- ─────────────────────────────────────────────
--  fn_count_patients_for_doctor
--  Returns number of currently admitted patients
--  assigned to a given doctor
-- ─────────────────────────────────────────────
DROP FUNCTION IF EXISTS fn_count_patients_for_doctor$$

CREATE FUNCTION fn_count_patients_for_doctor(
    p_doctor_id INT
)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_count INT DEFAULT 0;
    SELECT COUNT(*)
    INTO   v_count
    FROM   patients
    WHERE  assigned_doctor_id = p_doctor_id
      AND  status = 'Admitted';
    RETURN v_count;
END$$


-- ─────────────────────────────────────────────
--  fn_get_doctor_name
--  Returns full name of a doctor given their ID
--  Returns 'Not Assigned' if ID is NULL / not found
-- ─────────────────────────────────────────────
DROP FUNCTION IF EXISTS fn_get_doctor_name$$

CREATE FUNCTION fn_get_doctor_name(
    p_doctor_id INT
)
RETURNS VARCHAR(100)
READS SQL DATA
BEGIN
    DECLARE v_name VARCHAR(100) DEFAULT 'Not Assigned';
    IF p_doctor_id IS NOT NULL THEN
        SELECT name INTO v_name
        FROM   doctors
        WHERE  doctor_id = p_doctor_id
        LIMIT  1;
    END IF;
    RETURN v_name;
END$$

DELIMITER ;
