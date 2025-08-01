# Development Environment

## Database Migrations

1. Initialize Alembic (already done):
   ```bash
   cd apps/api
   alembic revision --autogenerate -m "<message>"
   alembic upgrade head
   ```

2. Run migrations against PostgreSQL container:
   ```bash
   # ensure DATABASE_URL points to postgres
   export DATABASE_URL=postgresql://postgres:password@localhost:5432/seraaj_dev
   alembic upgrade head
   ```
