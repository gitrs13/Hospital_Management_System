# Hospital Management System

A Python-based Hospital Management System with a modern GUI, backed by a MySQL database. Built as a Database Systems lab mini project demonstrating stored procedures, functions, triggers, and full DB connectivity.

---

## Features

- Login authentication from MySQL `users` table
- Add, search, discharge, and delete patients
- Add doctors and assign them to patients
- Book and manage appointments
- Generate bills with auto-calculated totals (via trigger)
- Reports: patients per doctor, revenue, admitted patients
- Audit log: all DB changes automatically logged by triggers

---

## Tech Stack

| Component     | Technology              |
|---------------|-------------------------|
| Database      | MySQL 8.x               |
| Language      | Python 3.x              |
| GUI           | CustomTkinter           |
| DB Connector  | mysql-connector-python  |

---

## Project Structure

```
dbs_project/
├── sql/
│   ├── schema.sql        # DDL — creates all 6 tables
│   ├── functions.sql     # 3 SQL functions
│   ├── procedures.sql    # 6 stored procedures
│   ├── triggers.sql      # 5 triggers
│   └── sample_data.sql   # Seed data for demo
├── model/
│   ├── person.py         # Base class
│   ├── patient.py        # Patient model
│   ├── doctor.py         # Doctor model
│   ├── billing.py        # Billing model
│   └── appointment.py    # Appointment model
├── database.py           # MySQL connection
├── login.py              # Login screen (entry point)
├── main_gui.py           # Main 6-tab GUI
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/gitrs13/Hospital_Management_System.git
cd Hospital_Management_System
```

### 2. Install Python dependencies
```bash
pip install customtkinter mysql-connector-python
```

### 3. Set up MySQL database
Run the SQL files in order in MySQL Workbench or CLI:
```bash
mysql -u root -p < sql/schema.sql
mysql -u root -p hospital_db < sql/functions.sql
mysql -u root -p hospital_db < sql/procedures.sql
mysql -u root -p hospital_db < sql/triggers.sql
mysql -u root -p hospital_db < sql/sample_data.sql
```

### 4. Configure DB credentials
Open `database.py` and update:
```python
DB_PASSWORD = "your_mysql_password"
```

### 5. Run the application
```bash
python login.py
```

---

## Default Login
| Username | Password |
|----------|----------|
| admin    | admin123 |

---

## Database Schema

6 normalized tables: `users`, `doctors`, `patients`, `appointments`, `billing`, `audit_log`

**PL/SQL Objects:**
- 3 Functions: `fn_calculate_bill`, `fn_get_doctor_name`, `fn_count_patients_for_doctor`
- 6 Procedures: `sp_add_patient`, `sp_add_doctor`, `sp_discharge_patient`, `sp_assign_doctor`, `sp_book_appointment`, `sp_generate_bill`
- 5 Triggers: patient insert/delete audit, doctor insert audit, bill auto-total, appointment status audit

---

## Author
**Riddhi Sahoo** — Registration No. 240911394  
Information Technology, Section IT-C, Roll No. 37
