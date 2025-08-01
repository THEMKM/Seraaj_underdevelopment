# Backend API Hotfix Log - 2025-08-01

## Summary
- Added system health tests and ensured legacy stubs hidden from docs
- Fixed UTC time usage with timezone aware datetime
- Updated test fixtures to import application correctly

## Testing
- `ruff --fix apps/api/tests/conftest.py apps/api/tests/test_api_routers_basic.py apps/api/tests/test_system_health.py apps/api/main.py apps/api/middleware/error_handler.py apps/api/middleware/request_logging.py`
- `mypy apps/api` *(fails: many errors)*
- `pytest -q apps/api/tests/test_system_health.py apps/api/tests/test_api_routers_basic.py` *(fails: 3 failed, 1 passed)*
