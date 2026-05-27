-- Demostracion academica: actualizacion atomica de score y evento de auditoria.
-- Este bloque debe ejecutarse despues de cargar datos demo.

BEGIN;

WITH target_process AS (
    SELECT process_id
    FROM procurement_process
    ORDER BY publication_date DESC NULLS LAST, process_id
    LIMIT 1
), inserted_assessment AS (
    INSERT INTO risk_assessment (
        process_id,
        priority_score,
        confidence_score,
        anomaly_score,
        peer_deviation_score,
        rule_score,
        explanation
    )
    SELECT
        process_id,
        65,
        80,
        60,
        70,
        55,
        'Demo transaccional: priorizacion de revision humana, no acusacion.'
    FROM target_process
    RETURNING risk_assessment_id, process_id
)
INSERT INTO audit_log(table_name, operation, row_pk, new_data)
SELECT
    'risk_assessment',
    'MANUAL',
    risk_assessment_id::TEXT,
    jsonb_build_object('process_id', process_id, 'demo', true)
FROM inserted_assessment;

COMMIT;

-- Ejemplo de rollback controlado.
BEGIN;
INSERT INTO audit_log(table_name, operation, row_pk, new_data)
VALUES ('risk_assessment', 'MANUAL', 'rollback-demo', '{"demo": true}'::jsonb);
ROLLBACK;
