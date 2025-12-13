# Assessment of Cleaning Quality — Backend Service

Backend-сервис для обработки и оценки качества уборки.  
Проект демонстрирует продакшн-подход к построению backend-приложений с использованием асинхронных задач, слоистой архитектуры и контейнеризации.

---

## ⚙️ Tech stack

- Python 3.13
- FastAPI
- PostgreSQL
- Redis
- Celery
- Alembic
- Docker / Docker Compose
- Pydantic

---

## 📁 Project structure

```text
assessment-of-cleaning-quality/
├── alembic/
│   └── versions/
├── configuration/
│   ├── base.py
│   ├── celery.py
│   ├── db.py
│   └── files.py
├── customlogger/
├── database/
│   ├── async_psql.py
│   ├── async_redis.py
│   └── sync_psql.py
├── internal/
│   ├── middleware/
│   ├── models/
│   ├── repo/
│   ├── router/
│   ├── service/
│   └── schemas/
├── locales/
├── static/
├── tasks/
├── utils/
├── main.py
├── celery_app.py
├── docker-compose.yaml
├── Dockerfile
├── Dockerfile.celery
└── requirements.txt
