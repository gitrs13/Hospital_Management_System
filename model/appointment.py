from datetime import date


class Appointment:
    """Handles appointment booking via stored procedure."""

    def __init__(self, patient_id: int, doctor_id: int,
                 appt_date: str, reason: str = ""):
        self.patient_id = patient_id
        self.doctor_id  = doctor_id
        self.appt_date  = appt_date
        self.reason     = reason

    # ── Write Operations ──────────────────────────────────────
    def book(self, cursor, conn) -> int:
        """Calls sp_book_appointment and returns new appt_id."""
        cursor.callproc("sp_book_appointment", [
            self.patient_id, self.doctor_id,
            self.appt_date, self.reason
        ])
        conn.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        row = cursor.fetchone()
        return row[0] if row else -1

    @staticmethod
    def update_status(cursor, conn, appt_id: int, status: str):
        """
        Calls sp_update_appointment_status.
        Triggers trg_after_appointment_update → audit_log.
        """
        cursor.callproc("sp_update_appointment_status", [appt_id, status])
        # Consume stored results so cursor is free for next query
        for _ in cursor.stored_results():
            pass
        conn.commit()

    # ── Read Operations ───────────────────────────────────────
    @staticmethod
    def get_all(cursor) -> list:
        cursor.execute("""
            SELECT a.appt_id,
                   p.name  AS patient_name,
                   d.name  AS doctor_name,
                   a.appt_date,
                   a.reason,
                   a.status
            FROM   appointments a
            JOIN   patients p ON p.patient_id = a.patient_id
            JOIN   doctors  d ON d.doctor_id  = a.doctor_id
            ORDER  BY a.appt_date DESC
        """)
        return cursor.fetchall()

    @staticmethod
    def get_for_patient(cursor, patient_id: int) -> list:
        cursor.execute("""
            SELECT a.appt_id, d.name AS doctor_name,
                   a.appt_date, a.reason, a.status
            FROM   appointments a
            JOIN   doctors d ON d.doctor_id = a.doctor_id
            WHERE  a.patient_id = %s
            ORDER  BY a.appt_date DESC
        """, (patient_id,))
        return cursor.fetchall()
