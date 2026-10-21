# 🎓 Faculty Load Management System (FLMS)
### Apex Institute of Engineering & Technology

A modern, professional, responsive, and fully functional **Faculty Load Management System** built with **Python**, **FastAPI**, **SQLite**, **SQLAlchemy**, and a sleek **HTML5/CSS3/JavaScript** frontend with **Chart.js**, **ReportLab**, and **Pandas/OpenPyXL**.

---

## 🌟 Key Features Overview

### 1. 🔐 Role-Based Login System
- **Two Separate Roles**:
  - **HOD Login**: Administrative privileges across all faculty profiles, duty assignments, timetable conflict overrides, analytics, reports, and audit trails.
  - **Faculty Login**: Restricted portal displaying personalized weekly timetables, assigned lectures and duties, real-time notifications, countdown reminders, and personal workload metrics.
- **Convenient 1-Click Demo Logins** on the login screen for testing both HOD and various Faculty profiles (High Load, Balanced, Available).

### 2. 📊 HOD Dashboard & Analytics
- **6 KPI Metric Cards**:
  1. **Total Faculty Members**: Real-time count of active departmental staff.
  2. **Lectures Scheduled This Week**: Total volume of theory classes and lab sessions.
  3. **Highest Teaching Load**: Faculty with the highest weekly hours (e.g. Dr. Amit Verma).
  4. **Lowest Teaching Load**: Faculty with the lowest teaching load (e.g. Prof. Anita Desai).
  5. **Faculty Available for Extra Duties**: Faculty with surplus capacity below thresholds.
  6. **Department Average Load**: Benchmark average hours per faculty.
- **Interactive Visual Charts** (Chart.js):
  - Stacked Teaching Load Breakdown (Regular Lectures, Labs, Substitute Classes, Exam & College Duties).
  - Department Workload Health Doughnut Chart (High Load vs Balanced vs Low Load).
- **Faculty Workload Directory Table**:
  - Columns: `Faculty Name | Department | Subjects | Weekly Lectures | Assigned Duties | Total Load | Available Slots | Actions`
  - Real-time search by name, code, designation, or subjects.
  - Instant filter by workload status (**High Workload**, **Balanced Workload**, **Low Workload**).

### 3. ⚖️ Faculty Load Management & Availability Finder
- Automatic calculation of weekly teaching hours based on scheduled events and durations.
- **Status Indicators**:
  - 🔴 **High Workload** (`>= 16 hrs` or exceeding weekly limit)
  - 🟢 **Balanced Workload** (`10 – 15 hrs`)
  - 🔵 **Low Workload / Available** (`< 10 hrs`)
- **Available Faculty Finder**: Dedicated recommendation engine ranking faculty by lowest load and remaining capacity for substitute lectures and examination duties.

### 4. ➕ Lecture & Duty Assignment with Conflict Prevention
- Supports assignment of:
  - **Regular Lectures**
  - **Substitute Lectures**
  - **Laboratory Practical Duties**
  - **Examination Duties** (Invigilation, Chief Superintendent)
  - **Other College Duties** (NAAC Accreditation, IQAC, Sports Committee, etc.)
- **Real-Time Timetable Conflict Engine**:
  - Live pre-check runs as you select faculty, date, start/end time, and classroom.
  - Detects **Faculty Overlaps** (faculty already booked in another class/duty).
  - Detects **Classroom Overlaps** (room already booked by another instructor).
  - Detects **Student Class/Semester Overlaps** (students already have another class).
  - Warning banner displays exact conflict reasons and prevents accidental double-booking.

### 5. 📅 Weekly Timetable (Monday to Saturday)
- Interactive calendar grid spanning **Monday to Saturday** (09:00 AM to 05:00 PM).
- Color-coded badges for Regular Lectures (Blue), Practical Labs (Emerald), Substitute Classes (Amber), Exam Duties (Purple), and College Duties (Rose).
- Click any session card to open a full details popup modal (location, subject, HOD instructions).
- **HOD View**: Can view timetables for the entire department or filter by specific faculty member, classroom, or subject.
- **Faculty View**: Strictly locked to their own personal timetable.
- **Print Timetable** and **PDF Download** buttons.

### 6. ⏰ Automatic Notifications & Configurable Reminders
- Immediate notification generated whenever HOD creates or updates an assignment.
- **Automated Background Reminder Scheduler**:
  - Python background daemon thread continuously scans upcoming events.
  - Automatically dispatches reminders at configured lead times:
    - **5 minutes before**
    - **15 minutes before** (Default)
    - **30 minutes before**
    - **1 hour before**
    - **1 day before**
- Top-bar **Notification Bell** with animated pulse badge and unread count.
- Multi-channel delivery support: **In-App Alerts**, **Browser Push Notifications** (via Web Notifications API), and **Simulated Email Logs**.
- "Check Reminders Now" and "Send Test Alert" buttons to easily trigger and demonstrate live alerts.

### 7. 👤 Faculty Profile Management
- Store Faculty ID/Code, Name, Department, Designation, Email, Phone, Cabin Room, Subjects Taught, Weekly Lecture Limit, and Max Duties Limit.
- HOD can add new faculty (which automatically creates user login accounts with credentials), edit profiles, and deactivate faculty.
- Faculty can view their profile and customize their personal reminder preferences.

