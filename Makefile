.PHONY: install migrate seed contracts check lint typecheck test build api worker web up smoke local-install local-verify down
install:
	uv sync --locked
	npm ci --no-fund --no-audit
migrate:
	uv run alembic upgrade head
seed:
	uv run python -m scripts.seed_demo
contracts:
	npm run contracts
lint:
	uv run ruff check apps/api services infra workers scripts tests
	uv run ruff format --check apps/api services infra workers scripts tests
	npm run lint
typecheck:
	uv run mypy apps/api services/prediction_engine infra/db.py infra/community.py infra/consumer_social.py infra/community_seed.py infra/conversations.py infra/chat_agent.py infra/chat_harness.py infra/chat_admission.py infra/chat_research.py infra/evidence_repository.py infra/research_repository.py infra/review_repository.py infra/critic_runner.py infra/accounts.py infra/admin_security.py infra/account_security.py infra/human_verification.py infra/privacy.py infra/personal_data.py infra/erasure_policy.py infra/erasure_journal.py infra/profiles.py infra/reports.py infra/report_demo.py infra/monitoring.py infra/billing.py infra/paid_research.py infra/costs.py infra/job_budget.py infra/operations.py infra/backup.py infra/updates.py infra/notifications.py infra/engine_artifacts.py infra/research_demo.py infra/settings.py infra/providers workers scripts/seed_demo.py scripts/export_contracts.py scripts/industry_agent.py
	npm run typecheck
test:
	uv run pytest -q
build:
	npm run build
check: lint typecheck test
api:
	uv run uvicorn apps.api.main:app --host 127.0.0.1 --port 8100 --log-config infra/logging.json --no-access-log --no-proxy-headers
worker:
	uv run python -m workers.research.main
web:
	DEMO_MODE=true npm run dev --workspace @futureos/web -- --port 3100 --hostname 127.0.0.1
local-install:
	uv sync --locked --group local
	uv run --group local python -m scripts.setup_postgres
up:
	uv run --group local python -m scripts.local_stack
local-verify:
	uv run --group local python -m scripts.local_stack --verify
smoke:
	uv run python -m scripts.smoke
down:
	uv run --group local python -m scripts.local_stack --stop

backup-drill:
	uv run --group local python -m scripts.backup_drill

admin-bootstrap:
	uv run python -m scripts.admin_bootstrap
