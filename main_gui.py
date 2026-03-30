import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date

from database import conn, cursor
from model.patient     import Patient
from model.doctor      import Doctor
from model.billing     import Billing
from model.appointment import Appointment

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ─── Treeview style helper ────────────────────────────────────
def style_tree(tv: ttk.Treeview):
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("Treeview",
                background="#2b2b2b", foreground="white",
                fieldbackground="#2b2b2b", rowheight=26)
    s.configure("Treeview.Heading",
                background="#1a73e8", foreground="white",
                font=("Arial", 10, "bold"))
    s.map("Treeview", background=[("selected", "#1a5fb4")])


def make_tree(parent, columns: list, widths: list) -> ttk.Treeview:
    frame = ctk.CTkFrame(parent)
    frame.pack(fill="both", expand=True, padx=8, pady=6)

    sb = ttk.Scrollbar(frame, orient="vertical")
    sb.pack(side="right", fill="y")

    tv = ttk.Treeview(frame, columns=columns, show="headings",
                      yscrollcommand=sb.set)
    sb.config(command=tv.yview)

    for col, w in zip(columns, widths):
        tv.heading(col, text=col)
        tv.column(col, width=w, anchor="center")

    style_tree(tv)
    tv.pack(fill="both", expand=True)
    return tv


# ═══════════════════════════════════════════════════════════════
class HospitalGUI:
    def __init__(self, root: ctk.CTk):
        self.root   = root
        self.root.title("Hospital Management System")
        self.root.geometry("1280x780")
        self.root.resizable(True, True)
        self._build_header()
        self._build_tabs()

    # ── Header ────────────────────────────────────────────────
    def _build_header(self):
        hdr = ctk.CTkFrame(self.root, fg_color="#1a73e8",
                           corner_radius=0, height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(
            hdr,
            text="🏥  Hospital Management System",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(
            hdr,
            text=f"📅 {date.today().strftime('%d %b %Y')}",
            font=ctk.CTkFont(size=13),
            text_color="#cce4ff"
        ).pack(side="right", padx=20)

    # ── Tabs ──────────────────────────────────────────────────
    def _build_tabs(self):
        self.tabs = ctk.CTkTabview(self.root, anchor="nw")
        self.tabs.pack(fill="both", expand=True, padx=12, pady=10)

        for name in ["🧑‍⚕️ Patients", "👨‍⚕️ Doctors",
                     "📅 Appointments", "💰 Billing",
                     "📊 Reports", "📋 Audit Log"]:
            self.tabs.add(name)

        self._build_patients_tab()
        self._build_doctors_tab()
        self._build_appointments_tab()
        self._build_billing_tab()
        self._build_reports_tab()
        self._build_audit_tab()

    # ══════════════════════════════════════════════════════════
    # TAB 1 — PATIENTS
    # ══════════════════════════════════════════════════════════
    def _build_patients_tab(self):
        tab = self.tabs.tab("🧑‍⚕️ Patients")

        # ── Form ─────────────────────────────────────────────
        form = ctk.CTkFrame(tab)
        form.pack(fill="x", padx=8, pady=(8, 4))

        fields = ["Name", "Age", "Gender", "Disease", "Doctor ID"]
        self.p_entries = {}
        for i, f in enumerate(fields):
            ctk.CTkLabel(form, text=f, width=90, anchor="e").grid(
                row=i // 3, column=(i % 3) * 2, padx=(10, 4), pady=6, sticky="e")
            e = ctk.CTkEntry(form, width=180)
            e.grid(row=i // 3, column=(i % 3) * 2 + 1, padx=(0, 16), pady=6)
            self.p_entries[f] = e

        # ── Buttons ───────────────────────────────────────────
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8)

        for txt, cmd, color in [
            ("➕ Add Patient",    self.add_patient,    "#1a73e8"),
            ("🔍 Search",         self.search_patient, "#2e7d32"),
            ("🔄 Refresh",        self.load_patients,  "#5c6bc0"),
            ("🚪 Discharge",      self.discharge_patient, "#e65100"),
            ("🗑 Delete",         self.delete_patient, "#c62828"),
        ]:
            ctk.CTkButton(btn_frame, text=txt, width=140, height=34,
                          fg_color=color, command=cmd).pack(
                side="left", padx=5, pady=6)

        # ── Treeview ──────────────────────────────────────────
        cols = ["ID", "Name", "Age", "Gender", "Disease",
                "Admitted", "Status", "Doctor"]
        ws   = [50, 160, 50, 80, 160, 100, 100, 160]
        self.p_tree = make_tree(tab, cols, ws)
        self.p_tree.bind("<<TreeviewSelect>>", self._on_patient_select)
        self.load_patients()

    def _on_patient_select(self, _=None):
        sel = self.p_tree.focus()
        if sel:
            vals = self.p_tree.item(sel, "values")
            keys = ["Name", "Age", "Gender", "Disease", "Doctor ID"]
            data = [vals[1], vals[2], vals[3], vals[4], ""]
            for k, v in zip(keys, data):
                self.p_entries[k].delete(0, "end")
                self.p_entries[k].insert(0, v)

    def add_patient(self):
        try:
            name   = self.p_entries["Name"].get().strip()
            age    = int(self.p_entries["Age"].get().strip())
            gender = self.p_entries["Gender"].get().strip()
            dis    = self.p_entries["Disease"].get().strip()
            did_s  = self.p_entries["Doctor ID"].get().strip()
            did    = int(did_s) if did_s else None

            if not all([name, gender, dis]):
                messagebox.showwarning("Input Error", "Fill in all required fields.")
                return

            p = Patient(name, age, gender, dis, did)
            p.save_to_db(cursor, conn)
            messagebox.showinfo("Success", f"Patient '{name}' added.")
            self.load_patients()
            self.load_audit()
        except ValueError:
            messagebox.showerror("Error", "Age must be a number.")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def search_patient(self):
        kw = self.p_entries["Name"].get().strip()
        if not kw:
            self.load_patients(); return
        rows = Patient.search(cursor, kw)
        self._populate_tree(self.p_tree, rows)

    def discharge_patient(self):
        sel = self.p_tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Select a patient first."); return
        pid = self.p_tree.item(sel, "values")[0]
        if messagebox.askyesno("Discharge", f"Discharge patient ID {pid}?"):
            try:
                Patient.discharge(cursor, conn, int(pid))
                messagebox.showinfo("Done", "Patient discharged.")
                self.load_patients()
                self.load_audit()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_patient(self):
        sel = self.p_tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Select a patient first."); return
        pid  = self.p_tree.item(sel, "values")[0]
        name = self.p_tree.item(sel, "values")[1]
        if messagebox.askyesno("Delete", f"Delete patient '{name}' (ID {pid})?"):
            try:
                Patient.delete_from_db(cursor, conn, int(pid))
                messagebox.showinfo("Deleted", f"Patient '{name}' deleted.")
                self.load_patients()
                self.load_audit()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_patients(self):
        self._populate_tree(self.p_tree, Patient.get_all(cursor))

    # ══════════════════════════════════════════════════════════
    # TAB 2 — DOCTORS
    # ══════════════════════════════════════════════════════════
    def _build_doctors_tab(self):
        tab = self.tabs.tab("👨‍⚕️ Doctors")

        form = ctk.CTkFrame(tab)
        form.pack(fill="x", padx=8, pady=(8, 4))

        fields = ["Name", "Age", "Gender", "Specialization", "Phone", "Email"]
        self.d_entries = {}
        for i, f in enumerate(fields):
            ctk.CTkLabel(form, text=f, width=110, anchor="e").grid(
                row=i // 3, column=(i % 3) * 2, padx=(10, 4), pady=6, sticky="e")
            e = ctk.CTkEntry(form, width=190)
            e.grid(row=i // 3, column=(i % 3) * 2 + 1, padx=(0, 16), pady=6)
            self.d_entries[f] = e

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8)

        for txt, cmd, color in [
            ("➕ Add Doctor",  self.add_doctor,  "#1a73e8"),
            ("🔄 Refresh",     self.load_doctors, "#5c6bc0"),
        ]:
            ctk.CTkButton(btn_frame, text=txt, width=140, height=34,
                          fg_color=color, command=cmd).pack(
                side="left", padx=5, pady=6)

        cols = ["ID", "Name", "Age", "Gender",
                "Specialization", "Phone", "Email"]
        ws   = [50, 160, 50, 80, 160, 120, 200]
        self.d_tree = make_tree(tab, cols, ws)
        self.load_doctors()

    def add_doctor(self):
        try:
            vals = {k: v.get().strip() for k, v in self.d_entries.items()}
            if not all([vals["Name"], vals["Gender"], vals["Specialization"], vals["Phone"]]):
                messagebox.showwarning("Input", "Fill all required fields."); return
            d = Doctor(vals["Name"], int(vals["Age"]), vals["Gender"],
                       vals["Specialization"], vals["Phone"], vals["Email"])
            d.save_to_db(cursor, conn)
            messagebox.showinfo("Success", f"Doctor '{vals['Name']}' added.")
            self.load_doctors()
            self.load_audit()
        except ValueError:
            messagebox.showerror("Error", "Age must be a number.")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def load_doctors(self):
        self._populate_tree(self.d_tree, Doctor.get_all(cursor))

    # ══════════════════════════════════════════════════════════
    # TAB 3 — APPOINTMENTS
    # ══════════════════════════════════════════════════════════
    def _build_appointments_tab(self):
        tab = self.tabs.tab("📅 Appointments")

        form = ctk.CTkFrame(tab)
        form.pack(fill="x", padx=8, pady=(8, 4))

        labels   = ["Patient ID", "Doctor ID", "Date (YYYY-MM-DD)", "Reason"]
        self.a_entries = {}
        for i, lbl in enumerate(labels):
            ctk.CTkLabel(form, text=lbl, width=160, anchor="e").grid(
                row=0, column=i * 2, padx=(10, 4), pady=6, sticky="e")
            e = ctk.CTkEntry(form, width=180)
            e.grid(row=0, column=i * 2 + 1, padx=(0, 12), pady=6)
            self.a_entries[lbl] = e

        # Status updater
        ctk.CTkLabel(form, text="Appt ID", width=70, anchor="e").grid(
            row=1, column=0, padx=(10, 4), pady=6, sticky="e")
        self.a_status_id = ctk.CTkEntry(form, width=80)
        self.a_status_id.grid(row=1, column=1, padx=(0, 12), pady=6)

        ctk.CTkLabel(form, text="New Status", width=90, anchor="e").grid(
            row=1, column=2, padx=(10, 4), pady=6, sticky="e")
        self.a_status_var = ctk.CTkComboBox(
            form, values=["Scheduled", "Completed", "Cancelled"], width=160)
        self.a_status_var.grid(row=1, column=3, padx=(0, 12), pady=6)

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8)
        for txt, cmd, color in [
            ("📅 Book Appointment", self.book_appointment, "#1a73e8"),
            ("✏️ Update Status",    self.update_appt_status, "#2e7d32"),
            ("🔄 Refresh",          self.load_appointments,  "#5c6bc0"),
        ]:
            ctk.CTkButton(btn_frame, text=txt, width=170, height=34,
                          fg_color=color, command=cmd).pack(
                side="left", padx=5, pady=6)

        cols = ["ID", "Patient", "Doctor", "Date", "Reason", "Status"]
        ws   = [50, 160, 160, 110, 200, 110]
        self.a_tree = make_tree(tab, cols, ws)
        self.load_appointments()

    def book_appointment(self):
        try:
            pid    = int(self.a_entries["Patient ID"].get().strip())
            did    = int(self.a_entries["Doctor ID"].get().strip())
            dt     = self.a_entries["Date (YYYY-MM-DD)"].get().strip()
            reason = self.a_entries["Reason"].get().strip()
            Appointment(pid, did, dt, reason).book(cursor, conn)
            messagebox.showinfo("Success", "Appointment booked.")
            self.load_appointments()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_appt_status(self):
        try:
            aid    = int(self.a_status_id.get().strip())
            status = self.a_status_var.get()
            Appointment.update_status(cursor, conn, aid, status)
            messagebox.showinfo("Updated", "Status updated.")
            self.load_appointments()
            self.load_audit()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_appointments(self):
        self._populate_tree(self.a_tree, Appointment.get_all(cursor))

    # ══════════════════════════════════════════════════════════
    # TAB 4 — BILLING
    # ══════════════════════════════════════════════════════════
    def _build_billing_tab(self):
        tab = self.tabs.tab("💰 Billing")

        form = ctk.CTkFrame(tab)
        form.pack(fill="x", padx=8, pady=(8, 4))

        labels = ["Patient ID", "Days Admitted", "Daily Charge (₹)", "Medicine Charge (₹)"]
        self.b_entries = {}
        for i, lbl in enumerate(labels):
            ctk.CTkLabel(form, text=lbl, width=160, anchor="e").grid(
                row=0, column=i * 2, padx=(10, 4), pady=8, sticky="e")
            e = ctk.CTkEntry(form, width=160)
            e.grid(row=0, column=i * 2 + 1, padx=(0, 12), pady=8)
            self.b_entries[lbl] = e

        # Preview total label
        self.bill_preview = ctk.CTkLabel(
            form, text="Estimated Total: ₹ —",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1a73e8")
        self.bill_preview.grid(row=1, column=0, columnspan=4, pady=4)

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8)
        for txt, cmd, color in [
            ("🧮 Preview Total",  self.preview_bill,   "#5c6bc0"),
            ("💾 Generate Bill",  self.generate_bill,  "#1a73e8"),
            ("🔄 Refresh",        self.load_bills,     "#2e7d32"),
        ]:
            ctk.CTkButton(btn_frame, text=txt, width=160, height=34,
                          fg_color=color, command=cmd).pack(
                side="left", padx=5, pady=6)

        cols = ["Bill ID", "Patient", "Days", "Daily ₹",
                "Medicine ₹", "Total ₹", "Date"]
        ws   = [70, 160, 60, 100, 110, 110, 110]
        self.b_tree = make_tree(tab, cols, ws)
        self.load_bills()

    def preview_bill(self):
        try:
            days = int(self.b_entries["Days Admitted"].get())
            daily = float(self.b_entries["Daily Charge (₹)"].get())
            med   = float(self.b_entries["Medicine Charge (₹)"].get() or 0)
            total = Billing.calculate_preview(cursor, days, daily, med)
            self.bill_preview.configure(text=f"Estimated Total: ₹ {total:,.2f}")
        except ValueError:
            self.bill_preview.configure(text="Enter valid numbers first.")

    def generate_bill(self):
        try:
            pid  = int(self.b_entries["Patient ID"].get())
            days = int(self.b_entries["Days Admitted"].get())
            daily = float(self.b_entries["Daily Charge (₹)"].get())
            med   = float(self.b_entries["Medicine Charge (₹)"].get() or 0)
            result = Billing(pid, days, daily, med).generate_bill(cursor, conn)
            if result:
                messagebox.showinfo(
                    "Bill Generated",
                    f"Patient : {result.get('patient_name','')}\n"
                    f"Days    : {result.get('days_admitted')}\n"
                    f"Daily   : ₹{result.get('daily_charge')}\n"
                    f"Medicine: ₹{result.get('medicine_charge')}\n"
                    f"─────────────────\n"
                    f"TOTAL   : ₹{result.get('total_amount')}"
                )
            self.load_bills()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_bills(self):
        self._populate_tree(self.b_tree, Billing.get_all(cursor))

    # ══════════════════════════════════════════════════════════
    # TAB 5 — REPORTS
    # ══════════════════════════════════════════════════════════
    def _build_reports_tab(self):
        tab = self.tabs.tab("📊 Reports")

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8, pady=10)

        reports = [
            ("Patients per Doctor",   self.rpt_patients_per_doctor, "#1a73e8"),
            ("Revenue Summary",       self.rpt_revenue,             "#2e7d32"),
            ("Admitted Patients",     self.rpt_admitted,            "#5c6bc0"),
            ("Appointment Summary",   self.rpt_appointments,        "#e65100"),
        ]
        for txt, cmd, color in reports:
            ctk.CTkButton(btn_frame, text=txt, width=190, height=36,
                          fg_color=color, command=cmd).pack(
                side="left", padx=6)

        self.rpt_label = ctk.CTkLabel(
            tab, text="Select a report above",
            font=ctk.CTkFont(size=13), text_color="gray")
        self.rpt_label.pack(pady=4)

        self.rpt_tree_frame = ctk.CTkFrame(tab)
        self.rpt_tree_frame.pack(fill="both", expand=True, padx=8, pady=6)

    def _show_report(self, title: str, cols: list, rows: list, widths: list):
        for w in self.rpt_tree_frame.winfo_children():
            w.destroy()
        self.rpt_label.configure(text=title)
        tv = make_tree(self.rpt_tree_frame, cols, widths)
        for r in rows:
            tv.insert("", "end", values=[str(x) for x in r])

    def rpt_patients_per_doctor(self):
        cursor.execute("""
            SELECT d.name AS Doctor,
                   fn_count_patients_for_doctor(d.doctor_id) AS Active_Patients,
                   d.specialization
            FROM   doctors d
            ORDER  BY Active_Patients DESC
        """)
        self._show_report("Patients per Doctor",
                          ["Doctor", "Active Patients", "Specialization"],
                          cursor.fetchall(), [200, 140, 180])

    def rpt_revenue(self):
        cursor.execute("""
            SELECT DATE_FORMAT(bill_date,'%Y-%m') AS Month,
                   COUNT(*) AS Bills,
                   SUM(total_amount) AS Total_Revenue
            FROM   billing
            GROUP  BY Month
            ORDER  BY Month DESC
        """)
        self._show_report("Monthly Revenue",
                          ["Month", "Bills", "Total Revenue (₹)"],
                          cursor.fetchall(), [120, 80, 160])

    def rpt_admitted(self):
        cursor.execute("""
            SELECT p.patient_id, p.name, p.disease,
                   p.admission_date,
                   fn_get_doctor_name(p.assigned_doctor_id) AS Doctor
            FROM   patients p
            WHERE  p.status = 'Admitted'
            ORDER  BY p.admission_date
        """)
        self._show_report("Currently Admitted Patients",
                          ["ID", "Name", "Disease", "Admitted", "Doctor"],
                          cursor.fetchall(), [50, 160, 160, 110, 180])

    def rpt_appointments(self):
        cursor.execute("""
            SELECT status, COUNT(*) AS Count
            FROM   appointments
            GROUP  BY status
        """)
        self._show_report("Appointment Status Summary",
                          ["Status", "Count"],
                          cursor.fetchall(), [160, 100])

    # ══════════════════════════════════════════════════════════
    # TAB 6 — AUDIT LOG
    # ══════════════════════════════════════════════════════════
    def _build_audit_tab(self):
        tab = self.tabs.tab("📋 Audit Log")

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8, pady=8)
        ctk.CTkButton(btn_frame, text="🔄 Refresh Audit Log",
                      width=180, height=34,
                      command=self.load_audit).pack(side="left", padx=6)

        cols = ["Log ID", "Table", "Action", "Record ID",
                "Details", "Changed At"]
        ws   = [70, 110, 90, 90, 340, 160]
        self.audit_tree = make_tree(tab, cols, ws)
        self.load_audit()

    def load_audit(self):
        cursor.execute(
            "SELECT log_id, table_name, action, record_id, "
            "details, changed_at FROM audit_log ORDER BY log_id DESC"
        )
        self._populate_tree(self.audit_tree, cursor.fetchall())

    # ── Utility ───────────────────────────────────────────────
    @staticmethod
    def _populate_tree(tv: ttk.Treeview, rows: list):
        tv.delete(*tv.get_children())
        for row in rows:
            tv.insert("", "end", values=[str(x) if x is not None else "" for x in row])


# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    root = ctk.CTk()
    HospitalGUI(root)
    root.mainloop()
