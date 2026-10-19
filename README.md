# fastapi-template

[fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices)를 따르는 FastAPI 템플릿.
Python 3.14 · uv · async SQLAlchemy 2 · Alembic · pydantic-settings · JWT(pwdlib/argon2).

## 시작하기

```bash
cp .env.example .env
make install      # uv sync
make db           # docker compose up -d db (Postgres 17)
make migrate      # alembic upgrade head
make run          # fastapi dev → http://localhost:8000/docs
```

```bash
make check        # lint + typecheck + deps + audit + test (CI와 동일)
make cov          # 커버리지 (htmlcov/)
make security     # bandit 룰(ruff S) + 의존성 CVE
make migration m="add post_like table"
```

## 품질 도구

| 역할 | 도구 | 대체한 것 |
| --- | --- | --- |
| 포매팅 · import 정렬 | `ruff format`, ruff `I` | black, isort |
| 린트 · 미사용 import | ruff `E W F B PL ...` | flake8, pylint, unimport |
| 보안 정적 분석 | ruff `S` | bandit |
| 타입 체크 | mypy strict + pydantic 플러그인 | |
| 의존성 정합성 | deptry | pipreqs, pipdeptree |
| 의존성 취약점 | `uv audit` | safety |
| 테스트 · 커버리지 | pytest, pytest-asyncio, pytest-cov | coverage |
| 커밋 전 검사 | pre-commit (`make install` 시 설치) | |
| CI | `.github/workflows/ci.yml` | |

테스트는 기본으로 in-memory SQLite를 쓰고, `TEST_DATABASE_URL`을 지정하면 Postgres로 돌아간다.

## 구조

도메인 단위 패키지. 각 도메인은 필요한 파일만 가진다.

```
src/
├── auth/                # 도메인 예시 1: 회원가입 · 토큰 발급 · /me
│   ├── router.py        # 엔드포인트
│   ├── schemas.py       # Pydantic 모델
│   ├── models.py        # SQLAlchemy 모델
│   ├── dependencies.py  # 검증 · 인증 의존성
│   ├── service.py       # 비즈니스 로직 / DB 접근
│   ├── security.py      # 해싱 · JWT
│   ├── config.py        # 도메인 전용 설정 (BaseSettings)
│   ├── constants.py
│   └── exceptions.py
├── posts/               # 도메인 예시 2: CRUD + 체인 의존성
├── config.py            # 전역 설정
├── constants.py         # Environment, DB naming convention
├── database.py          # engine, Base, DbSession
├── exceptions.py        # 전역 HTTP 예외
├── models.py            # 모든 도메인 모델 등록 (Alembic용)
├── pagination.py
├── schemas.py           # CustomModel (전역 Pydantic 베이스)
└── main.py
```

다른 도메인 import는 모듈 이름을 명시한다: `from src.auth import service as auth_service`.

## 적용한 best practices

| 항목 | 위치 |
| --- | --- |
| 도메인별 `src/` 구조 | `src/auth`, `src/posts` |
| async 라우트 + async 드라이버(asyncpg) | 전 라우트 |
| 커스텀 Pydantic 베이스 모델 (datetime 직렬화 통일) | `src/schemas.py` |
| `BaseSettings`를 도메인별로 분리 | `src/config.py`, `src/auth/config.py` |
| 의존성으로 요청 검증 (DB 조회 포함) | `valid_user_create`, `valid_post_id` |
| 체인 의존성 + 요청 내 캐시 | `valid_owned_post` → `valid_post_id`, `get_current_user` |
| REST 경로 변수명 통일 → 의존성 재사용 | `/posts/{post_id}` |
| 운영 환경에서 docs 숨김 | `src/config.py` (`ENVIRONMENT`) |
| DB 제약조건 naming convention | `src/constants.py` |
| 테이블명 lower_snake, 단수형, 모듈 prefix · `_at` 접미사 | `auth_user`, `post`, `created_at` |
| 마이그레이션 파일명 `날짜_slug` | `alembic.ini` `file_template` |
| async 테스트 클라이언트 (httpx `ASGITransport`) | `tests/conftest.py` |
| ruff 단일 린터/포매터 | `pyproject.toml` |

## 컨벤션

- 라우트는 `async def`. 블로킹 SDK는 `run_in_threadpool`으로 감싸고, CPU 작업은 워커로 분리한다.
- 응답 모델은 반환 타입 어노테이션으로 선언한다 (`-> PostResponse`).
- 트랜잭션은 요청 단위(unit of work). `DbSession`이 라우트 종료 시 커밋, 예외 시 롤백한다. service는 `flush()`만 하고 `commit()`하지 않는다.
- 도메인 예외는 `src/exceptions.py`의 클래스를 상속해서 `DETAIL`만 바꾼다.
- 새 모델을 추가하면 `src/models.py`에 import 해야 Alembic autogenerate가 인식한다.
