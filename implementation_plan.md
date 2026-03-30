# Hospital Management System – Implementation Plan

A comprehensive DBS mini-project built on **Python + MySQL**, using the reference repo as a base but heavily extended to satisfy all evaluation requirements:
- ER Diagram & Normalised tables, DDL + integrity constraints
- PL/SQL Procedures / Functions / Triggers
- Java-style DB connectivity via Python (`mysql-connector-python`)
- Modern GUI (CustomTkinter)

---

## Proposed Changes

### Database Layer

#### [NEW] [schema.sql](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/sql/schema.sql)
Creates the `hospital_db` database with **6 tables** (all 3NF/BCNF):

| Table | Key Fields |
|---|---|
| `users` | user_id, username, password_hash, role |
| `doctors` | doctor_id (PK, AUTO_INCREMENT), name, age, gender, specialization, phone, email |
| `patients` | patient_id (PK, AUTO_INCREMENT), name, age, gender, disease, admission_date, status, assigned_doctor_id (FK) |
| `appointments` | appt_id (PK), patient_id (FK), doctor_id (FK), appt_date, reason, status |
| `billing` | bill_id (PK, AUTO_INCREMENT), patient_id (FK), days_admitted, daily_charge, medicine_charge, total_amount, bill_date |
| `audit_log` | log_id (PK), table_name, action, record_id, changed_by, changed_at |

All FK constraints, NOT NULL, CHECK constraints included.

#### [NEW] [procedures.sql](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/sql/procedures.sql)
Stored procedures called by Python:
- `sp_add_patient(name, age, gender, disease, doctor_id)` – inserts patient
- `sp_discharge_patient(patient_id)` – updates status to 'Discharged'
- `sp_add_doctor(name, age, gender, spec, phone, email)` – inserts doctor
- `sp_assign_doctor(patient_id, doctor_id)` – updates assigned_doctor_id
- `sp_generate_bill(patient_id, days, daily_charge, med_charge)` – inserts billing row
- `sp_book_appointment(patient_id, doctor_id, date, reason)` – inserts appointment

#### [NEW] [functions.sql](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/sql/functions.sql)
SQL functions:
- `fn_calculate_bill(days, daily_charge, med_charge)` → DECIMAL – total bill
- `fn_count_patients_for_doctor(doctor_id)` → INT – active patients per doctor
- `fn_get_doctor_name(doctor_id)` → VARCHAR – doctor name lookup

#### [NEW] [triggers.sql](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/sql/triggers.sql)
Triggers:
- `trg_after_patient_insert` – logs INSERT into audit_log
- `trg_after_patient_delete` – logs DELETE into audit_log
- `trg_before_bill_insert` – auto-calculates total_amount using `fn_calculate_bill`
- `trg_after_appointment_update` – logs appointment status changes

#### [NEW] [sample_data.sql](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/sql/sample_data.sql)
Seeds 5 doctors, 10 patients, 8 appointments, 5 bills, 1 admin user.

---

### Python Backend

#### [NEW] [database.py](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/database.py)
MySQL connection manager with reconnection logic, single shared `conn` + `cursor`.

#### [MODIFY] [model/person.py](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/model/person.py)
Base class for shared fields. No changes needed from reference.

#### [MODIFY] [model/patient.py](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/model/patient.py)
- `save_to_db` → calls `sp_add_patient` procedure via `callproc`
- `discharge` → calls `sp_discharge_patient`
- `get_all`, `get_by_id` static methods for GUI display

#### [MODIFY] [model/doctor.py](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/model/doctor.py)
- `save_to_db` → calls `sp_add_doctor`
- `get_all` static method

#### [MODIFY] [model/billing.py](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/model/billing.py)
- `generate_bill` → calls `sp_generate_bill`; trigger auto-sets total
- `get_bill_for_patient` static method

#### [NEW] [model/appointment.py](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/model/appointment.py)
- `book` → calls `sp_book_appointment`
- `get_all`, `update_status` methods

---

### GUI Layer

#### [MODIFY] [login.py](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/login.py)
Modern CustomTkinter login window. Validates credentials against `users` table in DB (instead of hardcoded strings).

#### [MODIFY] [main_gui.py](file:///c:/4th%20Sem/dbs%20lab/project/dbs_project/main_gui.py)
Full tabbed GUI (`CTkTabview`) with:
| Tab | Features |
|---|---|
| 🧑‍⚕️ Patients | Add, Discharge, Search, View all (Treeview) |
| 👨‍⚕️ Doctors | Add, Search, View all (Treeview) |
| 📅 Appointments | Book, Update status, View all |
| 💰 Billing | Generate bill (calls procedure), View bills |
| 📊 Reports | Run pre-defined complex queries (patients per doctor, revenue) |
| 📋 Audit Log | View audit_log table entries |

---

## Verification Plan

### Automated / Script Tests
```
# 1. Set up database (run from MySQL Workbench or CLI)
mysql -u root -p < sql/schema.sql
mysql -u root -p hospital_db < sql/procedures.sql
mysql -u root -p hospital_db < sql/functions.sql
mysql -u root -p hospital_db < sql/triggers.sql
mysql -u root -p hospital_db < sql/sample_data.sql

# 2. Verify triggers and procedures exist
SHOW PROCEDURE STATUS WHERE Db = 'hospital_db';
SHOW FUNCTION STATUS WHERE Db = 'hospital_db';
SHOW TRIGGERS FROM hospital_db;

# 3. Run the application
pip install customtkinter mysql-connector-python
python login.py
```

### Manual Verification (step-by-step)
1. **Login**: Enter `admin` / `admin123` → main window opens
2. **Add Patient**: Fill form → click Add → row appears in Patients Treeview → check audit_log tab for INSERT entry
3. **Generate Bill**: Enter patient ID, days, charges → click Generate → total auto-filled by trigger → bill row appears in Billing tab
4. **Appointment Booking**: Select patient + doctor + date → Book → row in Appointments Treeview
5. **Discharge**: Select patient → Discharge → status changes to 'Discharged' → audit_log updated
6. **Reports Tab**: Click "Patients per Doctor" → table shows count grouped by doctor; Click "Revenue Report" → total bills per month
7. **Audit Log Tab**: All DB changes visible with timestamp
