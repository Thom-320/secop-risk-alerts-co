DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'contratia_analyst_readonly') THEN
        CREATE ROLE contratia_analyst_readonly;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'contratia_reviewer') THEN
        CREATE ROLE contratia_reviewer;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'contratia_admin') THEN
        CREATE ROLE contratia_admin;
    END IF;
END $$;

GRANT USAGE ON SCHEMA public TO contratia_analyst_readonly, contratia_reviewer, contratia_admin;

GRANT SELECT ON
    v_ranking_processes,
    v_entity_provider_concentration,
    v_value_outliers_by_modality,
    v_plan_vs_execution,
    v_fiscal_context,
    v_administrative_hierarchy_tree
TO contratia_analyst_readonly;

GRANT SELECT ON
    v_ranking_processes,
    v_entity_provider_concentration,
    v_value_outliers_by_modality,
    v_plan_vs_execution,
    v_fiscal_context,
    v_administrative_hierarchy_tree
TO contratia_reviewer;

GRANT SELECT, INSERT, UPDATE ON human_review TO contratia_reviewer;
GRANT USAGE, SELECT ON SEQUENCE human_review_human_review_id_seq TO contratia_reviewer;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO contratia_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO contratia_admin;
