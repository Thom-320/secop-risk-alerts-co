CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS source_dataset (
    dataset_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    owner TEXT NOT NULL DEFAULT 'datos.gov.co',
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS extraction_run (
    extraction_run_id BIGSERIAL PRIMARY KEY,
    dataset_id TEXT NOT NULL REFERENCES source_dataset(dataset_id),
    scope TEXT NOT NULL CHECK (scope IN ('demo', 'full')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('started', 'completed', 'failed')),
    rows_loaded INTEGER NOT NULL DEFAULT 0 CHECK (rows_loaded >= 0),
    message TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS department (
    department_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS municipality (
    municipality_id BIGSERIAL PRIMARY KEY,
    department_id BIGINT NOT NULL REFERENCES department(department_id),
    name TEXT NOT NULL,
    UNIQUE (department_id, name)
);

CREATE TABLE IF NOT EXISTS public_entity (
    entity_id BIGSERIAL PRIMARY KEY,
    entity_code TEXT UNIQUE,
    nit TEXT,
    name TEXT NOT NULL,
    department_id BIGINT REFERENCES department(department_id),
    municipality_id BIGINT REFERENCES municipality(municipality_id),
    entity_order TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (entity_code IS NOT NULL OR nit IS NOT NULL OR length(name) > 0)
);

CREATE TABLE IF NOT EXISTS provider (
    provider_id BIGSERIAL PRIMARY KEY,
    nit TEXT UNIQUE,
    name TEXT NOT NULL,
    department_id BIGINT REFERENCES department(department_id),
    municipality_id BIGINT REFERENCES municipality(municipality_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS modality (
    modality_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    family TEXT NOT NULL DEFAULT 'otros'
);

CREATE TABLE IF NOT EXISTS contract_type (
    contract_type_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS unspsc_category (
    unspsc_category_id BIGSERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS administrative_hierarchy (
    node_id BIGSERIAL PRIMARY KEY,
    parent_node_id BIGINT REFERENCES administrative_hierarchy(node_id),
    node_type TEXT NOT NULL CHECK (node_type IN ('country', 'department', 'municipality', 'entity')),
    label TEXT NOT NULL,
    entity_id BIGINT REFERENCES public_entity(entity_id)
);

CREATE TABLE IF NOT EXISTS procurement_process (
    process_id BIGSERIAL PRIMARY KEY,
    process_key TEXT NOT NULL UNIQUE,
    process_reference TEXT,
    entity_id BIGINT NOT NULL REFERENCES public_entity(entity_id),
    modality_id BIGINT REFERENCES modality(modality_id),
    contract_type_id BIGINT REFERENCES contract_type(contract_type_id),
    unspsc_category_id BIGINT REFERENCES unspsc_category(unspsc_category_id),
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'sin_estado',
    publication_date DATE,
    award_date DATE,
    base_price NUMERIC(18,2) NOT NULL DEFAULT 0 CHECK (base_price >= 0),
    awarded_total NUMERIC(18,2) CHECK (awarded_total IS NULL OR awarded_total >= 0),
    duration_days INTEGER CHECK (duration_days IS NULL OR duration_days >= 0),
    response_count INTEGER NOT NULL DEFAULT 0 CHECK (response_count >= 0),
    invited_suppliers INTEGER NOT NULL DEFAULT 0 CHECK (invited_suppliers >= 0),
    unique_suppliers INTEGER NOT NULL DEFAULT 0 CHECK (unique_suppliers >= 0),
    provider_id BIGINT REFERENCES provider(provider_id),
    source_url TEXT,
    source_dataset_id TEXT NOT NULL REFERENCES source_dataset(dataset_id),
    extraction_run_id BIGINT REFERENCES extraction_run(extraction_run_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (award_date IS NULL OR publication_date IS NULL OR award_date >= publication_date)
);

CREATE TABLE IF NOT EXISTS process_state_history (
    state_history_id BIGSERIAL PRIMARY KEY,
    process_id BIGINT NOT NULL REFERENCES procurement_process(process_id) ON DELETE CASCADE,
    old_status TEXT,
    new_status TEXT NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    changed_by TEXT NOT NULL DEFAULT current_user
);

CREATE TABLE IF NOT EXISTS contract (
    contract_id BIGSERIAL PRIMARY KEY,
    contract_key TEXT NOT NULL UNIQUE,
    process_id BIGINT NOT NULL REFERENCES procurement_process(process_id) ON DELETE CASCADE,
    provider_id BIGINT REFERENCES provider(provider_id),
    status TEXT NOT NULL DEFAULT 'sin_estado',
    signed_date DATE,
    start_date DATE,
    end_date DATE,
    value NUMERIC(18,2) NOT NULL DEFAULT 0 CHECK (value >= 0),
    paid_value NUMERIC(18,2) NOT NULL DEFAULT 0 CHECK (paid_value >= 0),
    source_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
);

CREATE TABLE IF NOT EXISTS annual_procurement_plan (
    plan_id BIGSERIAL PRIMARY KEY,
    plan_key TEXT NOT NULL UNIQUE,
    entity_id BIGINT NOT NULL REFERENCES public_entity(entity_id),
    year INTEGER NOT NULL CHECK (year BETWEEN 2000 AND 2100),
    version TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS paa_item (
    paa_item_id BIGSERIAL PRIMARY KEY,
    item_key TEXT NOT NULL UNIQUE,
    plan_id BIGINT NOT NULL REFERENCES annual_procurement_plan(plan_id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    expected_start_date DATE,
    expected_reception_date DATE,
    expected_duration_days INTEGER CHECK (expected_duration_days IS NULL OR expected_duration_days >= 0),
    planned_value NUMERIC(18,2) NOT NULL DEFAULT 0 CHECK (planned_value >= 0),
    modality_id BIGINT REFERENCES modality(modality_id),
    unspsc_category_id BIGINT REFERENCES unspsc_category(unspsc_category_id),
    related_process_reference TEXT,
    source_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS paa_process_match (
    paa_process_match_id BIGSERIAL PRIMARY KEY,
    paa_item_id BIGINT NOT NULL REFERENCES paa_item(paa_item_id) ON DELETE CASCADE,
    process_id BIGINT NOT NULL REFERENCES procurement_process(process_id) ON DELETE CASCADE,
    method TEXT NOT NULL CHECK (method IN ('related_process', 'semantic', 'manual', 'none')),
    confidence NUMERIC(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    status TEXT NOT NULL CHECK (status IN ('strong', 'weak', 'none')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (paa_item_id, process_id)
);

CREATE TABLE IF NOT EXISTS fiscal_control_subject (
    fiscal_subject_id BIGSERIAL PRIMARY KEY,
    entity_id BIGINT REFERENCES public_entity(entity_id),
    subject_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS fiscal_finding (
    fiscal_finding_id BIGSERIAL PRIMARY KEY,
    fiscal_subject_id BIGINT NOT NULL REFERENCES fiscal_control_subject(fiscal_subject_id) ON DELETE CASCADE,
    year INTEGER CHECK (year BETWEEN 2000 AND 2100),
    finding_type TEXT NOT NULL,
    amount NUMERIC(18,2) NOT NULL DEFAULT 0 CHECK (amount >= 0),
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS risk_rule (
    risk_rule_id BIGSERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    weight NUMERIC(6,4) NOT NULL CHECK (weight >= 0),
    active BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS risk_assessment (
    risk_assessment_id BIGSERIAL PRIMARY KEY,
    process_id BIGINT NOT NULL REFERENCES procurement_process(process_id) ON DELETE CASCADE,
    priority_score NUMERIC(5,2) NOT NULL CHECK (priority_score >= 0 AND priority_score <= 100),
    confidence_score NUMERIC(5,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 100),
    anomaly_score NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (anomaly_score >= 0 AND anomaly_score <= 100),
    peer_deviation_score NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (peer_deviation_score >= 0 AND peer_deviation_score <= 100),
    rule_score NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (rule_score >= 0 AND rule_score <= 100),
    explanation TEXT NOT NULL,
    assessed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS risk_reason (
    risk_reason_id BIGSERIAL PRIMARY KEY,
    risk_assessment_id BIGINT NOT NULL REFERENCES risk_assessment(risk_assessment_id) ON DELETE CASCADE,
    risk_rule_id BIGINT REFERENCES risk_rule(risk_rule_id),
    reason_text TEXT NOT NULL,
    contribution NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (contribution >= 0 AND contribution <= 100)
);

CREATE TABLE IF NOT EXISTS semantic_comparable (
    semantic_comparable_id BIGSERIAL PRIMARY KEY,
    process_id BIGINT NOT NULL REFERENCES procurement_process(process_id) ON DELETE CASCADE,
    comparable_process_id BIGINT NOT NULL REFERENCES procurement_process(process_id) ON DELETE CASCADE,
    similarity NUMERIC(5,4) NOT NULL CHECK (similarity >= 0 AND similarity <= 1),
    rank INTEGER NOT NULL CHECK (rank > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (process_id, comparable_process_id)
);

CREATE TABLE IF NOT EXISTS audit_log (
    audit_log_id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE', 'MANUAL')),
    row_pk TEXT,
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    changed_by TEXT NOT NULL DEFAULT current_user
);

CREATE TABLE IF NOT EXISTS app_user (
    app_user_id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'teacher', 'reviewer', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS usability_survey_response (
    usability_survey_response_id BIGSERIAL PRIMARY KEY,
    app_user_id BIGINT REFERENCES app_user(app_user_id),
    respondent_label TEXT NOT NULL,
    completed_at TIMESTAMPTZ,
    navigation_score INTEGER CHECK (navigation_score BETWEEN 1 AND 5),
    clarity_score INTEGER CHECK (clarity_score BETWEEN 1 AND 5),
    trust_score INTEGER CHECK (trust_score BETWEEN 1 AND 5),
    comments TEXT NOT NULL DEFAULT '',
    is_real_response BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS human_review (
    human_review_id BIGSERIAL PRIMARY KEY,
    process_id BIGINT NOT NULL REFERENCES procurement_process(process_id) ON DELETE CASCADE,
    app_user_id BIGINT REFERENCES app_user(app_user_id),
    reviewer_label TEXT NOT NULL DEFAULT 'reviewer_demo',
    review_status TEXT NOT NULL CHECK (
        review_status IN ('pending', 'in_review', 'reviewed', 'dismissed')
    ),
    priority_decision TEXT NOT NULL CHECK (
        priority_decision IN ('keep_priority', 'lower_priority', 'raise_priority', 'needs_more_data')
    ),
    notes TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (process_id, reviewer_label)
);

CREATE TABLE IF NOT EXISTS user_action_event (
    user_action_event_id BIGSERIAL PRIMARY KEY,
    app_user_id BIGINT REFERENCES app_user(app_user_id),
    action_type TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
