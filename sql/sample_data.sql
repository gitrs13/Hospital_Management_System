-- ============================================================
--  Hospital Management System  |  sample_data.sql
--  Run LAST (after triggers.sql)
-- ============================================================

USE hospital_db;

-- Users
INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'admin'),
('staff1', 'staff123', 'staff');

-- Doctors  (trg_after_doctor_insert will fire → audit_log)
INSERT INTO doctors (name, age, gender, specialization, phone, email) VALUES
('Dr. Arjun Sharma',  45, 'Male',   'Cardiology',      '9876543210', 'arjun.sharma@hms.com'),
('Dr. Priya Mehta',   38, 'Female', 'Neurology',       '9876543211', 'priya.mehta@hms.com'),
('Dr. Rohan Verma',   52, 'Male',   'Orthopedics',     '9876543212', 'rohan.verma@hms.com'),
('Dr. Sneha Iyer',    40, 'Female', 'Pediatrics',      '9876543213', 'sneha.iyer@hms.com'),
('Dr. Vikram Das',    47, 'Male',   'General Surgery', '9876543214', 'vikram.das@hms.com');

-- Patients  (trg_after_patient_insert will fire → audit_log)
INSERT INTO patients (name, age, gender, disease, admission_date, status, assigned_doctor_id) VALUES
('Anita Rao',    34, 'Female', 'Hypertension',  '2026-03-01', 'Admitted',   1),
('Ravi Kumar',   58, 'Male',   'Diabetes',      '2026-03-05', 'Admitted',   1),
('Suman Ghosh',  27, 'Female', 'Migraine',      '2026-03-08', 'Admitted',   2),
('Deepak Patel', 45, 'Male',   'Knee Fracture', '2026-03-10', 'Admitted',   3),
('Kavya Nair',    8, 'Female', 'Typhoid',       '2026-03-12', 'Admitted',   4),
('Manoj Singh',  62, 'Male',   'Heart Disease', '2026-03-14', 'Admitted',   1),
('Pooja Joshi',  30, 'Female', 'Appendicitis',  '2026-03-15', 'Discharged', 5),
('Arjun Mishra', 41, 'Male',   'Back Pain',     '2026-03-17', 'Admitted',   3),
('Neha Tiwari',  25, 'Female', 'Asthma',        '2026-03-20', 'Admitted',   2),
('Suresh Reddy', 70, 'Male',   'Stroke',        '2026-03-22', 'Admitted',   2);

-- Appointments
INSERT INTO appointments (patient_id, doctor_id, appt_date, reason, status) VALUES
(1,  1, '2026-03-25', 'BP check-up',            'Completed'),
(2,  1, '2026-03-26', 'Blood sugar review',      'Completed'),
(3,  2, '2026-03-27', 'MRI follow-up',           'Scheduled'),
(4,  3, '2026-03-28', 'X-Ray review',            'Scheduled'),
(5,  4, '2026-03-28', 'Vaccination',             'Scheduled'),
(6,  1, '2026-03-29', 'ECG test',                'Scheduled'),
(8,  3, '2026-03-30', 'Physiotherapy session',   'Scheduled'),
(10, 2, '2026-03-31', 'CT Scan review',          'Scheduled');

-- Billing  (trg_before_bill_insert auto-calculates total_amount)
INSERT INTO billing (patient_id, days_admitted, daily_charge, medicine_charge, bill_date) VALUES
(1,  10, 1500.00,  800.00, '2026-03-27'),
(2,   8, 1500.00, 1200.00, '2026-03-27'),
(7,   5, 2000.00, 1500.00, '2026-03-27'),
(4,  12, 1800.00, 2000.00, '2026-03-27'),
(5,   6, 1200.00,  500.00, '2026-03-27');
