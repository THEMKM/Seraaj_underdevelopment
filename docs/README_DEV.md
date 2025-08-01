# Development Environment

## Database Migrations

1. Initialize Alembic (already done):
   ```bash
   cd apps/api
   alembic stamp head          # mark database at current revision
   alembic revision --autogenerate -m "<message>"
   alembic upgrade head
   ```

2. Run migrations against PostgreSQL container:
   ```bash
   export DATABASE_URL=postgresql://postgres:password@localhost:5432/seraaj_dev
   alembic upgrade head
   ```

`alembic.ini` uses `${DATABASE_URL}` so set it appropriately for SQLite or Postgres.
