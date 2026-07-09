# School Result & Attendance Portal — Architecture

## Overview

A school management system where teachers record attendance and scores, students/parents view results, and AI predicts at-risk students based on attendance and grade trends.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | Python + Flask | Already know it, fast to build |
| Database | PostgreSQL | Real relational DB (vs SQLite), good for joins |
| ORM | SQLAlchemy | Production-grade, migrations via Alembic |
| Auth | Flask-Login + role-based | 3 user types: Admin, Teacher, Student/Parent |
| Frontend | Jinja2 + Tailwind CSS / Bootstrap 5 | No JS framework overhead |
| PDF | WeasyPrint or ReportLab | Report cards, attendance sheets |
| AI | scikit-learn (LogisticRegression) | Predict at-risk — lightweight, no GPU needed |
| Async | Celery + Redis | Background: PDF generation, notifications |
| Container | Docker Compose | Flask + Postgres + Redis + Celery worker |
| CI/CD | GitHub Actions | lint → test → build → deploy |
| Monitoring | Prometheus + Grafana (bonus) | Track request latency, error rates |

---

## User Roles & Permissions

| Feature | Admin | Teacher | Student/Parent |
|---------|-------|---------|----------------|
| Manage classes/courses | ✓ | | |
| Manage users | ✓ | | |
| Record attendance | | ✓ | |
| Enter/update scores | | ✓ | |
| View own scores | | | ✓ |
| View reports & trends | ✓ | ✓ | limited |
| Access AI risk predictions | ✓ | ✓ | |
| Generate PDF reports | ✓ | ✓ | |

---

## Database Schema

```
users
├── id (PK)
├── email / password (hashed)
├── full_name
├── role (admin | teacher | student | parent)
├── parent_id (FK → users, nullable)

classes
├── id (PK)
├── name (e.g. "Grade 10A")
├── academic_year
├── teacher_id (FK → users)

subjects
├── id (PK)
├── name
├── class_id (FK → classes)

attendance
├── id (PK)
├── student_id (FK → users)
├── class_id (FK → classes)
├── date
├── status (present | absent | excused)
├── UNIQUE(student_id, class_id, date)

scores
├── id (PK)
├── student_id (FK → users)
├── subject_id (FK → subjects)
├── term (1 | 2 | 3)
├── exam_type (midterm | final | assignment)
├── score (float)
├── max_score (float)

risk_predictions
├── id (PK)
├── student_id (FK → users)
├── term
├── risk_score (0.0 — 1.0)
├── risk_level (low | medium | high)
├── top_factors (JSON)
├── generated_at (datetime)
```

---

## API Routes

```
# Auth
POST   /auth/login
POST   /auth/logout

# Dashboard
GET    /                    → role-based dashboard

# Attendance (Teacher)
GET    /attendance/<class_id>
POST   /attendance/<class_id>
GET    /attendance/student/<student_id>

# Scores (Teacher)
GET    /scores/<class_id>/<subject_id>
POST   /scores/<class_id>/<subject_id>
GET    /scores/student/<student_id>

# Reports (Student/Parent)
GET    /reports/<student_id>
GET    /reports/<student_id>/pdf       → download PDF

# AI Predictions (Admin/Teacher)
GET    /risk/class/<class_id>
GET    /risk/student/<student_id>

# Admin
GET    /admin/users
POST   /admin/users
GET    /admin/classes
POST   /admin/classes
```

---

## Project Structure

