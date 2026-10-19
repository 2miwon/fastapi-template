# fastapi-template

Follows https://github.com/zhanymkanov/fastapi-best-practices. See README.md for layout and conventions.

- Package manager: uv (`uv add`, `uv run`). Never use pip.
- Verify with `make check` (ruff, mypy strict, deptry, uv audit, pytest) before claiming done. Don't add `# noqa`/`# type: ignore` without a reason in the comment.
- New domain → `src/<domain>/` with router/schemas/models/service/dependencies/exceptions as needed; register its router in `src/main.py` and its models in `src/models.py`.
- Schemas extend `src.schemas.CustomModel`; exceptions extend classes in `src/exceptions.py`.
- Put request validation that needs the DB in `dependencies.py`, not in the route body.
- One transaction per request (`DbSession`, scope="function"). Services `flush()`, never `commit()`. Routes stay thin.
- Migrations: `make migration m="..."`, then review the generated file.