### 8. 📑 Departmental Reports & Multi-Format Export
- Weekly and monthly departmental reports summary.
- **Excel Export (.xlsx)**: Generated using `pandas` and `openpyxl` with multiple sheets:
  - *Faculty Workloads Summary*
  - *Detailed Schedules*
  - *Department KPI Metrics*
- **PDF Export (.pdf)**: High-resolution official document generated using `reportlab`:
  - Institutional header: "Apex Institute of Engineering & Technology"
  - Summary KPI cards
  - Faculty workload table with status coloring
  - Sign-off block for Academic Coordinator, HOD, and Dean Academics.

### 9. 📜 Audit History & Activity Logs
- Comprehensive audit trail recording all assignment creations, updates, deletions, and automated reminder triggers.

---

## 💻 Technology Stack

| Component | Technology Used |
|---|---|
| **Backend Framework** | Python 3.14 + FastAPI + Uvicorn |
| **Database** | SQLite + SQLAlchemy ORM |
| **Authentication** | JWT (PyJWT) + Bcrypt Password Hashing |
| **Background Scheduler** | Python Threading Daemon (Automated 30s reminder scanner) |
| **PDF Generation** | ReportLab 5.0 (Institutional format) |
| **Excel Generation** | Pandas + OpenPyXL |
| **Frontend** | Vanilla HTML5, Modern CSS3 (CSS Variables, Flexbox/Grid, Responsive), Vanilla ES6 JavaScript |
| **Data Visualization** | Chart.js 4.4 |
| **Typography** | Inter (Google Fonts) |

---

## 🚀 Setup & Launch Instructions

### 1. Requirements
Ensure Python 3.10+ is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python run.py
```
*(Or alternatively: `uvicorn main:app --reload --host 127.0.0.1 --port 8000`)*

### 4. Open in Browser
Visit: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🔑 Default Login Credentials

| Role | Username | Password | Full Name / Description |
|---|---|---|---|
| **HOD (Administrator)** | `hod_cs` | `admin123` | **Dr. Rajesh Sharma** (Head of Department, CSE) |
| **Faculty (High Load)** | `prof_amit` | `faculty123` | **Dr. Amit Verma** (Associate Professor, 18 hrs/week) |
| **Faculty (Balanced Load)** | `prof_priya` | `faculty123` | **Prof. Priya Patel** (Assistant Professor, 14 hrs/week) |
| **Faculty (Balanced Load)** | `prof_rohit` | `faculty123` | **Dr. Rohit Gupta** (Assistant Professor, 13 hrs/week) |
| **Faculty (Balanced Load)** | `prof_sneha` | `faculty123` | **Prof. Sneha Kulkarni** (Assistant Professor, 11 hrs/week) |
| **Faculty (Low / Available)** | `prof_vikram` | `faculty123` | **Prof. Vikram Singh** (Lecturer, 8 hrs/week - Available for duties) |
| **Faculty (Low / Available)** | `prof_anita` | `faculty123` | **Prof. Anita Desai** (Assistant Professor, 7 hrs/week - Available) |

*(Tip: You can also use the 1-click demo login buttons directly on the login screen!)*

---

## 🗄️ Database Structure

The application creates and manages an SQLite database (`faculty_load.db`) with the following tables:
1. `users`: Authentication records, encrypted passwords, roles (`hod` or `faculty`), and linked faculty IDs.
2. `faculty_profiles`: Faculty code, name, designation, department, contact info, weekly lecture limits, and subjects taught.
3. `subjects`: Course codes (e.g. CS501), subject names, credits, and weekly hours.
4. `classes`: Academic classes/sections (e.g. B.Tech CSE 5th Sem Sec A).
5. `classrooms`: Room numbers (LH-301, Lab-1, Seminar Hall), capacities, and room types.
6. `schedules`: Scheduled lectures and duties, dates, days, start/end times, assigned faculty, classroom, duty title, and HOD instructions.
7. `notifications`: In-app and browser notifications with read/unread statuses and delivery channels.
8. `reminder_preferences`: Configured lead times (5m, 15m, 30m, 1h, 1d) and delivery channel flags.
9. `audit_logs`: Traceability log for administrative actions and reminder dispatches.

---

## 🧪 Testing Conflict Detection Live
1. Log in as **HOD** (`hod_cs` / `admin123`).
2. Go to **Assign Lecture/Duty**.
3. Select **Dr. Amit Verma**, Date **Monday**, Start Time **09:00**, End Time **10:00**, Room **LH-301**.
4. Observe the **Live Conflict Warning**:
   > *"⚠️ Schedule Conflict Detected! Faculty Conflict: Dr. Amit Verma is already assigned to 'Data Structures: Trees & Graphs' from 09:00 to 10:00 in LH-301."*
5. Change faculty to **Prof. Vikram Singh** and time to **12:00 - 13:00**:
   > *"✓ Slot Available: Faculty and classroom are free of scheduling conflicts."*
