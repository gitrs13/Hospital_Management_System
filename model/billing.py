from datetime import date


class Billing:
    """Handles bill generation via stored procedure and SQL function."""

    def __init__(self, patient_id: int, days: int,
                 daily_charge: float, medicine_charge: float = 0.0):
        self.patient_id      = patient_id
        self.days            = days
        self.daily_charge    = daily_charge
        self.medicine_charge = medicine_charge

    # ── Write Operations ──────────────────────────────────────
    def generate_bill(self, cursor, conn) -> dict:
        """
        Calls sp_generate_bill.
        The trigger trg_before_bill_insert auto-calculates total_amount.
        Returns a dict with bill details.
        """
        bill_date = date.today().strftime("%Y-%m-%d")
        cursor.callproc("sp_generate_bill", [
            self.patient_id,
            self.days,
            self.daily_charge,
            self.medicine_charge
        ])
        conn.commit()
        for result in cursor.stored_results():
            row = result.fetchone()
            if row:
                cols = ["bill_id", "patient_id", "patient_name",
                        "days_admitted", "daily_charge",
                        "medicine_charge", "total_amount", "bill_date"]
                return dict(zip(cols, row))
        return {}

    # ── Read Operations ───────────────────────────────────────
    @staticmethod
    def get_all(cursor) -> list:
        """Returns all bills joined with patient name."""
        cursor.execute("""
            SELECT b.bill_id,
                   p.name        AS patient_name,
                   b.days_admitted,
                   b.daily_charge,
                   b.medicine_charge,
                   b.total_amount,
                   b.bill_date
            FROM   billing  b
            JOIN   patients p ON p.patient_id = b.patient_id
            ORDER  BY b.bill_id DESC
        """)
        return cursor.fetchall()

    @staticmethod
    def get_for_patient(cursor, patient_id: int) -> list:
        cursor.execute("""
            SELECT bill_id, days_admitted, daily_charge,
                   medicine_charge, total_amount, bill_date
            FROM   billing
            WHERE  patient_id = %s
            ORDER  BY bill_id DESC
        """, (patient_id,))
        return cursor.fetchall()

    @staticmethod
    def calculate_preview(cursor, days: int,
                          daily: float, medicine: float) -> float:
        """Uses fn_calculate_bill SQL function for a live preview."""
        cursor.execute(
            "SELECT fn_calculate_bill(%s, %s, %s)", (days, daily, medicine)
        )
        row = cursor.fetchone()
        return float(row[0]) if row else 0.0
