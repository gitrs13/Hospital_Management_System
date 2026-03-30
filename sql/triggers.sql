-- ============================================================
--  Hospital Management System  |  triggers.sql
--  Run AFTER procedures.sql:
--      mysql -u root -p hospital_db < sql/triggers.sql
-- ============================================================

USE hospital_db;

DELIMITER $$

-- ─────────────────────────────────────────────
--  TRIGGER 1: trg_after_patient_insert
--  Fires AFTER a new patient row is inserted
--  → Logs the event in audit_log
-- ─────────────────────────────────────────────
DROP TRIGGER IF EXISTS trg_after_patient_insert$$

CREATE TRIGGER trg_after_patient_insert
AFTER INSERT ON patients
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, action, record_id, details)
    VALUES (
        'patients',
        'INSERT',
        NEW.patient_id,
        CONCAT('New patient added: ', NEW.name, ' | Disease: ', NEW.disease)
    );
END$$


-- ─────────────────────────────────────────────
--  TRIGGER 2: trg_after_patient_delete
--  Fires AFTER a patient row is deleted
--  → Logs the event in audit_log
-- ─────────────────────────────────────────────
DROP TRIGGER IF EXISTS trg_after_patient_delete$$

CREATE TRIGGER trg_after_patient_delete
AFTER DELETE ON patients
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, action, record_id, details)
    VALUES (
        'patients',
        'DELETE',
        OLD.patient_id,
        CONCAT('Patient removed: ', OLD.name, ' | Disease: ', OLD.disease)
    );
END$$


-- ─────────────────────────────────────────────
--  TRIGGER 3: trg_before_bill_insert
--  Fires BEFORE a billing row is inserted
--  → Auto-calculates total_amount using fn_calculate_bill
--    so Python never has to send the total manually
-- ─────────────────────────────────────────────
DROP TRIGGER IF EXISTS trg_before_bill_insert$$

CREATE TRIGGER trg_before_bill_insert
BEFORE INSERT ON billing
FOR EACH ROW
BEGIN
    SET NEW.total_amount = fn_calculate_bill(
        NEW.days_admitted,
        NEW.daily_charge,
        NEW.medicine_charge
    );
END$$


-- ─────────────────────────────────────────────
--  TRIGGER 4: trg_after_appointment_update
--  Fires AFTER an appointment status is updated
--  → Logs the status change in audit_log
-- ─────────────────────────────────────────────
DROP TRIGGER IF EXISTS trg_after_appointment_update$$

CREATE TRIGGER trg_after_appointment_update
AFTER UPDATE ON appointments
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO audit_log (table_name, action, record_id, details)
        VALUES (
            'appointments',
            'UPDATE',
            NEW.appt_id,
            CONCAT('Appointment #', NEW.appt_id,
                   ' status changed from ', OLD.status, ' to ', NEW.status)
        );
    END IF;
END$$


-- ─────────────────────────────────────────────
--  TRIGGER 5: trg_after_doctor_insert
--  Fires AFTER a new doctor row is inserted
--  → Logs the event in audit_log
-- ─────────────────────────────────────────────
DROP TRIGGER IF EXISTS trg_after_doctor_insert$$

CREATE TRIGGER trg_after_doctor_insert
AFTER INSERT ON doctors
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, action, record_id, details)
    VALUES (
        'doctors',
        'INSERT',
        NEW.doctor_id,
        CONCAT('New doctor added: ', NEW.name, ' | Specialization: ', NEW.specialization)
    );
END$$

DELIMITER ;
