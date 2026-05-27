CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION write_audit_log()
RETURNS TRIGGER AS $$
DECLARE
    pk_value TEXT;
    old_json JSONB;
    new_json JSONB;
BEGIN
    IF TG_OP = 'DELETE' THEN
        old_json = to_jsonb(OLD);
        new_json = NULL;
    ELSIF TG_OP = 'INSERT' THEN
        old_json = NULL;
        new_json = to_jsonb(NEW);
    ELSE
        old_json = to_jsonb(OLD);
        new_json = to_jsonb(NEW);
    END IF;

    pk_value = COALESCE(
        new_json->>'process_id',
        old_json->>'process_id',
        new_json->>'contract_id',
        old_json->>'contract_id',
        new_json->>'paa_item_id',
        old_json->>'paa_item_id',
        new_json->>'risk_assessment_id',
        old_json->>'risk_assessment_id',
        new_json->>'human_review_id',
        old_json->>'human_review_id'
    );

    INSERT INTO audit_log(table_name, operation, row_pk, old_data, new_data)
    VALUES (TG_TABLE_NAME, TG_OP, pk_value, old_json, new_json);

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION write_process_state_history()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO process_state_history(process_id, old_status, new_status)
        VALUES (NEW.process_id, NULL, NEW.status);
    ELSIF NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO process_state_history(process_id, old_status, new_status)
        VALUES (NEW.process_id, OLD.status, NEW.status);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION validate_risk_assessment()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.process_id IS NULL THEN
        RAISE EXCEPTION 'risk_assessment requires process_id';
    END IF;
    IF NEW.priority_score < 0 OR NEW.priority_score > 100 THEN
        RAISE EXCEPTION 'priority_score must be between 0 and 100';
    END IF;
    IF NEW.confidence_score < 0 OR NEW.confidence_score > 100 THEN
        RAISE EXCEPTION 'confidence_score must be between 0 and 100';
    END IF;
    IF length(trim(NEW.explanation)) = 0 THEN
        RAISE EXCEPTION 'risk_assessment explanation cannot be empty';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_public_entity_updated_at ON public_entity;
CREATE TRIGGER trg_public_entity_updated_at
BEFORE UPDATE ON public_entity
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_provider_updated_at ON provider;
CREATE TRIGGER trg_provider_updated_at
BEFORE UPDATE ON provider
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_procurement_process_updated_at ON procurement_process;
CREATE TRIGGER trg_procurement_process_updated_at
BEFORE UPDATE ON procurement_process
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_contract_updated_at ON contract;
CREATE TRIGGER trg_contract_updated_at
BEFORE UPDATE ON contract
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_paa_item_updated_at ON paa_item;
CREATE TRIGGER trg_paa_item_updated_at
BEFORE UPDATE ON paa_item
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_risk_assessment_updated_at ON risk_assessment;
CREATE TRIGGER trg_risk_assessment_updated_at
BEFORE UPDATE ON risk_assessment
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_human_review_updated_at ON human_review;
CREATE TRIGGER trg_human_review_updated_at
BEFORE UPDATE ON human_review
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_procurement_process_audit ON procurement_process;
CREATE TRIGGER trg_procurement_process_audit
AFTER INSERT OR UPDATE OR DELETE ON procurement_process
FOR EACH ROW EXECUTE FUNCTION write_audit_log();

DROP TRIGGER IF EXISTS trg_contract_audit ON contract;
CREATE TRIGGER trg_contract_audit
AFTER INSERT OR UPDATE OR DELETE ON contract
FOR EACH ROW EXECUTE FUNCTION write_audit_log();

DROP TRIGGER IF EXISTS trg_paa_item_audit ON paa_item;
CREATE TRIGGER trg_paa_item_audit
AFTER INSERT OR UPDATE OR DELETE ON paa_item
FOR EACH ROW EXECUTE FUNCTION write_audit_log();

DROP TRIGGER IF EXISTS trg_risk_assessment_audit ON risk_assessment;
CREATE TRIGGER trg_risk_assessment_audit
AFTER INSERT OR UPDATE OR DELETE ON risk_assessment
FOR EACH ROW EXECUTE FUNCTION write_audit_log();

DROP TRIGGER IF EXISTS trg_human_review_audit ON human_review;
CREATE TRIGGER trg_human_review_audit
AFTER INSERT OR UPDATE OR DELETE ON human_review
FOR EACH ROW EXECUTE FUNCTION write_audit_log();

DROP TRIGGER IF EXISTS trg_procurement_process_state_history ON procurement_process;
CREATE TRIGGER trg_procurement_process_state_history
AFTER INSERT OR UPDATE OF status ON procurement_process
FOR EACH ROW EXECUTE FUNCTION write_process_state_history();

DROP TRIGGER IF EXISTS trg_risk_assessment_validate ON risk_assessment;
CREATE TRIGGER trg_risk_assessment_validate
BEFORE INSERT OR UPDATE ON risk_assessment
FOR EACH ROW EXECUTE FUNCTION validate_risk_assessment();
