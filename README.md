# NahinEdify

**A full-stack Learning Management System built with Django REST Framework and React.**

NahinEdify is a role-based Learning Management System designed to manage courses, lessons, assignments, submissions, grading, and user accounts through a RESTful API and modern React frontend.

---

## Overview

NahinEdify provides a centralized platform for managing learning activities between **administrators, teachers, and students**.

The backend is built with **Django REST Framework**, while the frontend is developed using **React and Vite**. Authentication is handled using **JWT**, with role-based permissions controlling access to different resources.

---

## Features

* JWT-based authentication
* Phone number login
* Role-based access control
* Admin, Teacher, and Student roles
* Course management
* Lesson management
* Assignment management
* Assignment submission
* Grading and results
* Enrollment management
* Search and filtering
* Password reset through email
* Protected API endpoints
* Responsive React frontend
* RESTful API architecture

---

## Tech Stack

### Backend

* Python
* Django
* Django REST Framework
* Simple JWT
* SQLite

### Frontend

* React
* JavaScript
* Vite
* Tailwind CSS
* Recharts

### Tools

* Git
* GitHub
* VS Code

---

## Screenshots

### Login

### Dashboard

### Courses

### Assignments

### Submissions & Results

### Profile

---

## Project Structure

```text
NahinEdify/
│
├── backend/
│   ├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   └── screenshots/
│       ├── login.png
│       ├── dashboard.png
│       ├── courses.png
│       ├── assignments.png
│       ├── submissions.png
│       └── profile.png
│
└── README.md
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/nahinsha/NahinEdify.git
cd NahinEdify
```

---

### 2. Backend Setup

Open the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

### 3. Environment Variables

Create a `.env` file inside the `backend` directory:

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

The `.env` file should not be committed to GitHub.

---

### 4. Database Setup

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create an admin account:

```bash
python manage.py createsuperuser
```

---

### 5. Run the Backend

Start the Django development server:

```bash
python manage.py runserver
```

The backend API will be available at:

```text
http://127.0.0.1:8000/api/
```

---

### 6. Frontend Setup

Open another terminal and go to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

The frontend will be available at the URL shown by Vite in the terminal.

---

## User Roles & Permissions

### Admin

The administrator has full access to the system and can manage:

* Users
* Courses
* Lessons
* Assignments
* Enrollments
* Submissions
* Grades
* Other system resources

### Teacher

Teachers can manage learning content and academic activities, including:

* Courses
* Lessons
* Assignments
* Enrollments
* Student submissions
* Grading

### Student

Students can:

* View available courses
* View lessons
* Access assignments
* Submit assignments
* View their grades and results

---

## API Overview

The backend provides RESTful API endpoints for the main LMS resources.

```text
/api/login/
/api/register/
/api/courses/
/api/lessons/
/api/assignments/
/api/submissions/
/api/grades/
/api/enrollments/
```

Authentication-protected endpoints require a valid JWT access token.

---

## Authentication

NahinEdify uses **JWT (JSON Web Token)** authentication.

After successful login, the API provides:

* Access Token
* Refresh Token

The access token is used to access protected API endpoints according to the user's role and permissions.

---

## GitHub Repository

**Repository:**
https://github.com/nahinsha/NahinEdify

---

## Author

**Nahin Shahariar**

* GitHub: https://github.com/nahinsha
* LinkedIn: https://linkedin.com/in/md-shahariar-nahin-a5b147301
* Portfolio: https://shahariar-nahin-portfolio.vercel.app/
