from .person import Person
from datetime import date


class Doctor(Person):
    """Represents a hospital doctor. Calls stored procedures for DB operations."""

    def __init__(self, name: str, age: int, gender: str,
                 specialization: str, phone: str, email: str = ""):
        super().__init__(name, age, gender)
        self.specialization = specialization
        self.phone          = phone
        self.email          = email

    # ── Write Operations ──────────────────────────────────────
    def save_to_db(self, cursor, conn) -> int:
        """Calls sp_add_doctor procedure and returns new doctor_id."""
        cursor.callproc("sp_add_doctor", [
            self.name, self.age, self.gender,
            self.specialization, self.phone, self.email
        ])
        conn.commit()
        for result in cursor.stored_results():
            row = result.fetchone()
            if row:
                return row[0]   # new_doctor_id
        return -1

    # ── Read Operations ───────────────────────────────────────
    @staticmethod
    def get_all(cursor) -> list:
        """Returns all doctors as a list of tuples."""
        cursor.execute(
            "SELECT doctor_id, name, age, gender, specialization, phone, email "
            "FROM doctors ORDER BY doctor_id"
        )
        return cursor.fetchall()

    @staticmethod
    def get_by_id(cursor, doctor_id: int):
        cursor.execute(
            "SELECT doctor_id, name, age, gender, specialization, phone, email "
            "FROM doctors WHERE doctor_id = %s", (doctor_id,)
        )
        return cursor.fetchone()

    @staticmethod
    def get_patient_count(cursor, doctor_id: int) -> int:
        """Uses fn_count_patients_for_doctor SQL function."""
        cursor.execute(
            "SELECT fn_count_patients_for_doctor(%s)", (doctor_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else 0