```
school-portal/
├── app/
│   ├── __init__.py          # create_app() factory
│   ├── config.py            # Settings: DB, Redis, env vars
│   ├── models/
│   │   ├── user.py
│   │   ├── class_.py
│   │   ├── subject.py
│   │   ├── attendance.py
│   │   ├── score.py
│   │   └── risk.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── attendance.py
│   │   ├── scores.py
│   │   ├── reports.py
│   │   ├── risk.py
│   │   └── admin.py
│   ├── services/
│   │   ├── pdf_generator.py
│   │   ├── risk_predictor.py
│   │   └── notification.py
│   ├── templates/
│   │   ├── layouts/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── attendance/
│   │   ├── scores/
│   │   ├── reports/
│   │   ├── risk/
│   │   └── admin/
│   └── static/
│       ├── css/
│       └── js/
├── migrations/              # Alembic
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_attendance.py
│   ├── test_scores.py
│   ├── test_risk.py
│   └── test_reports.py
├── docker-compose.yml       # Flask + Postgres + Redis + Celery
├── Dockerfile
├── .github/workflows/ci.yml
├── pyproject.toml            # Ruff + pytest
└── seed.py                  # Demo data seeder
```

---

## AI: At-Risk Prediction

### Features (input to model)

| Feature | Source | Description |
|---------|--------|-------------|
| attendance_rate | attendance | % of classes attended this term |
| avg_score | scores | Average across all subjects |
| score_trend | scores | Slope of scores over time (-1 to 1) |
| missing_assignments | scores | Count of missing/zero assignments |
| prev_term_gpa | scores | Previous term GPA |
| days_absent_streak | attendance | Consecutive absences |

### Model

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

model = LogisticRegression(class_weight="balanced")
# Trained on historical data (or simulated seed data)
# Predicts: at_risk (1) or not (0)
# Risk score = probability of class 1
```

### Output

```
Student: Fatou Sillah (Grade 10A)
Risk Level: HIGH (0.87)
Top Factors:
  • Attendance rate: 62% (below threshold)
  • Score trend: declining (-0.4)
  • Missing assignments: 3
```

Run predictions:
- **On-demand** — teacher clicks "Analyze Class"
- **Scheduled** — Celery beat runs weekly, caches results in `risk_predictions` table

---

## DevOps Pipeline

```yaml
# .github/workflows/ci.yml
on: push → main

jobs:
  lint:    ruff check .
  test:    pytest -v --cov=app
  build:   docker compose build
```

```yaml
# docker-compose.yml
services:
  web:      Flask + Gunicorn, :5000
  db:       PostgreSQL 16, volume persisted
  redis:    Redis 7, message broker
  worker:   Celery worker (same image as web)
  beat:     Celery beat (scheduled tasks)
```

### Deployment

```bash
# Dev
docker compose up

# Initial setup
docker compose exec web flask db upgrade
docker compose exec web python seed.py

# Production additions:
# - nginx reverse proxy (SSL termination)
# - Traefik or Caddy for automatic HTTPS
# - GitHub Container Registry for images
```

---

## Why This Project Strengthens Your Portfolio

| Skill | How This Project Proves It |
|-------|---------------------------|
| **Full-stack** | Flask + SQLAlchemy + PostgreSQL + Jinja2/Tailwind + PDF |
| **Auth & roles** | Flask-Login, 3 user types, decorator-based access control |
| **Relational DB** | 6+ tables, foreign keys, migrations (Alembic), complex queries |
| **AI/ML in production** | Trained model served alongside web app, feature engineering |
| **Async tasks** | Celery + Redis for PDF gen + scheduled predictions |
| **DevOps** | Multi-service Docker Compose, CI/CD, health checks |
| **Testing** | Pytest with DB fixtures, route testing, model validation |
| **Monitoring** | Prometheus metrics + Grafana dashboards (bonus) |

---

## Getting Started

```bash
# Clone
git clone https://github.com/your-username/school-portal.git
cd school-portal

# Copy env
cp .env.example .env

# Start everything
docker compose up

# Run migrations
docker compose exec web flask db upgrade

# Seed demo data
docker compose exec web python seed.py

# Open http://localhost:5000
```

Demo accounts (seeded):
- Admin: admin@school.gov / admin123
- Teacher: teacher@school.gov / teacher123
- Student: student@school.gov / student123
