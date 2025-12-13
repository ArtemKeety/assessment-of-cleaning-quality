assessment-of-cleaning-quality/
├── alembic/
│   ├── versions/
│   │   ├── b46c8e4bab93_initial_migration.py
│   │   └── ee6391437f5c_migration_2.py
│   ├── README
│   ├── alembic_scripts
│   ├── env.py
│   └── script.py.mako
├── configuration/
│   ├── __init__.py
│   ├── base.py
│   ├── celery.py
│   ├── cookie.py
│   ├── db.py
│   └── files.py
├── customlogger/
│   ├── __init__.py
│   └── log.py
├── database/
│   ├── __init__.py
│   ├── async_psql.py
│   ├── async_redis.py
│   └── sync_psql.py
├── internal/
│   ├── midleware/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── custom_ratelimit.py
│   │   ├── error.py
│   │   ├── files.py
│   │   ├── header.py
│   │   ├── logger.py
│   │   ├── swagger.py
│   │   └── timeout.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── flat.py
│   │   ├── report.py
│   │   └── user.py
│   ├── repo/
│   │   ├── __init__.py
│   │   ├── flat.py
│   │   ├── report.py
│   │   └── user.py
│   ├── router/
│   │   ├── __init__.py
│   │   ├── flat.py
│   │   ├── report.py
│   │   └── user.py
│   ├── service/
│   │   ├── __init__.py
│   │   ├── flat.py
│   │   ├── report.py
│   │   └── user.py
│   ├── shemas/
│       ├── __init__.py
│       ├── base.py
│       ├── flat.py
│       ├── report.py
│       ├── session.py
│       └── user.py
├── locales/
│   ├── en/
│   │   ├── LC_MESSAGES/
│   │       └── messages.po
│   ├── ru/
│   │   ├── LC_MESSAGES/
│   │       └── messages.po
│   └── scripts.txt
├── static/
│   ├── flat/
│   ├── raw_report/
│   ├── report/
├── tasks/
│   ├── __init__.py
│   ├── ai_handler.py
│   ├── eq_image.py
│   ├── req_ai.py
│   └── scripts.txt
├── utils/
│   ├── __init__.py
│   ├── byte.py
│   ├── file.py
│   └── password.py
├── Dockerfile
├── Dockerfile.celery
├── alembic.ini
├── celery_app.py
├── docker-compose.yaml
├── main.py
├── requirements.txt
└── sql.txt
