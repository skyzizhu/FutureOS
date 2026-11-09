"""Database defence for private ownership, initial pointers and one-report ledger."""

from alembic import op

revision = "0008_m4_private_guards"
down_revision = "0007_m4"
branch_labels = None
depends_on = None

TABLES = (
    "user_reports",
    "entitlement_reservations",
    "usage_ledger",
    "report_version_forecasts",
    "personal_impacts",
    "recommendations",
)


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("""CREATE FUNCTION futureos_m4_private_guard() RETURNS trigger
        LANGUAGE plpgsql AS $$ BEGIN
          IF TG_TABLE_NAME='user_reports' THEN
            IF NEW.current_version_id IS NOT NULL THEN RAISE EXCEPTION 'M4_INITIAL_POINTER'; END IF;
          ELSIF TG_TABLE_NAME='entitlement_reservations' THEN
            IF NEW.state<>'reserved' OR NEW.expires_at<=CURRENT_TIMESTAMP
              OR NOT EXISTS(SELECT 1 FROM jobs j WHERE j.id=NEW.job_id AND j.user_id=NEW.user_id
                AND j.task_type='m4_report')
              OR EXISTS(SELECT 1 FROM usage_ledger l WHERE l.user_id=NEW.user_id
                AND l.entry_kind='consumed') THEN RAISE EXCEPTION 'M4_RESERVATION_OWNER'; END IF;
          ELSIF TG_TABLE_NAME='usage_ledger' THEN
            IF NOT EXISTS(SELECT 1 FROM entitlement_reservations r WHERE r.id=NEW.reservation_id
              AND r.user_id=NEW.user_id AND r.job_id=NEW.job_id
              AND ((NEW.entry_kind='released' AND r.state='released')
                OR (NEW.entry_kind='consumed' AND r.state='consumed' AND EXISTS(
                  SELECT 1 FROM prediction_requests q JOIN user_report_versions v
                  ON v.profile_snapshot_id=q.profile_snapshot_id AND v.user_id=q.user_id
                  WHERE q.job_id=NEW.job_id AND q.user_id=NEW.user_id))))
            THEN RAISE EXCEPTION 'M4_LEDGER_REQUIRES_COMPLETED_REPORT'; END IF;
          ELSIF TG_TABLE_NAME='report_version_forecasts' THEN
            IF NOT EXISTS(SELECT 1 FROM user_report_versions r JOIN forecast_versions v
              ON r.label=v.label WHERE r.id=NEW.report_version_id AND v.id=NEW.forecast_version_id)
            THEN RAISE EXCEPTION 'M4_REPORT_LABEL_MISMATCH'; END IF;
          ELSIF TG_TABLE_NAME='personal_impacts' THEN
            IF NOT EXISTS(SELECT 1 FROM user_report_versions r JOIN report_version_forecasts f
              ON f.report_version_id=r.id WHERE r.id=NEW.report_version_id
              AND r.user_id=NEW.user_id AND r.profile_snapshot_id=NEW.profile_snapshot_id
              AND f.forecast_version_id=NEW.forecast_version_id)
            THEN RAISE EXCEPTION 'M4_IMPACT_INPUT_MISMATCH'; END IF;
          ELSIF TG_TABLE_NAME='recommendations' THEN
            IF NOT EXISTS(SELECT 1 FROM personal_impacts i WHERE i.id=NEW.impact_id
              AND i.user_id=NEW.user_id AND i.report_version_id=NEW.report_version_id)
            THEN RAISE EXCEPTION 'M4_RECOMMENDATION_OWNER'; END IF;
          END IF;
          RETURN NEW;
        END; $$""")
        for table in TABLES:
            op.execute(
                f"CREATE TRIGGER m4_private_insert BEFORE INSERT ON {table} "
                "FOR EACH ROW EXECUTE FUNCTION futureos_m4_private_guard()"
            )
    else:
        conditions = {
            "user_reports": ("NEW.current_version_id IS NOT NULL", "M4_INITIAL_POINTER"),
            "entitlement_reservations": (
                """NEW.state<>'reserved'
              OR julianday(NEW.expires_at)<=julianday('now')
              OR NOT EXISTS(SELECT 1 FROM jobs j WHERE j.id=NEW.job_id AND j.user_id=NEW.user_id
                AND j.task_type='m4_report')
              OR EXISTS(SELECT 1 FROM usage_ledger l WHERE l.user_id=NEW.user_id
                AND l.entry_kind='consumed')""",
                "M4_RESERVATION_OWNER",
            ),
            "usage_ledger": (
                """NOT EXISTS(SELECT 1 FROM entitlement_reservations r
              WHERE r.id=NEW.reservation_id AND r.user_id=NEW.user_id AND r.job_id=NEW.job_id
              AND ((NEW.entry_kind='released' AND r.state='released')
                OR (NEW.entry_kind='consumed' AND r.state='consumed' AND EXISTS(
                  SELECT 1 FROM prediction_requests q JOIN user_report_versions v
                  ON v.profile_snapshot_id=q.profile_snapshot_id AND v.user_id=q.user_id
                  WHERE q.job_id=NEW.job_id AND q.user_id=NEW.user_id))))""",
                "M4_LEDGER_REQUIRES_COMPLETED_REPORT",
            ),
            "report_version_forecasts": (
                """NOT EXISTS(SELECT 1 FROM user_report_versions r
              JOIN forecast_versions v ON r.label=v.label WHERE r.id=NEW.report_version_id
              AND v.id=NEW.forecast_version_id)""",
                "M4_REPORT_LABEL_MISMATCH",
            ),
            "personal_impacts": (
                """NOT EXISTS(SELECT 1 FROM user_report_versions r
              JOIN report_version_forecasts f ON f.report_version_id=r.id
              WHERE r.id=NEW.report_version_id AND r.user_id=NEW.user_id
              AND r.profile_snapshot_id=NEW.profile_snapshot_id
              AND f.forecast_version_id=NEW.forecast_version_id)""",
                "M4_IMPACT_INPUT_MISMATCH",
            ),
            "recommendations": (
                """NOT EXISTS(SELECT 1 FROM personal_impacts i WHERE i.id=NEW.impact_id
              AND i.user_id=NEW.user_id AND i.report_version_id=NEW.report_version_id)""",
                "M4_RECOMMENDATION_OWNER",
            ),
        }
        for table, (condition, message) in conditions.items():
            op.execute(
                f"CREATE TRIGGER m4_private_insert_{table} BEFORE INSERT ON {table} "
                f"WHEN {condition} BEGIN SELECT RAISE(ABORT,'{message}'); END"
            )


def downgrade() -> None:
    pg = op.get_bind().dialect.name == "postgresql"
    for table in TABLES:
        op.execute(
            f"DROP TRIGGER m4_private_insert ON {table}"
            if pg
            else f"DROP TRIGGER m4_private_insert_{table}"
        )
    if pg:
        op.execute("DROP FUNCTION futureos_m4_private_guard()")
