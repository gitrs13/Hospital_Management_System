from .person import Person
from datetime import date


class Patient(Person):
    """Represents a hospital patient. Calls stored procedures for DB operations."""

    def __init__(self, name: str, age: int, gender: str,
                 disease: str, doctor_id: int = None):
        super().__init__(name, age, gender)
        self.disease   = disease
        self.doctor_id = doctor_id

    # ── Write Operations ──────────────────────────────────────
    def save_to_db(self, cursor, conn) -> int:
        """Calls sp_add_patient procedure and returns new patient_id."""
        admission_date = date.today().strftime("%Y-%m-%d")
        cursor.callproc("sp_add_patient", [
            self.name, self.age, self.gender,
            self.disease, self.doctor_id
        ])
        conn.commit()
        # sp_add_patient does an INSERT; get the new id
        cursor.execute("SELECT LAST_INSERT_ID()")
        row = cursor.fetchone()
        return row[0] if row else -1

    @staticmethod
    def discharge(cursor, conn, patient_id: int):
        """Calls sp_discharge_patient procedure."""
        cursor.callproc("sp_discharge_patient", [patient_id])
        for _ in cursor.stored_results():
            pass
        conn.commit()

    @staticmethod
    def assign_doctor(cursor, conn, patient_id: int, doctor_id: int):
        """Calls sp_assign_doctor procedure."""
        cursor.callproc("sp_assign_doctor", [patient_id, doctor_id])
        conn.commit()

    @staticmethod
    def delete_from_db(cursor, conn, patient_id: int):
        """Deletes a patient (triggers trg_after_patient_delete → audit_log)."""
        cursor.execute(
            "DELETE FROM patients WHERE patient_id = %s", (patient_id,)
        )
        conn.commit()

    # ── Read Operations ───────────────────────────────────────
    @staticmethod
    def get_all(cursor) -> list:
        """Returns all patients joined with doctor name."""
        cursor.execute("""
            SELECT p.patient_id,
                   p.name,
                   p.age,
                   p.gender,
                   p.disease,
                   p.admission_date,
                   p.status,
                   fn_get_doctor_name(p.assigned_doctor_id) AS doctor_name
            FROM   patients p
            ORDER  BY p.patient_id
        """)
        return cursor.fetchall()

    @staticmethod
    def get_by_id(cursor, patient_id: int):
        cursor.execute(
            "SELECT patient_id, name, age, gender, disease, "
            "admission_date, status, assigned_doctor_id "
            "FROM patients WHERE patient_id = %s", (patient_id,)
        )
        return cursor.fetchone()

    @staticmethod
    def search(cursor, keyword: str) -> list:
        """Search patients by name or disease."""
        like = f"%{keyword}%"
        cursor.execute("""
            SELECT p.patient_id,
                   p.name,
                   p.age,
                   p.gender,
                   p.disease,
                   p.admission_date,
                   p.status,
                   fn_get_doctor_name(p.assigned_doctor_id) AS doctor_name
            FROM   patients p
            WHERE  p.name LIKE %s OR p.disease LIKE %s
            ORDER  BY p.patient_id
        """, (like, like))
        return cursor.fetchall()
