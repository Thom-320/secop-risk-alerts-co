INSERT INTO source_dataset(dataset_id, name, source_url, description)
VALUES
    ('p6dx-8zbt', 'SECOP II Procesos de Contratacion', 'https://www.datos.gov.co/resource/p6dx-8zbt.json', 'Procesos de contratacion SECOP II'),
    ('rpmr-utcd', 'SECOP Integrado', 'https://www.datos.gov.co/resource/rpmr-utcd.json', 'Contratos y procesos integrados'),
    ('9sue-ezhx', 'SECOP II Plan Anual de Adquisiciones Detalle', 'https://www.datos.gov.co/resource/9sue-ezhx.json', 'Detalle PAA'),
    ('wasc-xi4h', 'Ejecucion plan vigilancia control fiscal', 'https://www.datos.gov.co/resource/wasc-xi4h.json', 'Contexto fiscal visible')
ON CONFLICT (dataset_id) DO UPDATE
SET name = EXCLUDED.name,
    source_url = EXCLUDED.source_url,
    description = EXCLUDED.description;

INSERT INTO risk_rule(code, name, description, weight)
VALUES
    ('LOW_COMPETITION', 'Baja competencia visible', 'Pocas respuestas o proveedores unicos pueden requerir revision humana.', 0.25),
    ('VALUE_OUTLIER', 'Valor atipico frente a pares', 'El valor se aleja de procesos comparables por modalidad y departamento.', 0.35),
    ('DIRECT_MODALITY', 'Modalidad de contratacion directa', 'La modalidad puede requerir trazabilidad adicional segun contexto.', 0.20),
    ('PAA_WEAK_MATCH', 'Plan vs ejecucion debil', 'El enlace con PAA existe pero no es fuerte.', 0.20)
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name,
    description = EXCLUDED.description,
    weight = EXCLUDED.weight;

INSERT INTO app_user(email, display_name, role)
VALUES ('demo@transparencia360.local', 'Usuario demo', 'reviewer')
ON CONFLICT (email) DO NOTHING;
