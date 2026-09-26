# ⚡ Siraj UPS and Solar — Billing & Inventory Management System

Professional, simple, fast, and user-friendly **Billing, Inventory, Customer, Supplier, Expense, Service Repair, and Financial Management Desktop Software** built for **Siraj UPS and Solar**.

---

## 🛠️ Technology Stack

* **Backend Framework:** Python (Django 5/6)
* **WSGI Production Server:** Waitress
* **Desktop App Window Engine:** PyWebView / Chromium App Container
* **Database:** SQLite3 (Compatible with PostgreSQL for future cloud deployment)
* **PDF Invoice Engine:** ReportLab
* **Frontend UI:** HTML5, Vanilla CSS3, Bootstrap 5, Font Awesome 6 Icons, Chart.js Charts

---

## 🚀 Quick Access & How to Run

### 1. Desktop Shortcut (Recommended)
Double-click the **`Siraj UPS and Solar`** shortcut icon on your Windows Desktop to launch the standalone desktop window silently.

### 2. Standalone Portable Executable (`.exe`)
Copy the folder **`Siraj UPS Software Portable`** located on your Desktop to any USB drive or secondary PC and run:
```cmd
SirajUPS_Software.exe
```
*(No Python installation required on the other computer).*

### 3. Local Web Access
While the software is running on the main shop computer, open any web browser and go to:
```url
http://127.0.0.1:8000
```

### 4. Development Server Mode
From the project folder (`C:\Users\siraj\Desktop\Siraj UPS`), run:
```powershell
venv\Scripts\python.exe manage.py runserver 8000
```

---

## 🔑 Default Login Credentials

* **Username:** `admin`
* **Password:** `admin1234`

---

## 📦 Key System Modules & Features

### 1. POS Counter Billing & Invoicing
* Quick product search by SKU code, name, brand, or barcode scanner.
* Dynamic quantity updates, unit price edits, item-level discounts, and overall bill discount.
* Flexible payment methods: **Cash**, **Bank Transfer**, **Easypaisa**, **JazzCash**, **Udhaar (Credit)**.
* Automatic stock deduction and PDF invoice generation with official shop logo.
* Real-time calculation of **Change Due / Return** when paid cash exceeds grand total.

### 2. Products & Inventory Management
* Complete catalog for UPS units, Batteries, Solar Panels, Inverters, Cables, and Accessories.
* Inline **"+ New Category"** modal for adding categories without leaving the form.
* Stock adjustment modal for adding/removing stock with audit logs.
* Visual **Low Stock Warnings** when inventory drops below alert thresholds.

### 3. Customer & Udhaar (Credit) Ledger
* Complete registry of customer accounts, phone numbers, and addresses.
* Real-time tracking of total outstanding credit (**Udhaar**).
* **"Record Payment"** feature to log cash recovery and update customer balances instantly.
* Printable customer statement ledgers.

### 4. Suppliers & Stock Purchases
* Manage wholesale suppliers and battery distributors.
* Log incoming purchase orders to automatically increase stock levels.
* Track unpaid balances owed to suppliers.

### 5. Shop Expenses & Services / Repair Jobs
* **Expenses:** Record daily shop bills, rent, staff salaries, tea/lunch, and transport.
* **Services / Repairs:** Track UPS/Inverter repair tickets, customer equipment, repair statuses (*Pending, In Progress, Completed, Delivered*), and repair charges.

### 6. Reports & Analytics
* Interactive Dashboard with sales trends, daily revenue, and net profit charts.
* Financial reports: **Sales Report**, **Purchase Report**, **Profit & Loss Report**, **Customer Udhaar Balances**, **Supplier Payables**, and **Stock Valuation**.

### 7. Administration & Maintenance
* **Shop Settings:** Customize Shop Name, Tagline, Phone, Address, NTN/Tax #, and Upload Shop Logo.
* **User Roles:** Assign **Admin** (full access) or **Cashier** (POS billing only) user roles.
* **Database Backup & Restore:** Download daily `.json` database backups and restore saved backups.
* **Danger Zone (Database Reset):** Clear demo/test data with security confirmation while preserving admin users and shop configuration.

---

## 🌐 Multi-PC & Shop Wi-Fi Network Sharing

### Scenario A: Shared over Shop Wi-Fi / Local Area Network (LAN)
1. Find your main shop PC's local IP address (e.g., `192.168.1.10`).
2. Keep the software running on the main computer.
3. On any second laptop or mobile phone connected to the same shop Wi-Fi, open the browser and enter:
   `http://192.168.1.10:8000`

### Scenario B: Transfer to Second PC via USB Drive
1. Copy the folder **`Siraj UPS Software Portable`** from your Desktop to a USB Flash Drive.
2. Paste the folder onto the Desktop of the new PC/Laptop.
3. Double-click **`SirajUPS_Software.exe`**.

---

## 📄 User Documentation Files

* **`Siraj_UPS_Solar_User_Guide.pdf`** — Printable PDF Operations Manual on your Desktop.
* **`Siraj_UPS_Solar_User_Guide.docx`** — Editable Microsoft Word Document on your Desktop.

---

*Designed and Developed for **Siraj UPS & Solar**.*
