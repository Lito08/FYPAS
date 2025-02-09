# Face Recognition Attendance System
Final Year Project for enhancing face recognition algorithm accuracy through parameter optimization for attendance system.

## 📌 Overview
A Django-based face recognition attendance system that automates student check-in using AI.

## ⚙️ Installation
Clone the repository and install dependencies:
```bash
git clone <your-repository-url>
cd <your-project-folder>
pip install -r requirements.txt
```
Ensure PostgreSQL is installed and configured.

## 🚀 Running the Project
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

## 🏗 Project Structure
```
attendance_system/
├── courses/        # Course and enrollment management
├── attendance/     # Attendance tracking modules
├── users/          # User authentication and roles
├── templates/      # HTML templates
├── static/         # CSS and JavaScript
├── manage.py       # Django management script
├── requirements.txt # Project dependencies
├── README.md       # Project documentation
```

## 🎯 Features
- 🔹 Face Recognition for Attendance
- 🔹 QR Code Backup
- 🔹 Schedule Management
- 🔹 Admin & Lecturer Controls
- 🔹 Student Self-Enrollment with Conflict Prevention

## 📸 Screenshots
_Include relevant images_

## 🛠 Technologies Used
- **Backend:** Django, PostgreSQL
- **Frontend:** Bootstrap, JavaScript
- **AI:** OpenCV, dlib, Face Recognition

## 📂 Database Setup
Create a `.env` file and configure:
```
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
```
Run migrations:
```bash
python manage.py migrate
```

## ✍ Contributors
- [Daniel Yusoff bin Asri](https://github.com/Lito08)
