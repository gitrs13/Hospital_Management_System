import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from database import get_connection

# ── Theme ────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LoginApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Hospital Management System — Login")
        self.root.geometry("480x520")
        self.root.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self.root, fg_color="#1a73e8", corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="🏥  Hospital Management System",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color="white"
        ).pack(pady=18)

        # ── Card ─────────────────────────────────────────────
        card = ctk.CTkFrame(self.root, corner_radius=16)
        card.pack(padx=40, pady=30, fill="both", expand=True)

        ctk.CTkLabel(
            card,
            text="Sign In",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(24, 4))

        ctk.CTkLabel(
            card,
            text="Enter your credentials to continue",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 20))

        # Username
        ctk.CTkLabel(card, text="Username", anchor="w").pack(
            fill="x", padx=30)
        self.username_entry = ctk.CTkEntry(
            card, placeholder_text="admin", height=38)
        self.username_entry.pack(fill="x", padx=30, pady=(4, 14))

        # Password
        ctk.CTkLabel(card, text="Password", anchor="w").pack(
            fill="x", padx=30)
        self.password_entry = ctk.CTkEntry(
            card, placeholder_text="••••••••", show="*", height=38)
        self.password_entry.pack(fill="x", padx=30, pady=(4, 24))

        # Login button
        ctk.CTkButton(
            card,
            text="Login",
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.authenticate
        ).pack(fill="x", padx=30, pady=(0, 10))

        # Error label (hidden by default)
        self.error_label = ctk.CTkLabel(
            card, text="", text_color="#ff5555",
            font=ctk.CTkFont(size=12))
        self.error_label.pack(pady=4)

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self.authenticate())

    def authenticate(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.configure(text="Please enter both fields.")
            return

        try:
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, role FROM users "
                "WHERE username = %s AND password = %s",
                (username, password)
            )
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                self.root.destroy()
                # Launch main GUI
                from main_gui import HospitalGUI
                app_root = ctk.CTk()
                HospitalGUI(app_root)
                app_root.mainloop()
            else:
                self.error_label.configure(
                    text="❌ Invalid username or password.")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))


if __name__ == "__main__":
    root = ctk.CTk()
    LoginApp(root)
    root.mainloop()
