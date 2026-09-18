# 🏥 MediCare Hospital Management System

A desktop-based **Hospital Management System** developed using **Python, Tkinter, and SQLite**. The application is designed specifically for **receptionist operations**, helping manage patients, doctors, appointments, admissions, discharges, billing, and reports through a simple and professional graphical interface.

---

## 📌 Project Overview

The **MediCare Hospital Management System** is designed to simplify day-to-day receptionist activities in a hospital.

Instead of maintaining patient and billing information manually, the system provides a centralized application for managing important hospital records.

The application uses:

- **Python** for application development
- **Tkinter** for the graphical user interface
- **SQLite** for database management
- **HTML** for printable bill generation

---

## ✨ Features

### 🔐 1. Login & Logout

- Receptionist login
- Username and password authentication
- Logout functionality
- Secure access to the application

---

### 📊 2. Dashboard

The dashboard provides a quick overview of hospital activities.

It displays:

- 👤 Total Patients
- 📅 Today's Appointments
- 👨‍⚕️ Available Doctors
- 💰 Pending Bills
- 🛏️ Available Beds

---

### 👤 3. Patient Registration

Receptionists can register new patients with details such as:

- Patient ID
- Patient Name
- Age
- Gender
- Phone Number
- Blood Group
- Address
- Emergency Contact

---

### 🔎 4. Patient Management

The system allows receptionists to:

- View patients
- Search patients
- Edit patient information
- Delete patient records
- Update patient details

---

### 👨‍⚕️ 5. Doctor Management

Doctor information can be managed through the application.

Details include:

- Doctor Name
- Specialization
- Department
- Available Days
- Available Time
- Consultation Fee

The system also supports **updating doctor information**.

---

### 📅 6. Appointment Management

Receptionists can manage appointments with features such as:

- Book Appointment
- View Appointments
- Reschedule Appointment
- Cancel Appointment
- Update Appointment Status

---

### 🛏️ 7. Admission Management

The application supports patient admission management.

Receptionists can:

- Admit patients
- Assign rooms
- Assign beds
- Assign doctors
- Record admission dates
- Manage bed availability

---

### 🏥 8. Discharge Management

The discharge module allows receptionists to:

- Discharge patients
- Record discharge dates
- Generate final billing information
- Update bed availability

---

### 💰 9. Billing Management

The billing system supports multiple types of hospital charges:

- Consultation Fee
- Room Charges
- Medicine Charges
- Lab Charges
- Other Charges

The system automatically calculates:

**Total Amount = Consultation + Room + Medicine + Lab + Other Charges**

Billing status can be maintained as:

- ✅ Paid
- ⏳ Pending

---

### 🖨️ 10. Printable Bill

The system provides printable billing functionality.

A professional HTML-based bill can be generated containing:

- Hospital Name
- Patient Information
- Doctor Information
- Consultation Charges
- Room Charges
- Medicine Charges
- Lab Charges
- Other Charges
- Total Amount
- Payment Status

---

### 🔍 11. Search

The application provides search functionality for quickly finding patient and hospital records.

This helps receptionists access information without manually checking large amounts of data.

---

### 📈 12. Reports

The reporting section provides useful information about hospital operations and billing.

Examples include:

- Patient statistics
- Appointment information
- Doctor information
- Billing summary
- Paid bills
- Pending bills
- Financial summary

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| 🐍 Python | Application development |
| 🖥️ Tkinter | Graphical User Interface |
| 🗄️ SQLite | Database management |
| 🌐 HTML | Printable bill generation |
| 📁 Git | Version control |
| 🐙 GitHub | Project hosting |

---

## 📂 Project Structure

```text
MediCare-Hospital-Management-System/
│
├── 📁 Bills/
│   └── hospital.py
│
├── 📄 .gitignore
├── 📄 B001_printable_bill.html
├── 📄 main.py
└── 📄 README.md
