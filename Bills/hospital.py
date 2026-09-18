
import os
import sqlite3
import webbrowser
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox

APP_TITLE = "MediCare Hospital - Receptionist Management System"
DB_NAME = "medicare_hospital.db"


# ----------------------------- DATABASE -----------------------------

class Database:
    def __init__(self, db_name=DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.seed_data()

    def execute(self, sql, params=(), fetch=False, many=False):
        cur = self.conn.cursor()
        if many:
            cur.executemany(sql, params)
        else:
            cur.execute(sql, params)
        self.conn.commit()
        if fetch:
            return cur.fetchall()
        return cur

    def create_tables(self):
        self.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'Receptionist'
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT,
                blood_group TEXT,
                address TEXT,
                emergency_contact TEXT,
                registered_on TEXT NOT NULL
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                department TEXT NOT NULL,
                days TEXT NOT NULL,
                available_time TEXT NOT NULL,
                fee REAL DEFAULT 0
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT UNIQUE NOT NULL,
                patient_id TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                status TEXT DEFAULT 'Booked',
                notes TEXT
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS beds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bed_no TEXT UNIQUE NOT NULL,
                ward TEXT NOT NULL,
                bed_type TEXT NOT NULL,
                status TEXT DEFAULT 'Available',
                patient_id TEXT
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS admissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admission_id TEXT UNIQUE NOT NULL,
                patient_id TEXT NOT NULL,
                bed_no TEXT NOT NULL,
                admission_date TEXT NOT NULL,
                reason TEXT,
                status TEXT DEFAULT 'Admitted'
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS discharges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discharge_id TEXT UNIQUE NOT NULL,
                patient_id TEXT NOT NULL,
                admission_id TEXT,
                discharge_date TEXT NOT NULL,
                remarks TEXT
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id TEXT UNIQUE NOT NULL,
                patient_id TEXT NOT NULL,
                consultation REAL DEFAULT 0,
                room REAL DEFAULT 0,
                medicine REAL DEFAULT 0,
                lab REAL DEFAULT 0,
                other_charges REAL DEFAULT 0,
                total REAL DEFAULT 0,
                paid REAL DEFAULT 0,
                pending REAL DEFAULT 0,
                status TEXT DEFAULT 'Pending',
                bill_date TEXT NOT NULL
            )
        """)

    def seed_data(self):
        self.execute(
            "INSERT OR IGNORE INTO users(username,password,role) VALUES (?,?,?)",
            ("admin", "admin123", "Receptionist")
        )

        doctors = [
            ("D001", "Dr. Arun", "Cardiologist", "Cardiology",
             "Monday, Wednesday, Friday", "10:00 AM - 1:00 PM", 500),
            ("D002", "Dr. Priya", "Dermatologist", "Dermatology",
             "Tuesday, Thursday", "11:00 AM - 2:00 PM", 400),
            ("D003", "Dr. Kumar", "General Physician", "General Medicine",
             "Monday - Saturday", "9:00 AM - 12:00 PM", 300),
        ]
        self.execute("""
            INSERT OR IGNORE INTO doctors
            (doctor_id,name,specialization,department,days,available_time,fee)
            VALUES (?,?,?,?,?,?,?)
        """, doctors, many=True)

        for i in range(1, 11):
            ward = "General Ward" if i <= 6 else "Private Ward"
            bed_type = "General" if i <= 6 else "Private"
            self.execute("""
                INSERT OR IGNORE INTO beds(bed_no,ward,bed_type,status)
                VALUES (?,?,?,'Available')
            """, (f"B{i:02d}", ward, bed_type))


# ----------------------------- MAIN APP -----------------------------

class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1360x800")
        self.root.minsize(1120, 700)
        self.root.configure(bg="#eef5fb")

        self.db = Database()
        self.current_user = None
        self.current_page = None

        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.configure_styles()
        self.show_login()

    # ------------------------- STYLE -------------------------

    def configure_styles(self):
        self.style.configure(
            "Treeview",
            rowheight=34,
            font=("Segoe UI", 9),
            background="white",
            fieldbackground="white"
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI Semibold", 9),
            padding=7
        )
        self.style.configure(
            "TCombobox",
            padding=7,
            font=("Segoe UI", 10)
        )
        self.style.configure(
            "TEntry",
            padding=7,
            font=("Segoe UI", 10)
        )

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ------------------------- LOGO -------------------------

    def create_logo(self, parent, small=False):
        w = 245 if not small else 175
        h = 78 if not small else 58
        canvas = tk.Canvas(parent, width=w, height=h, bg=parent.cget("bg"),
                           highlightthickness=0)
        canvas.pack(side="left", padx=18, pady=5)

        # Heart-like professional logo
        cx = 34 if not small else 25
        cy = 35 if not small else 27
        s = 1 if not small else 0.72

        canvas.create_oval(cx-19*s, cy-17*s, cx+1*s, cy+6*s,
                           fill="#0b6fbf", outline="")
        canvas.create_oval(cx-1*s, cy-17*s, cx+19*s, cy+6*s,
                           fill="#0b6fbf", outline="")
        canvas.create_polygon(
            cx-19*s, cy-4*s, cx+19*s, cy-4*s,
            cx, cy+25*s, fill="#0a87a6", outline=""
        )
        canvas.create_rectangle(
            cx-4*s, cy-13*s, cx+4*s, cy+8*s,
            fill="white", outline=""
        )
        canvas.create_rectangle(
            cx-13*s, cy-4*s, cx+13*s, cy+4*s,
            fill="white", outline=""
        )

        title_size = 22 if not small else 15
        sub_size = 8 if not small else 6

        canvas.create_text(
            62 if not small else 45, 24 if not small else 18,
            text="MediCare", anchor="w",
            font=("Segoe UI Semibold", title_size),
            fill="#08447f"
        )
        canvas.create_text(
            63 if not small else 46, 48 if not small else 36,
            text="H O S P I T A L", anchor="w",
            font=("Segoe UI Semibold", sub_size),
            fill="#0b8fb2"
        )
        canvas.create_line(
            63 if not small else 46, 56 if not small else 42,
            220 if not small else 165, 56 if not small else 42,
            fill="#19a7bb", width=1
        )
        if not small:
            canvas.create_text(
                64, 67, text="Compassion • Care • Better Health",
                anchor="w", font=("Segoe UI", 7), fill="#315b80"
            )
        return canvas

    # ------------------------- LOGIN -------------------------

    def show_login(self):
        self.clear_root()
        self.root.configure(bg="#edf5fb")

        outer = tk.Frame(self.root, bg="#edf5fb")
        outer.pack(fill="both", expand=True)

        top = tk.Frame(outer, bg="#0a5a96", height=110)
        top.pack(fill="x")
        self.create_logo(top)

        tk.Label(
            top, text="Receptionist Portal",
            bg="#0a5a96", fg="white",
            font=("Segoe UI Semibold", 16)
        ).pack(side="right", padx=35, pady=25)

        card = tk.Frame(
            outer, bg="white", bd=1, relief="solid",
            highlightbackground="#d5e4f1", highlightthickness=1
        )
        card.place(relx=0.5, rely=0.53, anchor="center", width=470, height=420)

        tk.Label(
            card, text="Welcome Back",
            bg="white", fg="#0b4b82",
            font=("Segoe UI Semibold", 24)
        ).pack(pady=(38, 5))

        tk.Label(
            card, text="Login to manage hospital reception",
            bg="white", fg="#66809a",
            font=("Segoe UI", 10)
        ).pack(pady=(0, 25))

        form = tk.Frame(card, bg="white")
        form.pack(fill="x", padx=55)

        tk.Label(form, text="Username", bg="white", fg="#123f67",
                 font=("Segoe UI Semibold", 10)).pack(anchor="w")
        self.login_user = ttk.Entry(form)
        self.login_user.pack(fill="x", pady=(6, 18))
        self.login_user.insert(0, "admin")

        tk.Label(form, text="Password", bg="white", fg="#123f67",
                 font=("Segoe UI Semibold", 10)).pack(anchor="w")
        self.login_pass = ttk.Entry(form, show="*")
        self.login_pass.pack(fill="x", pady=(6, 8))
        self.login_pass.insert(0, "admin123")

        tk.Label(
            form, text="Demo login: admin / admin123",
            bg="white", fg="#7b91a5",
            font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(0, 18))

        tk.Button(
            form, text="🔐  Login",
            command=self.login,
            bg="#087ac1", fg="white",
            activebackground="#0569a7", activeforeground="white",
            relief="flat", cursor="hand2",
            font=("Segoe UI Semibold", 11),
            padx=10, pady=11
        ).pack(fill="x")

        self.login_pass.bind("<Return>", lambda e: self.login())
        self.login_user.focus()

    def login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get().strip()

        row = self.db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password), fetch=True
        )
        if row:
            self.current_user = row[0]
            self.show_main()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def logout(self):
        if messagebox.askyesno("Logout", "Do you want to logout?"):
            self.current_user = None
            self.show_login()

    # ------------------------- MAIN LAYOUT -------------------------

    def show_main(self):
        self.clear_root()
        self.root.configure(bg="#eef5fb")

        header = tk.Frame(self.root, bg="#0a67a8", height=82)
        header.pack(fill="x")
        header.pack_propagate(False)

        self.create_logo(header, small=True)

        right = tk.Frame(header, bg="#0a67a8")
        right.pack(side="right", padx=20, fill="y")

        tk.Label(
            right, text="👤  Receptionist",
            bg="#0a67a8", fg="white",
            font=("Segoe UI Semibold", 10)
        ).pack(side="left", padx=15)

        tk.Label(
            right, text=datetime.now().strftime("%d-%m-%Y   %I:%M %p"),
            bg="#0a67a8", fg="white",
            font=("Segoe UI", 9)
        ).pack(side="left", padx=15)

        tk.Button(
            right, text="↪  Logout",
            command=self.logout,
            bg="#0a67a8", fg="white",
            activebackground="#084d80",
            relief="solid", bd=1,
            font=("Segoe UI Semibold", 9),
            cursor="hand2"
        ).pack(side="left", padx=8, pady=17, ipadx=10, ipady=5)

        body = tk.Frame(self.root, bg="#eef5fb")
        body.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(body, bg="#063e6e", width=175)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(body, bg="#eef5fb")
        self.content.pack(side="left", fill="both", expand=True)

        menu = [
            ("⌂", "Dashboard", self.show_dashboard),
            ("●", "Patient Registration", self.show_patient_registration),
            ("👥", "Patient Management", self.show_patient_management),
            ("♟", "Doctor Information", self.show_doctors),
            ("▣", "Appointments", self.show_appointments),
            ("▰", "Admission", self.show_admission),
            ("⇥", "Discharge", self.show_discharge),
            ("₹", "Billing", self.show_billing),
            ("⌕", "Search", self.show_search),
            ("▤", "Reports", self.show_reports),
        ]

        for icon, label, command in menu:
            self.add_menu_button(icon, label, command)

        tk.Frame(self.sidebar, bg="#0e679c", height=1).pack(fill="x", padx=15, pady=7)
        self.add_menu_button("↪", "Logout", self.logout)

        self.show_dashboard()

    def add_menu_button(self, icon, text, command):
        btn = tk.Button(
            self.sidebar,
            text=f"{icon}   {text}",
            command=command,
            anchor="w",
            bg="#063e6e",
            fg="white",
            activebackground="#1387d1",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=14,
            pady=11,
            font=("Segoe UI", 9),
            cursor="hand2"
        )
        btn.pack(fill="x", padx=3, pady=1)
        return btn

    def page_header(self, title, subtitle=""):
        for widget in self.content.winfo_children():
            widget.destroy()

        outer = tk.Frame(self.content, bg="#eef5fb")
        outer.pack(fill="both", expand=True, padx=14, pady=14)

        title_card = tk.Frame(
            outer, bg="white", bd=1, relief="solid",
            highlightbackground="#d8e7f2", highlightthickness=1
        )
        title_card.pack(fill="x", pady=(0, 10))

        tk.Label(
            title_card, text=title,
            bg="white", fg="#0b4b82",
            font=("Segoe UI Semibold", 19)
        ).pack(anchor="w", padx=18, pady=(12, 1))

        if subtitle:
            tk.Label(
                title_card, text=subtitle,
                bg="white", fg="#65819a",
                font=("Segoe UI", 9)
            ).pack(anchor="w", padx=19, pady=(0, 12))

        return outer

    def make_card(self, parent, title=None):
        card = tk.Frame(
            parent, bg="white", bd=1, relief="solid",
            highlightbackground="#d6e5f0", highlightthickness=1
        )
        if title:
            tk.Label(
                card, text=title, bg="white", fg="#0a4c83",
                font=("Segoe UI Semibold", 11)
            ).pack(anchor="w", padx=14, pady=(12, 8))
        return card

    def button(self, parent, text, command, kind="primary"):
        if kind == "danger":
            bg, active = "#dc3545", "#b92b39"
        elif kind == "success":
            bg, active = "#1b9b63", "#137b4e"
        elif kind == "secondary":
            bg, active = "#6c8497", "#526b7e"
        else:
            bg, active = "#087ac1", "#0569a7"

        return tk.Button(
            parent, text=text, command=command,
            bg=bg, fg="white", activebackground=active,
            activeforeground="white", relief="flat",
            cursor="hand2", font=("Segoe UI Semibold", 9),
            padx=13, pady=7
        )

    def entry(self, parent, label, var=None, width=None):
        f = tk.Frame(parent, bg="white")
        tk.Label(
            f, text=label, bg="white", fg="#173f62",
            font=("Segoe UI Semibold", 9)
        ).pack(anchor="w", pady=(0, 4))
        e = ttk.Entry(f, textvariable=var, width=width)
        e.pack(fill="x")
        return f, e

    def combo(self, parent, label, values, var=None):
        f = tk.Frame(parent, bg="white")
        tk.Label(
            f, text=label, bg="white", fg="#173f62",
            font=("Segoe UI Semibold", 9)
        ).pack(anchor="w", pady=(0, 4))
        c = ttk.Combobox(f, values=values, textvariable=var,
                         state="readonly")
        c.pack(fill="x")
        return f, c

    # ------------------------- DASHBOARD -------------------------

    def show_dashboard(self):
        outer = self.page_header(
            "📊 Dashboard",
            "Reception desk overview and today's hospital activity"
        )

        stats = tk.Frame(outer, bg="#eef5fb")
        stats.pack(fill="x", pady=(0, 12))

        queries = [
            ("Total Patients", "SELECT COUNT(*) FROM patients", "#0b76bb"),
            ("Today's Appointments",
             "SELECT COUNT(*) FROM appointments WHERE appointment_date=? AND status='Booked'",
             "#218c6b"),
            ("Available Doctors", "SELECT COUNT(*) FROM doctors", "#7055a6"),
            ("Pending Bills", "SELECT COUNT(*) FROM bills WHERE status='Pending'", "#c77b16"),
            ("Available Beds", "SELECT COUNT(*) FROM beds WHERE status='Available'", "#18758c"),
        ]

        today = date.today().isoformat()

        for i, (label, sql, accent) in enumerate(queries):
            value = self.db.execute(
                sql, (today,) if "?" in sql else (), fetch=True
            )[0][0]

            card = tk.Frame(
                stats, bg="white", bd=1, relief="solid",
                highlightbackground="#d6e5f0", highlightthickness=1
            )
            card.grid(row=0, column=i, sticky="nsew", padx=5)
            stats.columnconfigure(i, weight=1)

            tk.Frame(card, bg=accent, width=6).pack(side="left", fill="y")
            tk.Label(
                card, text=str(value), bg="white", fg="#0b4b82",
                font=("Segoe UI Semibold", 24)
            ).pack(anchor="w", padx=15, pady=(14, 0))
            tk.Label(
                card, text=label, bg="white", fg="#6c8294",
                font=("Segoe UI", 9)
            ).pack(anchor="w", padx=15, pady=(0, 14))

        middle = tk.Frame(outer, bg="#eef5fb")
        middle.pack(fill="both", expand=True)

        # Today's appointments
        ap_card = self.make_card(middle, "📅 Today's Appointments")
        ap_card.pack(side="left", fill="both", expand=True, padx=(0, 6))

        cols = ("ID", "Patient", "Doctor", "Time", "Status")
        tree = ttk.Treeview(ap_card, columns=cols, show="headings", height=9)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=90)
        tree.column("Patient", width=140)
        tree.column("Doctor", width=130)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        rows = self.db.execute("""
            SELECT a.appointment_id, p.name AS patient, d.name AS doctor,
                   a.appointment_time, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id=p.patient_id
            JOIN doctors d ON a.doctor_id=d.doctor_id
            WHERE a.appointment_date=?
            ORDER BY a.appointment_time
        """, (today,), fetch=True)

        for r in rows:
            tree.insert("", "end", values=tuple(r))

        # Quick actions
        q_card = self.make_card(middle, "⚡ Quick Actions")
        q_card.pack(side="left", fill="y", padx=(6, 0), ipadx=8)

        actions = [
            ("👤 Register Patient", self.show_patient_registration),
            ("👨‍⚕️ Add / Update Doctor", self.show_doctors),
            ("📅 Book Appointment", self.show_appointments),
            ("🛏️ Assign Bed", self.show_admission),
            ("💰 Generate Bill", self.show_billing),
            ("📑 View Reports", self.show_reports),
        ]

        for text, cmd in actions:
            self.button(q_card, text, cmd).pack(fill="x", padx=15, pady=6)

    # ------------------------- PATIENT REGISTRATION -------------------------

    def show_patient_registration(self):
        outer = self.page_header(
            "👤 Patient Registration",
            "Register a new patient and save details to SQLite"
        )

        card = self.make_card(outer, "Patient Details")
        card.pack(fill="x", padx=2, pady=2)

        form = tk.Frame(card, bg="white")
        form.pack(fill="x", padx=16, pady=8)

        vars_ = {
            "patient_id": tk.StringVar(value=self.next_id("patients", "patient_id", "P")),
            "name": tk.StringVar(),
            "age": tk.StringVar(),
            "gender": tk.StringVar(value="Male"),
            "phone": tk.StringVar(),
            "blood": tk.StringVar(value="Unknown"),
            "address": tk.StringVar(),
            "emergency": tk.StringVar()
        }

        fields = [
            ("Patient ID", "patient_id"),
            ("Patient Name *", "name"),
            ("Age *", "age"),
            ("Phone", "phone"),
            ("Address", "address"),
            ("Emergency Contact", "emergency"),
        ]

        for idx, (label, key) in enumerate(fields):
            r, c = divmod(idx, 2)
            frame, _ = self.entry(form, label, vars_[key])
            frame.grid(row=r, column=c, sticky="ew", padx=7, pady=7)

        frame, _ = self.combo(form, "Gender *",
                              ["Male", "Female", "Other"], vars_["gender"])
        frame.grid(row=0, column=2, sticky="ew", padx=7, pady=7)

        frame, _ = self.combo(form, "Blood Group",
                              ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                              vars_["blood"])
        frame.grid(row=1, column=2, sticky="ew", padx=7, pady=7)

        for c in range(3):
            form.columnconfigure(c, weight=1)

        actions = tk.Frame(card, bg="white")
        actions.pack(fill="x", padx=23, pady=(8, 18))
        self.button(
            actions, "💾 Save Patient",
            lambda: self.save_patient(vars_)
        ).pack(side="left")
        self.button(
            actions, "Clear",
            lambda: self.show_patient_registration(),
            "secondary"
        ).pack(side="left", padx=8)

        info = self.make_card(outer, "Registration Note")
        info.pack(fill="x", padx=2, pady=10)
        tk.Label(
            info,
            text="Patient ID is generated automatically. All registered details are stored in medicare_hospital.db.",
            bg="white", fg="#61798e", font=("Segoe UI", 9)
        ).pack(anchor="w", padx=16, pady=14)

    def save_patient(self, v):
        name = v["name"].get().strip()
        age = v["age"].get().strip()

        if not name or not age:
            messagebox.showwarning("Required", "Please enter patient name and age.")
            return

        try:
            age_int = int(age)
            if age_int < 0 or age_int > 130:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Age", "Enter a valid age.")
            return

        try:
            self.db.execute("""
                INSERT INTO patients
                (patient_id,name,age,gender,phone,blood_group,address,emergency_contact,registered_on)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                v["patient_id"].get(), name, age_int, v["gender"].get(),
                v["phone"].get().strip(), v["blood"].get(),
                v["address"].get().strip(), v["emergency"].get().strip(),
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))
            messagebox.showinfo(
                "Success",
                f"Patient registered successfully.\nPatient ID: {v['patient_id'].get()}"
            )
            self.show_patient_management()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Patient ID already exists.")

    # ------------------------- PATIENT MANAGEMENT -------------------------

    def show_patient_management(self):
        outer = self.page_header(
            "👥 Patient Management",
            "View, search and edit registered patients"
        )

        top = tk.Frame(outer, bg="#eef5fb")
        top.pack(fill="x", pady=(0, 8))

        search_var = tk.StringVar()
        tk.Label(top, text="Search Patient:", bg="#eef5fb",
                 fg="#173f62", font=("Segoe UI Semibold", 9)).pack(side="left")
        search = ttk.Entry(top, textvariable=search_var, width=35)
        search.pack(side="left", padx=8)
        self.button(top, "🔎 Search",
                    lambda: load(search_var.get().strip())).pack(side="left")
        self.button(top, "Refresh",
                    lambda: load(""), "secondary").pack(side="left", padx=7)

        card = self.make_card(outer)
        card.pack(fill="both", expand=True)

        cols = ("Patient ID", "Name", "Age", "Gender", "Phone", "Blood Group",
                "Address", "Emergency", "Registered")
        tree = ttk.Treeview(card, columns=cols, show="headings")
        widths = [90, 145, 50, 75, 105, 90, 180, 120, 125]
        for c, w in zip(cols, widths):
            tree.heading(c, text=c)
            tree.column(c, width=w, minwidth=60)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def load(term=""):
            for item in tree.get_children():
                tree.delete(item)
            if term:
                rows = self.db.execute("""
                    SELECT patient_id,name,age,gender,phone,blood_group,address,
                           emergency_contact,registered_on
                    FROM patients
                    WHERE patient_id LIKE ? OR name LIKE ? OR phone LIKE ?
                    ORDER BY id DESC
                """, (f"%{term}%", f"%{term}%", f"%{term}%"), fetch=True)
            else:
                rows = self.db.execute("""
                    SELECT patient_id,name,age,gender,phone,blood_group,address,
                           emergency_contact,registered_on
                    FROM patients ORDER BY id DESC
                """, fetch=True)
            for r in rows:
                tree.insert("", "end", values=tuple(r))

        actions = tk.Frame(card, bg="white")
        actions.pack(fill="x", padx=10, pady=(0, 10))

        def edit():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select", "Select a patient to edit.")
                return
            patient_id = tree.item(selected[0])["values"][0]
            self.edit_patient(patient_id)

        self.button(actions, "✏ Edit Patient", edit).pack(side="left")
        self.button(actions, "🔄 Refresh", lambda: load(""), "secondary").pack(side="left", padx=7)

        load()

    def edit_patient(self, patient_id):
        rows = self.db.execute(
            "SELECT * FROM patients WHERE patient_id=?", (patient_id,), fetch=True
        )
        if not rows:
            return
        p = rows[0]

        win = tk.Toplevel(self.root)
        win.title("Update Patient")
        win.geometry("520x560")
        win.configure(bg="white")
        win.transient(self.root)
        win.grab_set()

        tk.Label(
            win, text="Update Patient Information",
            bg="white", fg="#0b4b82",
            font=("Segoe UI Semibold", 18)
        ).pack(anchor="w", padx=25, pady=(22, 18))

        form = tk.Frame(win, bg="white")
        form.pack(fill="x", padx=25)

        vars_ = {
            "name": tk.StringVar(value=p["name"]),
            "age": tk.StringVar(value=p["age"]),
            "gender": tk.StringVar(value=p["gender"]),
            "phone": tk.StringVar(value=p["phone"] or ""),
            "blood": tk.StringVar(value=p["blood_group"] or "Unknown"),
            "address": tk.StringVar(value=p["address"] or ""),
            "emergency": tk.StringVar(value=p["emergency_contact"] or "")
        }

        fields = [
            ("Name *", "name"), ("Age *", "age"), ("Phone", "phone"),
            ("Address", "address"), ("Emergency Contact", "emergency")
        ]
        for i, (label, key) in enumerate(fields):
            f, _ = self.entry(form, label, vars_[key])
            f.pack(fill="x", pady=5)

        f, _ = self.combo(form, "Gender", ["Male", "Female", "Other"], vars_["gender"])
        f.pack(fill="x", pady=5)
        f, _ = self.combo(form, "Blood Group",
                          ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                          vars_["blood"])
        f.pack(fill="x", pady=5)

        def update():
            try:
                age = int(vars_["age"].get())
            except ValueError:
                messagebox.showwarning("Invalid", "Enter a valid age.", parent=win)
                return
            if not vars_["name"].get().strip():
                messagebox.showwarning("Required", "Name is required.", parent=win)
                return

            self.db.execute("""
                UPDATE patients
                SET name=?, age=?, gender=?, phone=?, blood_group=?,
                    address=?, emergency_contact=?
                WHERE patient_id=?
            """, (
                vars_["name"].get().strip(), age, vars_["gender"].get(),
                vars_["phone"].get().strip(), vars_["blood"].get(),
                vars_["address"].get().strip(), vars_["emergency"].get().strip(),
                patient_id
            ))
            messagebox.showinfo("Updated", "Patient updated successfully.", parent=win)
            win.destroy()
            self.show_patient_management()

        actions = tk.Frame(win, bg="white")
        actions.pack(fill="x", padx=25, pady=20)
        self.button(actions, "💾 Update", update).pack(side="left")
        self.button(actions, "Cancel", win.destroy, "secondary").pack(side="left", padx=8)

    # ------------------------- DOCTORS -------------------------

    def show_doctors(self):
        outer = self.page_header(
            "👨‍⚕️ Doctor Information",
            "View, add and update doctor details"
        )

        top = tk.Frame(outer, bg="#eef5fb")
        top.pack(fill="x", pady=(0, 8))
        self.button(top, "＋ Add New Doctor",
                    self.add_doctor).pack(side="right")

        card = self.make_card(outer)
        card.pack(fill="both", expand=True)

        cols = ("ID", "Doctor Name", "Specialization", "Department",
                "Days", "Time", "Fee (₹)", "Action")
        tree = ttk.Treeview(card, columns=cols, show="headings")
        widths = [65, 125, 130, 130, 170, 135, 75, 120]
        for c, w in zip(cols, widths):
            tree.heading(c, text=c)
            tree.column(c, width=w, minwidth=55)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        rows = self.db.execute("SELECT * FROM doctors ORDER BY doctor_id", fetch=True)
        for r in rows:
            tree.insert(
                "", "end",
                values=(r["doctor_id"], r["name"], r["specialization"],
                        r["department"], r["days"], r["available_time"],
                        f"{r['fee']:.0f}", "Edit / Delete")
            )

        actions = tk.Frame(card, bg="white")
        actions.pack(fill="x", padx=10, pady=(0, 10))

        def edit():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select", "Select a doctor.")
                return
            doctor_id = tree.item(selected[0])["values"][0]
            self.update_doctor(doctor_id)

        def delete():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select", "Select a doctor.")
                return
            doctor_id = tree.item(selected[0])["values"][0]
            if messagebox.askyesno("Delete Doctor",
                                   f"Delete doctor {doctor_id}?"):
                self.db.execute("DELETE FROM doctors WHERE doctor_id=?", (doctor_id,))
                self.show_doctors()

        self.button(actions, "✏ Update Doctor", edit).pack(side="left")
        self.button(actions, "🗑 Delete Doctor", delete, "danger").pack(side="left", padx=7)

    def add_doctor(self):
        self.doctor_form("Add New Doctor")

    def update_doctor(self, doctor_id):
        rows = self.db.execute(
            "SELECT * FROM doctors WHERE doctor_id=?", (doctor_id,), fetch=True
        )
        if rows:
            self.doctor_form("Update Doctor Information", rows[0])

    def doctor_form(self, title, doctor=None):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("600x600")
        win.configure(bg="white")
        win.transient(self.root)
        win.grab_set()

        tk.Label(
            win, text="👨‍⚕️  " + title,
            bg="white", fg="#0b4b82",
            font=("Segoe UI Semibold", 18)
        ).pack(anchor="w", padx=25, pady=(20, 18))

        form = tk.Frame(win, bg="white")
        form.pack(fill="x", padx=25)

        vals = {
            "id": tk.StringVar(value=doctor["doctor_id"] if doctor else self.next_id("doctors", "doctor_id", "D")),
            "name": tk.StringVar(value=doctor["name"] if doctor else ""),
            "spec": tk.StringVar(value=doctor["specialization"] if doctor else "General Physician"),
            "dept": tk.StringVar(value=doctor["department"] if doctor else "General Medicine"),
            "days": tk.StringVar(value=doctor["days"] if doctor else "Monday - Saturday"),
            "time": tk.StringVar(value=doctor["available_time"] if doctor else "9:00 AM - 12:00 PM"),
            "fee": tk.StringVar(value=str(doctor["fee"]) if doctor else "300")
        }

        f, _ = self.entry(form, "Doctor ID *", vals["id"])
        f.pack(fill="x", pady=5)
        if doctor:
            # IDs are kept stable after creation.
            for child in f.winfo_children():
                if isinstance(child, ttk.Entry):
                    child.configure(state="disabled")

        f, _ = self.entry(form, "Doctor Name *", vals["name"])
        f.pack(fill="x", pady=5)
        f, _ = self.combo(form, "Specialization *",
                          ["General Physician", "Cardiologist", "Dermatologist",
                           "Pediatrician", "Neurologist", "Orthopedic", "ENT Specialist"],
                          vals["spec"])
        f.pack(fill="x", pady=5)
        f, _ = self.combo(form, "Department *",
                          ["General Medicine", "Cardiology", "Dermatology",
                           "Pediatrics", "Neurology", "Orthopedics", "ENT"],
                          vals["dept"])
        f.pack(fill="x", pady=5)
        f, _ = self.entry(form, "Available Days *", vals["days"])
        f.pack(fill="x", pady=5)
        f, _ = self.entry(form, "Available Time *", vals["time"])
        f.pack(fill="x", pady=5)
        f, _ = self.entry(form, "Consultation Fee (₹)", vals["fee"])
        f.pack(fill="x", pady=5)

        def save():
            try:
                fee = float(vals["fee"].get())
                if fee < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid", "Enter a valid consultation fee.", parent=win)
                return

            required = [vals["id"].get().strip(), vals["name"].get().strip(),
                        vals["spec"].get().strip(), vals["dept"].get().strip(),
                        vals["days"].get().strip(), vals["time"].get().strip()]
            if not all(required):
                messagebox.showwarning("Required", "Please fill all required fields.", parent=win)
                return

            try:
                if doctor:
                    self.db.execute("""
                        UPDATE doctors
                        SET name=?, specialization=?, department=?,
                            days=?, available_time=?, fee=?
                        WHERE doctor_id=?
                    """, (
                        vals["name"].get().strip(), vals["spec"].get(),
                        vals["dept"].get(), vals["days"].get().strip(),
                        vals["time"].get().strip(), fee, doctor["doctor_id"]
                    ))
                    msg = "Doctor Updated Successfully!"
                else:
                    self.db.execute("""
                        INSERT INTO doctors
                        (doctor_id,name,specialization,department,days,available_time,fee)
                        VALUES (?,?,?,?,?,?,?)
                    """, (
                        vals["id"].get().strip(), vals["name"].get().strip(),
                        vals["spec"].get(), vals["dept"].get(),
                        vals["days"].get().strip(), vals["time"].get().strip(), fee
                    ))
                    msg = "Doctor Added Successfully!"

                messagebox.showinfo("Success", msg, parent=win)
                win.destroy()
                self.show_doctors()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Doctor ID already exists.", parent=win)

        actions = tk.Frame(win, bg="white")
        actions.pack(fill="x", padx=25, pady=20)
        self.button(actions, "💾 Save / Update", save).pack(side="left")
        self.button(actions, "Cancel", win.destroy, "secondary").pack(side="left", padx=8)

    # ------------------------- APPOINTMENTS -------------------------

    def show_appointments(self):
        outer = self.page_header(
            "📅 Appointments",
            "Book, reschedule and cancel patient appointments"
        )

        card = self.make_card(outer, "Appointment Booking")
        card.pack(fill="x", padx=2, pady=(0, 10))

        form = tk.Frame(card, bg="white")
        form.pack(fill="x", padx=16, pady=8)

        pv = tk.StringVar()
        dv = tk.StringVar()
        av = tk.StringVar(value=date.today().isoformat())
        tv = tk.StringVar(value="10:00 AM")
        notes = tk.StringVar()

        f, pe = self.entry(form, "Patient ID *", pv)
        f.grid(row=0, column=0, sticky="ew", padx=7, pady=7)
        f, de = self.combo(
            form, "Doctor *",
            [f"{r['doctor_id']} - {r['name']}" for r in
             self.db.execute("SELECT doctor_id,name FROM doctors ORDER BY doctor_id", fetch=True)],
            dv
        )
        f.grid(row=0, column=1, sticky="ew", padx=7, pady=7)
        f, _ = self.entry(form, "Date (YYYY-MM-DD) *", av)
        f.grid(row=1, column=0, sticky="ew", padx=7, pady=7)
        f, _ = self.combo(form, "Time",
                          ["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
                           "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",
                           "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM"],
                          tv)
        f.grid(row=1, column=1, sticky="ew", padx=7, pady=7)
        f, _ = self.entry(form, "Notes", notes)
        f.grid(row=2, column=0, columnspan=2, sticky="ew", padx=7, pady=7)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        def book():
            patient_id = pv.get().strip()
            doctor = dv.get().strip()
            if not patient_id or not doctor:
                messagebox.showwarning("Required", "Patient and doctor are required.")
                return

            p = self.db.execute(
                "SELECT name FROM patients WHERE patient_id=?", (patient_id,), fetch=True
            )
            if not p:
                messagebox.showwarning("Not Found", "Patient ID not found.")
                return

            doctor_id = doctor.split(" - ")[0]
            try:
                datetime.strptime(av.get().strip(), "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Invalid Date", "Use YYYY-MM-DD.")
                return

            self.db.execute("""
                INSERT INTO appointments
                (appointment_id,patient_id,doctor_id,appointment_date,appointment_time,status,notes)
                VALUES (?,?,?,?,?,?,?)
            """, (
                self.next_id("appointments", "appointment_id", "A"),
                patient_id, doctor_id, av.get().strip(), tv.get(),
                "Booked", notes.get().strip()
            ))
            messagebox.showinfo("Booked", "Appointment booked successfully.")
            self.show_appointments()

        self.button(form, "📅 Book Appointment", book).grid(
            row=3, column=0, sticky="w", padx=7, pady=10
        )

        list_card = self.make_card(outer, "Appointment List")
        list_card.pack(fill="both", expand=True)

        cols = ("ID", "Patient", "Doctor", "Date", "Time", "Status", "Notes")
        tree = ttk.Treeview(list_card, columns=cols, show="headings")
        widths = [75, 90, 105, 100, 90, 85, 180]
        for c, w in zip(cols, widths):
            tree.heading(c, text=c)
            tree.column(c, width=w)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def load():
            for x in tree.get_children():
                tree.delete(x)
            rows = self.db.execute("""
                SELECT a.appointment_id,a.patient_id,d.name,a.appointment_date,
                       a.appointment_time,a.status,a.notes
                FROM appointments a
                JOIN doctors d ON a.doctor_id=d.doctor_id
                ORDER BY a.appointment_date DESC, a.appointment_time
            """, fetch=True)
            for r in rows:
                tree.insert("", "end", values=tuple(r))

        actions = tk.Frame(list_card, bg="white")
        actions.pack(fill="x", padx=10, pady=(0, 10))

        def change_status(status):
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select", "Select an appointment.")
                return
            appt_id = tree.item(selected[0])["values"][0]
            self.db.execute(
                "UPDATE appointments SET status=? WHERE appointment_id=?",
                (status, appt_id)
            )
            load()

        def reschedule():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select", "Select an appointment.")
                return
            vals = tree.item(selected[0])["values"]
            self.reschedule_appointment(vals[0], vals[3], vals[4])

        self.button(actions, "✏ Reschedule", reschedule).pack(side="left")
        self.button(actions, "✓ Mark Completed",
                    lambda: change_status("Completed"), "success").pack(side="left", padx=7)
        self.button(actions, "✕ Cancel",
                    lambda: change_status("Cancelled"), "danger").pack(side="left")
        load()

    def reschedule_appointment(self, appt_id, old_date, old_time):
        win = tk.Toplevel(self.root)
        win.title("Reschedule Appointment")
        win.geometry("400x270")
        win.configure(bg="white")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="Reschedule Appointment",
                 bg="white", fg="#0b4b82",
                 font=("Segoe UI Semibold", 17)).pack(pady=(25, 18))

        date_v = tk.StringVar(value=old_date)
        time_v = tk.StringVar(value=old_time)

        f, _ = self.entry(win, "New Date (YYYY-MM-DD)", date_v)
        f.pack(fill="x", padx=30, pady=6)
        f, _ = self.combo(win, "New Time",
                          ["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
                           "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",
                           "01:00 PM", "01:30 PM", "02:00 PM"], time_v)
        f.pack(fill="x", padx=30, pady=6)

        def save():
            try:
                datetime.strptime(date_v.get().strip(), "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Invalid", "Use YYYY-MM-DD.", parent=win)
                return
            self.db.execute("""
                UPDATE appointments
                SET appointment_date=?, appointment_time=?, status='Booked'
                WHERE appointment_id=?
            """, (date_v.get().strip(), time_v.get(), appt_id))
            messagebox.showinfo("Updated", "Appointment rescheduled.", parent=win)
            win.destroy()
            self.show_appointments()

        self.button(win, "💾 Update Appointment", save).pack(pady=16)

    # ------------------------- ADMISSION -------------------------

    def show_admission(self):
        outer = self.page_header(
            "🛏️ Admission & Bed Assignment",
            "Assign available beds to admitted patients"
        )

        card = self.make_card(outer, "New Admission")
        card.pack(fill="x", padx=2, pady=(0, 10))

        form = tk.Frame(card, bg="white")
        form.pack(fill="x", padx=16, pady=8)

        pv = tk.StringVar()
        bedv = tk.StringVar()
        reason = tk.StringVar()

        f, _ = self.entry(form, "Patient ID *", pv)
        f.grid(row=0, column=0, sticky="ew", padx=7, pady=7)

        beds = self.db.execute(
            "SELECT bed_no,ward,bed_type FROM beds WHERE status='Available' ORDER BY bed_no",
            fetch=True
        )
        bed_values = [f"{b['bed_no']} - {b['ward']} ({b['bed_type']})" for b in beds]

        f, _ = self.combo(form, "Available Bed *", bed_values, bedv)
        f.grid(row=0, column=1, sticky="ew", padx=7, pady=7)
        f, _ = self.entry(form, "Reason / Diagnosis", reason)
        f.grid(row=1, column=0, columnspan=2, sticky="ew", padx=7, pady=7)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        def admit():
            patient_id = pv.get().strip()
            bed = bedv.get().strip()
            if not patient_id or not bed:
                messagebox.showwarning("Required", "Patient ID and bed are required.")
                return

            if not self.db.execute(
                "SELECT 1 FROM patients WHERE patient_id=?", (patient_id,), fetch=True
            ):
                messagebox.showwarning("Not Found", "Patient ID not found.")
                return

            bed_no = bed.split(" - ")[0]
            admission_id = self.next_id("admissions", "admission_id", "ADM")

            self.db.execute("""
                INSERT INTO admissions
                (admission_id,patient_id,bed_no,admission_date,reason,status)
                VALUES (?,?,?,?,?,'Admitted')
            """, (
                admission_id, patient_id, bed_no,
                date.today().isoformat(), reason.get().strip()
            ))
            self.db.execute(
                "UPDATE beds SET status='Occupied', patient_id=? WHERE bed_no=?",
                (patient_id, bed_no)
            )
            messagebox.showinfo("Success",
                                f"Patient admitted successfully.\nBed: {bed_no}")
            self.show_admission()

        self.button(form, "🛏️ Assign Bed & Admit", admit).grid(
            row=2, column=0, sticky="w", padx=7, pady=10
        )

        list_card = self.make_card(outer, "Current Admissions")
        list_card.pack(fill="both", expand=True)

        cols = ("Admission ID", "Patient ID", "Bed", "Admission Date", "Reason", "Status")
        tree = ttk.Treeview(list_card, columns=cols, show="headings")
        for c, w in zip(cols, [110, 90, 75, 120, 230, 90]):
            tree.heading(c, text=c)
            tree.column(c, width=w)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        rows = self.db.execute("""
            SELECT admission_id,patient_id,bed_no,admission_date,reason,status
            FROM admissions WHERE status='Admitted'
            ORDER BY id DESC
        """, fetch=True)
        for r in rows:
            tree.insert("", "end", values=tuple(r))

    # ------------------------- DISCHARGE -------------------------

    def show_discharge(self):
        outer = self.page_header(
            "🚪 Discharge",
            "Discharge admitted patients and release occupied beds"
        )

        card = self.make_card(outer, "Discharge Patient")
        card.pack(fill="x", padx=2, pady=(0, 10))

        form = tk.Frame(card, bg="white")
        form.pack(fill="x", padx=16, pady=8)

        pv = tk.StringVar()
        remarks = tk.StringVar()

        f, _ = self.entry(form, "Patient ID *", pv)
        f.grid(row=0, column=0, sticky="ew", padx=7, pady=7)
        f, _ = self.entry(form, "Discharge Remarks", remarks)
        f.grid(row=0, column=1, sticky="ew", padx=7, pady=7)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        def discharge():
            patient_id = pv.get().strip()
            rows = self.db.execute("""
                SELECT admission_id,bed_no FROM admissions
                WHERE patient_id=? AND status='Admitted'
                ORDER BY id DESC LIMIT 1
            """, (patient_id,), fetch=True)

            if not rows:
                messagebox.showwarning(
                    "Not Found",
                    "No active admission found for this patient."
                )
                return

            adm = rows[0]
            did = self.next_id("discharges", "discharge_id", "DIS")

            self.db.execute("""
                INSERT INTO discharges
                (discharge_id,patient_id,admission_id,discharge_date,remarks)
                VALUES (?,?,?,?,?)
            """, (
                did, patient_id, adm["admission_id"],
                date.today().isoformat(), remarks.get().strip()
            ))
            self.db.execute(
                "UPDATE admissions SET status='Discharged' WHERE admission_id=?",
                (adm["admission_id"],)
            )
            self.db.execute("""
                UPDATE beds SET status='Available', patient_id=NULL
                WHERE bed_no=?
            """, (adm["bed_no"],))

            messagebox.showinfo(
                "Discharged",
                f"Patient discharged successfully.\nBed {adm['bed_no']} is now available."
            )
            self.show_discharge()

        self.button(form, "🚪 Discharge Patient", discharge,
                    "success").grid(row=1, column=0, sticky="w", padx=7, pady=10)

        list_card = self.make_card(outer, "Discharge History")
        list_card.pack(fill="both", expand=True)

        cols = ("Discharge ID", "Patient ID", "Admission ID", "Date", "Remarks")
        tree = ttk.Treeview(list_card, columns=cols, show="headings")
        for c, w in zip(cols, [100, 90, 110, 110, 300]):
            tree.heading(c, text=c)
            tree.column(c, width=w)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        rows = self.db.execute("""
            SELECT discharge_id,patient_id,admission_id,discharge_date,remarks
            FROM discharges ORDER BY id DESC
        """, fetch=True)
        for r in rows:
            tree.insert("", "end", values=tuple(r))

    # ------------------------- BILLING -------------------------

    def show_billing(self):
        outer = self.page_header(
            "💰 Billing",
            "Create patient bills, calculate pending amount and print bills"
        )

        card = self.make_card(outer, "Bill Details")
        card.pack(fill="x", padx=2, pady=(0, 10))

        form = tk.Frame(card, bg="white")
        form.pack(fill="x", padx=16, pady=8)

        pid = tk.StringVar()
        pname = tk.StringVar()
        consultation = tk.StringVar(value="0")
        room = tk.StringVar(value="0")
        medicine = tk.StringVar(value="0")
        lab = tk.StringVar(value="0")
        other = tk.StringVar(value="0")
        paid = tk.StringVar(value="0")
        total_v = tk.StringVar(value="₹ 0.00")
        pending_v = tk.StringVar(value="₹ 0.00")
        status_v = tk.StringVar(value="Pending")

        f, _ = self.entry(form, "Patient ID *", pid)
        f.grid(row=0, column=0, sticky="ew", padx=7, pady=7)

        patient_info = tk.Frame(form, bg="#f2f8fd", bd=1, relief="solid")
        patient_info.grid(row=0, column=1, sticky="nsew", padx=7, pady=7)
        tk.Label(patient_info, text="Patient Name",
                 bg="#f2f8fd", fg="#4e6d85",
                 font=("Segoe UI Semibold", 8)).grid(row=0, column=0, sticky="w", padx=10, pady=(7, 0))
        tk.Label(patient_info, textvariable=pname,
                 bg="#f2f8fd", fg="#123f67",
                 font=("Segoe UI Semibold", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 7))

        def lookup_patient():
            rows = self.db.execute(
                "SELECT name FROM patients WHERE patient_id=?", (pid.get().strip(),),
                fetch=True
            )
            if rows:
                pname.set(rows[0]["name"])
            else:
                pname.set("")
                messagebox.showwarning("Not Found", "Patient ID not found.")

        self.button(form, "🔎", lookup_patient).grid(
            row=0, column=2, padx=7, pady=7
        )

        billing_fields = [
            ("Consultation Fee (₹)", consultation),
            ("Room Charges (₹)", room),
            ("Medicine Charges (₹)", medicine),
            ("Lab Charges (₹)", lab),
            ("Other Charges (₹)", other),
            ("Paid Amount (₹)", paid),
        ]

        for i, (label, var) in enumerate(billing_fields):
            r = 1 + i // 2
            c = i % 2
            f, _ = self.entry(form, label, var)
            f.grid(row=r, column=c, sticky="ew", padx=7, pady=7)

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        def calculate(*_):
            try:
                values = [float(x.get() or 0) for x in
                          [consultation, room, medicine, lab, other]]
                paid_amt = float(paid.get() or 0)
                if any(v < 0 for v in values) or paid_amt < 0:
                    raise ValueError
            except ValueError:
                total_v.set("Invalid")
                pending_v.set("Invalid")
                return

            total = sum(values)
            pending = max(total - paid_amt, 0)
            status_v.set("Paid" if pending == 0 else "Pending")
            total_v.set(f"₹ {total:,.2f}")
            pending_v.set(f"₹ {pending:,.2f}")

        for var in [consultation, room, medicine, lab, other, paid]:
            var.trace_add("write", calculate)

        summary = tk.Frame(card, bg="#edf7fd", bd=1, relief="solid")
        summary.pack(fill="x", padx=23, pady=10)

        rows = [
            ("Total Amount", total_v),
            ("Paid Amount", paid),
            ("Pending Amount", pending_v),
            ("Status", status_v)
        ]
        for i, (label, var) in enumerate(rows):
            tk.Label(summary, text=label, bg="#edf7fd",
                     fg="#174c78", font=("Segoe UI Semibold", 9)).grid(
                         row=i, column=0, sticky="w", padx=14, pady=5
                     )
            tk.Label(summary, textvariable=var, bg="#edf7fd",
                     fg="#174c78", font=("Segoe UI Semibold", 10)).grid(
                         row=i, column=1, sticky="w", padx=14, pady=5
                     )

        actions = tk.Frame(card, bg="white")
        actions.pack(fill="x", padx=23, pady=(3, 18))

        def generate():
            patient_id = pid.get().strip()
            if not patient_id:
                messagebox.showwarning("Required", "Enter Patient ID.")
                return

            patient = self.db.execute(
                "SELECT * FROM patients WHERE patient_id=?", (patient_id,), fetch=True
            )
            if not patient:
                messagebox.showwarning("Not Found", "Patient ID not found.")
                return

            try:
                cons, room_amt, med, lab_amt, other_amt, paid_amt = [
                    float(v.get() or 0) for v in
                    [consultation, room, medicine, lab, other, paid]
                ]
                if min(cons, room_amt, med, lab_amt, other_amt, paid_amt) < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid", "Enter valid non-negative amounts.")
                return

            total = cons + room_amt + med + lab_amt + other_amt
            pending = max(total - paid_amt, 0)
            status = "Paid" if pending == 0 else "Pending"
            bill_id = self.next_id("bills", "bill_id", "B")

            self.db.execute("""
                INSERT INTO bills
                (bill_id,patient_id,consultation,room,medicine,lab,other_charges,
                 total,paid,pending,status,bill_date)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                bill_id, patient_id, cons, room_amt, med, lab_amt, other_amt,
                total, paid_amt, pending, status,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))

            self.generate_printable_bill(
                bill_id, patient[0], cons, room_amt, med, lab_amt,
                other_amt, total, paid_amt, pending, status
            )
            messagebox.showinfo(
                "Bill Generated Successfully",
                f"Bill ID: {bill_id}\n"
                f"Total Amount: ₹ {total:,.2f}\n"
                f"Paid Amount: ₹ {paid_amt:,.2f}\n"
                f"Pending Amount: ₹ {pending:,.2f}\n"
                f"Status: {status}\n\n"
                "The printable bill has been opened in your browser."
            )
            self.show_billing()

        self.button(actions, "🧾 Generate Bill + Print", generate).pack(side="left")

        recent = self.make_card(outer, "Recent Bills")
        recent.pack(fill="both", expand=True)

        cols = ("Bill ID", "Patient ID", "Patient Name",
                "Total", "Paid", "Pending", "Status", "Date")
        tree = ttk.Treeview(recent, columns=cols, show="headings")
        for c, w in zip(cols, [80, 80, 130, 95, 90, 95, 85, 130]):
            tree.heading(c, text=c)
            tree.column(c, width=w)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        rows = self.db.execute("""
            SELECT b.bill_id,b.patient_id,p.name,b.total,b.paid,b.pending,
                   b.status,b.bill_date
            FROM bills b JOIN patients p ON b.patient_id=p.patient_id
            ORDER BY b.id DESC LIMIT 20
        """, fetch=True)
        for r in rows:
            tree.insert("", "end", values=(
                r["bill_id"], r["patient_id"], r["name"],
                f"₹ {r['total']:,.2f}", f"₹ {r['paid']:,.2f}",
                f"₹ {r['pending']:,.2f}", r["status"], r["bill_date"]
            ))

        calculate()

    def generate_printable_bill(self, bill_id, patient, consultation,
                                room, medicine, lab, other, total,
                                paid, pending, status):
        safe = lambda x: str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        filename = os.path.abspath(f"{bill_id}_printable_bill.html")

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{safe(bill_id)} - MediCare Hospital</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 35px; color: #163b5c; }}
.header {{ border-bottom: 3px solid #087ac1; padding-bottom: 12px; }}
.logo {{ color: #087ac1; font-size: 30px; font-weight: bold; }}
.tag {{ color: #55758f; }}
h2 {{ color: #0b4b82; }}
.info {{ background:#f1f8fd; padding:14px; margin-top:18px; }}
table {{ width:100%; border-collapse:collapse; margin-top:18px; }}
th, td {{ border:1px solid #c8dce9; padding:10px; text-align:left; }}
th {{ background:#e8f4fb; }}
.amount {{ text-align:right; }}
.total {{ font-weight:bold; font-size:18px; }}
.status {{ font-weight:bold; }}
.footer {{ margin-top:35px; color:#688196; font-size:12px; }}
.print {{ margin-bottom:20px; padding:10px 18px; background:#087ac1; color:white;
          border:0; cursor:pointer; }}
@media print {{ .print {{ display:none; }} body {{ margin:15px; }} }}
</style>
</head>
<body>
<button class="print" onclick="window.print()">🖨 Print Bill</button>
<div class="header">
  <div class="logo">♥ MediCare Hospital</div>
  <div class="tag">Compassion • Care • Better Health</div>
</div>
<h2>Patient Bill</h2>
<div class="info">
<b>Bill ID:</b> {safe(bill_id)}<br>
<b>Date:</b> {safe(datetime.now().strftime("%d-%m-%Y %I:%M %p"))}<br>
<b>Patient ID:</b> {safe(patient["patient_id"])}<br>
<b>Patient Name:</b> {safe(patient["name"])}<br>
<b>Age:</b> {safe(patient["age"])} &nbsp;&nbsp;
<b>Gender:</b> {safe(patient["gender"])}<br>
<b>Phone:</b> {safe(patient["phone"] or "")}
</div>
<table>
<tr><th>Particular</th><th class="amount">Amount (₹)</th></tr>
<tr><td>Consultation Fee</td><td class="amount">{consultation:,.2f}</td></tr>
<tr><td>Room Charges</td><td class="amount">{room:,.2f}</td></tr>
<tr><td>Medicine Charges</td><td class="amount">{medicine:,.2f}</td></tr>
<tr><td>Lab Charges</td><td class="amount">{lab:,.2f}</td></tr>
<tr><td>Other Charges</td><td class="amount">{other:,.2f}</td></tr>
<tr class="total"><td>Total Amount</td><td class="amount">{total:,.2f}</td></tr>
<tr><td>Paid Amount</td><td class="amount">{paid:,.2f}</td></tr>
<tr><td>Pending Amount</td><td class="amount">{pending:,.2f}</td></tr>
<tr><td class="status">Status</td><td class="status">{safe(status)}</td></tr>
</table>
<div class="footer">
Thank you for choosing MediCare Hospital.<br>
This is a computer-generated bill.
</div>
</body>
</html>"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open("file://" + filename)

    # ------------------------- SEARCH -------------------------

    def show_search(self):
        outer = self.page_header(
            "🔎 Search",
            "Search patients, doctors, appointments and bills from one screen"
        )

        top = tk.Frame(outer, bg="#eef5fb")
        top.pack(fill="x", pady=(0, 10))

        q = tk.StringVar()
        ttk.Entry(top, textvariable=q).pack(side="left", fill="x", expand=True)
        self.button(top, "🔎 Search All",
                    lambda: search_all(q.get().strip())).pack(side="left", padx=8)

        card = self.make_card(outer, "Search Results")
        card.pack(fill="both", expand=True)

        result = ttk.Treeview(
            card, columns=("Type", "ID", "Name / Patient", "Details", "Status"),
            show="headings"
        )
        for c, w in zip(("Type", "ID", "Name / Patient", "Details", "Status"),
                        [110, 100, 180, 330, 110]):
            result.heading(c, text=c)
            result.column(c, width=w)
        result.pack(fill="both", expand=True, padx=10, pady=10)

        def search_all(term):
            for x in result.get_children():
                result.delete(x)
            if not term:
                return

            patients = self.db.execute("""
                SELECT patient_id,name,phone,gender FROM patients
                WHERE patient_id LIKE ? OR name LIKE ? OR phone LIKE ?
            """, (f"%{term}%", f"%{term}%", f"%{term}%"), fetch=True)

            for p in patients:
                result.insert("", "end", values=(
                    "Patient", p["patient_id"], p["name"],
                    f"Phone: {p['phone'] or '-'} | Gender: {p['gender']}", "-"
                ))

            doctors = self.db.execute("""
                SELECT doctor_id,name,specialization,department FROM doctors
                WHERE doctor_id LIKE ? OR name LIKE ? OR specialization LIKE ?
                   OR department LIKE ?
            """, (f"%{term}%", f"%{term}%", f"%{term}%", f"%{term}%"), fetch=True)

            for d in doctors:
                result.insert("", "end", values=(
                    "Doctor", d["doctor_id"], d["name"],
                    f"{d['specialization']} | {d['department']}", "-"
                ))

            bills = self.db.execute("""
                SELECT b.bill_id,b.patient_id,p.name,b.total,b.status
                FROM bills b JOIN patients p ON b.patient_id=p.patient_id
                WHERE b.bill_id LIKE ? OR b.patient_id LIKE ? OR p.name LIKE ?
            """, (f"%{term}%", f"%{term}%", f"%{term}%"), fetch=True)

            for b in bills:
                result.insert("", "end", values=(
                    "Bill", b["bill_id"], b["name"],
                    f"Patient ID: {b['patient_id']} | Total: ₹ {b['total']:,.2f}",
                    b["status"]
                ))

    # ------------------------- REPORTS -------------------------

    def show_reports(self):
        outer = self.page_header(
            "📑 Reports",
            "Hospital statistics and printable report summaries"
        )

        grid = tk.Frame(outer, bg="#eef5fb")
        grid.pack(fill="x", pady=4)

        stats = [
            ("Patients", "SELECT COUNT(*) FROM patients"),
            ("Doctors", "SELECT COUNT(*) FROM doctors"),
            ("Appointments", "SELECT COUNT(*) FROM appointments"),
            ("Admissions", "SELECT COUNT(*) FROM admissions WHERE status='Admitted'"),
            ("Discharges", "SELECT COUNT(*) FROM discharges"),
            ("Bills", "SELECT COUNT(*) FROM bills"),
        ]

        for i, (label, sql) in enumerate(stats):
            val = self.db.execute(sql, fetch=True)[0][0]
            card = self.make_card(grid)
            card.grid(row=i // 3, column=i % 3, sticky="ew", padx=5, pady=5)
            tk.Label(card, text=label, bg="white", fg="#668099",
                     font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(12, 2))
            tk.Label(card, text=str(val), bg="white", fg="#0b4b82",
                     font=("Segoe UI Semibold", 22)).pack(anchor="w", padx=14, pady=(0, 12))

        for i in range(3):
            grid.columnconfigure(i, weight=1)

        lower = self.make_card(outer, "Financial Summary")
        lower.pack(fill="x", pady=10)

        total = self.db.execute(
            "SELECT COALESCE(SUM(total),0) FROM bills", fetch=True
        )[0][0]
        paid = self.db.execute(
            "SELECT COALESCE(SUM(paid),0) FROM bills", fetch=True
        )[0][0]
        pending = self.db.execute(
            "SELECT COALESCE(SUM(pending),0) FROM bills", fetch=True
        )[0][0]

        for i, (label, value) in enumerate([
            ("Total Billed", total),
            ("Total Collected", paid),
            ("Total Pending", pending)
        ]):
            f = tk.Frame(lower, bg="#f3f8fc", bd=1, relief="solid")
            f.grid(row=0, column=i, sticky="ew", padx=6, pady=12)
            lower.columnconfigure(i, weight=1)
            tk.Label(f, text=label, bg="#f3f8fc", fg="#5c758a",
                     font=("Segoe UI", 9)).pack(pady=(10, 2))
            tk.Label(f, text=f"₹ {value:,.2f}", bg="#f3f8fc",
                     fg="#0b4b82", font=("Segoe UI Semibold", 16)).pack(pady=(0, 10))

        actions = tk.Frame(outer, bg="#eef5fb")
        actions.pack(fill="x", pady=4)
        self.button(actions, "🖨 Open Printable Report",
                    self.print_report).pack(side="left")

    def print_report(self):
        today = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        patients = self.db.execute("SELECT COUNT(*) FROM patients", fetch=True)[0][0]
        doctors = self.db.execute("SELECT COUNT(*) FROM doctors", fetch=True)[0][0]
        appointments = self.db.execute("SELECT COUNT(*) FROM appointments", fetch=True)[0][0]
        admissions = self.db.execute(
            "SELECT COUNT(*) FROM admissions WHERE status='Admitted'", fetch=True
        )[0][0]
        discharges = self.db.execute("SELECT COUNT(*) FROM discharges", fetch=True)[0][0]
        bills = self.db.execute("SELECT COUNT(*) FROM bills", fetch=True)[0][0]
        total = self.db.execute("SELECT COALESCE(SUM(total),0) FROM bills", fetch=True)[0][0]
        paid = self.db.execute("SELECT COALESCE(SUM(paid),0) FROM bills", fetch=True)[0][0]
        pending = self.db.execute("SELECT COALESCE(SUM(pending),0) FROM bills", fetch=True)[0][0]

        filename = os.path.abspath("medicare_hospital_report.html")
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>MediCare Hospital Report</title>
<style>
body {{font-family:Arial;margin:35px;color:#163b5c}}
h1 {{color:#0b4b82}}
table {{border-collapse:collapse;width:100%;margin-top:20px}}
td,th {{border:1px solid #c8dce9;padding:12px}}
th {{background:#e8f4fb;text-align:left}}
button {{padding:10px 18px;background:#087ac1;color:#fff;border:0;margin-bottom:15px}}
@media print {{button{{display:none}}}}
</style>
</head>
<body>
<button onclick="window.print()">🖨 Print Report</button>
<h1>♥ MediCare Hospital</h1>
<p>Compassion • Care • Better Health</p>
<p><b>Report Generated:</b> {today}</p>
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Total Patients</td><td>{patients}</td></tr>
<tr><td>Total Doctors</td><td>{doctors}</td></tr>
<tr><td>Total Appointments</td><td>{appointments}</td></tr>
<tr><td>Current Admissions</td><td>{admissions}</td></tr>
<tr><td>Total Discharges</td><td>{discharges}</td></tr>
<tr><td>Total Bills</td><td>{bills}</td></tr>
<tr><td>Total Billed</td><td>₹ {total:,.2f}</td></tr>
<tr><td>Total Collected</td><td>₹ {paid:,.2f}</td></tr>
<tr><td>Total Pending</td><td>₹ {pending:,.2f}</td></tr>
</table>
<p style="margin-top:35px;color:#71879a">Computer-generated hospital report.</p>
</body>
</html>"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        webbrowser.open("file://" + filename)

    # ------------------------- UTILITIES -------------------------

    def next_id(self, table, column, prefix):
        row = self.db.execute(
            f"SELECT {column} FROM {table} ORDER BY id DESC LIMIT 1",
            fetch=True
        )
        if not row:
            return f"{prefix}001"

        value = row[0][column]
        digits = "".join(ch for ch in str(value) if ch.isdigit())
        try:
            n = int(digits) + 1
        except ValueError:
            n = 1
        return f"{prefix}{n:03d}"


def main():
    root = tk.Tk()
    app = HospitalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
