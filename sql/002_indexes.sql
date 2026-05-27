CREATE INDEX IF NOT EXISTS idx_procurement_process_entity ON procurement_process(entity_id);
CREATE INDEX IF NOT EXISTS idx_procurement_process_modality ON procurement_process(modality_id);
CREATE INDEX IF NOT EXISTS idx_procurement_process_publication_date ON procurement_process(publication_date);
CREATE INDEX IF NOT EXISTS idx_procurement_process_status ON procurement_process(status);
CREATE INDEX IF NOT EXISTS idx_procurement_process_base_price ON procurement_process(base_price);
CREATE INDEX IF NOT EXISTS idx_contract_process ON contract(process_id);
CREATE INDEX IF NOT EXISTS idx_contract_provider ON contract(provider_id);
CREATE INDEX IF NOT EXISTS idx_paa_item_plan ON paa_item(plan_id);
CREATE INDEX IF NOT EXISTS idx_paa_process_match_process ON paa_process_match(process_id);
CREATE INDEX IF NOT EXISTS idx_risk_assessment_process ON risk_assessment(process_id);
CREATE INDEX IF NOT EXISTS idx_risk_assessment_priority ON risk_assessment(priority_score DESC, confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_semantic_comparable_process ON semantic_comparable(process_id, rank);
CREATE INDEX IF NOT EXISTS idx_audit_log_table_time ON audit_log(table_name, changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_public_entity_department ON public_entity(department_id);
CREATE INDEX IF NOT EXISTS idx_provider_name ON provider(name);
CREATE INDEX IF NOT EXISTS idx_human_review_process ON human_review(process_id, review_status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_administrative_hierarchy_unique
ON administrative_hierarchy(node_type, label, COALESCE(entity_id, 0));
