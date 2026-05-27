CREATE OR REPLACE PROCEDURE recompute_demo_priority_score(target_process_id BIGINT)
LANGUAGE plpgsql
AS $$
DECLARE
    new_priority NUMERIC(5,2);
    new_confidence NUMERIC(5,2);
BEGIN
    SELECT
        LEAST(100, GREATEST(0,
            CASE WHEN response_count <= 1 THEN 30 ELSE 10 END
            + CASE WHEN base_price > 0 THEN 30 ELSE 5 END
            + CASE WHEN status IS NOT NULL THEN 20 ELSE 5 END
        )),
        CASE WHEN length(description) > 40 THEN 80 ELSE 55 END
    INTO new_priority, new_confidence
    FROM procurement_process
    WHERE process_id = target_process_id;

    IF new_priority IS NULL THEN
        RAISE EXCEPTION 'process_id % does not exist', target_process_id;
    END IF;

    INSERT INTO risk_assessment(
        process_id, priority_score, confidence_score, anomaly_score,
        peer_deviation_score, rule_score, explanation
    )
    VALUES (
        target_process_id, new_priority, new_confidence, new_priority,
        new_priority, new_priority,
        'Recalculo transaccional para priorizacion de revision humana.'
    );

    INSERT INTO audit_log(table_name, operation, row_pk, new_data)
    VALUES (
        'risk_assessment', 'MANUAL', target_process_id::TEXT,
        jsonb_build_object('process_id', target_process_id, 'priority_score', new_priority)
    );
END;
$$;
