# Models Layer (`backend/app/models/`)

This directory contains SQLAlchemy 2.0 ORM database models.

### Guidelines:
- Every entity model must inherit from `app.db.base.Base`.
- All tables representing private user data must include a `user_id` foreign key referencing the user table (Project Rule 1).
- Import every model into `models/__init__.py` so that Alembic's `target_metadata = Base.metadata` in `alembic/env.py` discovers all tables during schema migrations.
