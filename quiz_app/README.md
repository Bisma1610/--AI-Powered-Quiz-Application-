# AI-Powered Quiz Application
> Submitted by: Bisma | Roll No: 2K23-BSCS-229 | 6th Semester | BS Computer Science

A Flutter + Python AI-powered quiz application that generates MCQs from uploaded study material using the FLAN-T5 language model.

---

## Project Structure

```
quiz_app/
├── lib/
│   ├── main.dart                        # App entry point
│   ├── app_router.dart                  # GoRouter navigation
│   ├── models/
│   │   ├── user_model.dart              # User data model
│   │   └── quiz_model.dart              # Quiz, Question, Result, Class models
│   ├── services/
│   │   ├── database_service.dart        # SQLite CRUD operations
│   │   ├── auth_service.dart            # Login, signup, session
│   │   └── ai_service.dart              # FLAN-T5 API calls
│   ├── bloc/
│   │   ├── auth/                        # AuthBloc (login/signup/logout)
│   │   └── quiz/                        # QuizBloc (generate/answer/submit)
│   └── screens/
│       ├── auth/
│       │   ├── splash_screen.dart
│       │   ├── login_screen.dart
│       │   └── signup_screen.dart
│       ├── student/
│       │   ├── student_dashboard.dart
│       │   ├── upload_file_screen.dart
│       │   ├── quiz_screen.dart
│       │   ├── result_screen.dart
│       │   └── history_screen.dart
│       └── teacher/
│           ├── teacher_dashboard.dart
│           └── class_detail_screen.dart
├── backend/
│   ├── main.py                          # FastAPI + FLAN-T5 backend
│   └── requirements.txt
└── pubspec.yaml
```

---

## Technology Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Frontend    | Flutter (Dart)                    |
| State       | BLoC Pattern (flutter_bloc 8.x)  |
| Navigation  | GoRouter                          |
| Database    | SQLite (sqflite)                  |
| Backend     | Python FastAPI                    |
| AI Model    | FLAN-T5 (Hugging Face)            |
| Charts      | fl_chart                          |

---

## Setup Instructions

### Flutter App

```bash
# 1. Install dependencies
flutter pub get

# 2. Run on Android emulator or device
flutter run

# 3. Build APK
flutter build apk --release
```

### Python Backend

```bash
cd backend

# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> The Flutter app connects to `http://10.0.2.2:8000` (Android emulator localhost).
> For a real device, replace with your machine's local IP address in `ai_service.dart`.

---

## Features

### Student
- Register/Login with role-based auth
- Select class during signup
- Upload PDF, DOCX, or TXT files
- Configure quiz: number of questions, difficulty, timer
- Take timer-based MCQ quizzes (auto-submit on timeout)
- View instant results with score, grade, and percentage
- View full quiz history

### Teacher
- Register/Login as teacher
- View assigned classes
- Monitor student performance per class
- Bar chart visualization of class scores

---

## Key Modules

### BLoC Architecture
```
AuthBloc:  AuthEvent → AuthBloc → AuthState
           LoginRequested → AuthLoading → AuthAuthenticated/AuthFailure
           SignupRequested → AuthLoading → AuthAuthenticated/AuthFailure

QuizBloc:  QuizEvent → QuizBloc → QuizState
           QuizGenerateRequested → QuizLoading → QuizLoaded
           QuizAnswerSelected → QuizLoaded (updated)
           QuizSubmitted → QuizCompleted
```

### Database Tables
- `users` — stores student/teacher accounts
- `classes` — predefined class list
- `teacher_classes` — many-to-many teacher↔class
- `uploaded_files` — file upload records
- `quizzes` — quiz sessions
- `quiz_results` — scores per quiz

---

## Notes
- Passwords are hashed using SHA-256 before storage
- FLAN-T5 model loads on first API call (~1-2 min first run)
- App works offline with mock questions if backend is unavailable
- Default classes are seeded automatically on first app launch
