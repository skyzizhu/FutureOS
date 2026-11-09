"""Bind publication columns to immutable body and prevent forged initial pointers."""

from alembic import op

revision = "0006_m3_gate_shape"
down_revision = "0005_m3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("""CREATE FUNCTION futureos_m3_version_shape() RETURNS trigger
        LANGUAGE plpgsql AS $$ BEGIN
          IF NEW.research_as_of <> (NEW.body->>'research_as_of')::timestamptz
            OR NEW.version_num <> (SELECT coalesce(max(version_num),0)+1
                 FROM forecast_versions WHERE forecast_id=NEW.forecast_id)
            OR NEW.immutable_hash !~ '^[a-f0-9]{64}$' OR length(trim(NEW.change_reason))=0
          THEN RAISE EXCEPTION 'M3_INVALID_VERSION_SHAPE'; END IF;
          RETURN NEW;
        END; $$""")
        op.execute(
            "CREATE TRIGGER m3_version_shape BEFORE INSERT ON forecast_versions "
            "FOR EACH ROW EXECUTE FUNCTION futureos_m3_version_shape()"
        )
        op.execute("""CREATE FUNCTION futureos_m3_world_insert() RETURNS trigger
        LANGUAGE plpgsql AS $$ BEGIN
          IF NEW.current_version_id IS NOT NULL OR NEW.status <> 'internal_unreviewed'
          THEN RAISE EXCEPTION 'M3_INVALID_INITIAL_POINTER'; END IF;
          RETURN NEW;
        END; $$""")
        op.execute(
            "CREATE TRIGGER m3_world_insert BEFORE INSERT ON world_forecasts "
            "FOR EACH ROW EXECUTE FUNCTION futureos_m3_world_insert()"
        )
    else:
        op.execute("""CREATE TRIGGER m3_version_shape BEFORE INSERT ON forecast_versions
        WHEN julianday(NEW.research_as_of)<>julianday(json_extract(NEW.body,'$.research_as_of'))
          OR NEW.version_num<>(SELECT coalesce(max(version_num),0)+1 FROM forecast_versions
            WHERE forecast_id=NEW.forecast_id)
          OR length(NEW.immutable_hash)<>64 OR length(trim(NEW.change_reason))=0
        BEGIN SELECT RAISE(ABORT,'M3_INVALID_VERSION_SHAPE'); END""")
        op.execute("""CREATE TRIGGER m3_world_insert BEFORE INSERT ON world_forecasts
        WHEN NEW.current_version_id IS NOT NULL OR NEW.status <> 'internal_unreviewed'
        BEGIN SELECT RAISE(ABORT,'M3_INVALID_INITIAL_POINTER'); END""")


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP TRIGGER m3_version_shape ON forecast_versions")
        op.execute("DROP TRIGGER m3_world_insert ON world_forecasts")
        op.execute("DROP FUNCTION futureos_m3_version_shape()")
        op.execute("DROP FUNCTION futureos_m3_world_insert()")
    else:
        op.execute("DROP TRIGGER m3_version_shape")
        op.execute("DROP TRIGGER m3_world_insert")
