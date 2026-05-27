CREATE OR REPLACE VIEW v_ranking_processes AS
SELECT
    p.process_id,
    p.process_key,
    p.process_reference,
    e.name AS entity_name,
    d.name AS department,
    m.name AS modality,
    p.base_price,
    ra.priority_score,
    ra.confidence_score,
    ra.explanation,
    row_number() OVER (ORDER BY ra.priority_score DESC, ra.confidence_score DESC, p.base_price DESC) AS national_rank
FROM procurement_process p
JOIN public_entity e ON e.entity_id = p.entity_id
LEFT JOIN department d ON d.department_id = e.department_id
LEFT JOIN modality m ON m.modality_id = p.modality_id
LEFT JOIN LATERAL (
    SELECT *
    FROM risk_assessment ra
    WHERE ra.process_id = p.process_id
    ORDER BY ra.assessed_at DESC
    LIMIT 1
) ra ON true;

CREATE OR REPLACE VIEW v_entity_provider_concentration AS
SELECT
    e.entity_id,
    e.name AS entity_name,
    pr.provider_id,
    pr.name AS provider_name,
    count(*) AS awarded_contracts,
    sum(c.value) AS awarded_value,
    dense_rank() OVER (PARTITION BY e.entity_id ORDER BY sum(c.value) DESC) AS provider_rank_in_entity,
    sum(c.value) / NULLIF(sum(sum(c.value)) OVER (PARTITION BY e.entity_id), 0) AS entity_value_share
FROM contract c
JOIN procurement_process p ON p.process_id = c.process_id
JOIN public_entity e ON e.entity_id = p.entity_id
LEFT JOIN provider pr ON pr.provider_id = c.provider_id
GROUP BY e.entity_id, e.name, pr.provider_id, pr.name;

CREATE OR REPLACE VIEW v_value_outliers_by_modality AS
SELECT
    p.process_id,
    p.process_key,
    d.name AS department,
    m.name AS modality,
    p.base_price,
    percent_rank() OVER (PARTITION BY d.department_id, m.modality_id ORDER BY p.base_price) AS value_percent_rank,
    ntile(10) OVER (PARTITION BY d.department_id, m.modality_id ORDER BY p.base_price) AS value_decile
FROM procurement_process p
JOIN public_entity e ON e.entity_id = p.entity_id
LEFT JOIN department d ON d.department_id = e.department_id
LEFT JOIN modality m ON m.modality_id = p.modality_id;

CREATE OR REPLACE VIEW v_plan_vs_execution AS
SELECT
    pi.paa_item_id,
    pi.item_key,
    pi.description AS paa_description,
    pi.planned_value,
    p.process_id,
    p.process_key,
    p.base_price,
    ppm.method,
    ppm.confidence,
    ppm.status AS match_status
FROM paa_item pi
LEFT JOIN paa_process_match ppm ON ppm.paa_item_id = pi.paa_item_id
LEFT JOIN procurement_process p ON p.process_id = ppm.process_id;

CREATE OR REPLACE VIEW v_fiscal_context AS
SELECT
    e.entity_id,
    e.name AS entity_name,
    fcs.subject_name,
    count(ff.fiscal_finding_id) AS findings_count,
    COALESCE(sum(ff.amount), 0) AS findings_amount
FROM public_entity e
LEFT JOIN fiscal_control_subject fcs ON fcs.entity_id = e.entity_id
LEFT JOIN fiscal_finding ff ON ff.fiscal_subject_id = fcs.fiscal_subject_id
GROUP BY e.entity_id, e.name, fcs.subject_name;

CREATE OR REPLACE VIEW v_administrative_hierarchy_tree AS
WITH RECURSIVE tree AS (
    SELECT
        node_id,
        parent_node_id,
        node_type,
        label,
        entity_id,
        0 AS depth,
        label::TEXT AS path
    FROM administrative_hierarchy
    WHERE parent_node_id IS NULL
    UNION ALL
    SELECT
        child.node_id,
        child.parent_node_id,
        child.node_type,
        child.label,
        child.entity_id,
        tree.depth + 1,
        tree.path || ' > ' || child.label
    FROM administrative_hierarchy child
    JOIN tree ON tree.node_id = child.parent_node_id
)
SELECT * FROM tree;
