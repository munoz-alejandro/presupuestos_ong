-- Porcentaje de ejecucion de fondos por cada proyecto registrado.
-- Ejecucion = total gastado por ordenes de compra / total recibido por donaciones.
SELECT
    p.id,
    p.codigo,
    p.nombre,
    COALESCE(d.total_donado, 0) AS total_donado,
    COALESCE(oc.total_gastado, 0) AS total_gastado,
    CASE
        WHEN COALESCE(d.total_donado, 0) = 0 THEN 0
        ELSE ROUND((COALESCE(oc.total_gastado, 0) * 100.0) / d.total_donado, 2)
    END AS porcentaje_ejecucion
FROM organizaciones_proyecto AS p
LEFT JOIN (
    SELECT proyecto_id, SUM(monto) AS total_donado
    FROM organizaciones_donacion
    GROUP BY proyecto_id
) AS d ON d.proyecto_id = p.id
LEFT JOIN (
    SELECT oc.proyecto_id, SUM(loc.monto) AS total_gastado
    FROM organizaciones_ordencompra AS oc
    JOIN organizaciones_lineaordencompra AS loc ON loc.orden_compra_id = oc.id
    GROUP BY oc.proyecto_id
) AS oc ON oc.proyecto_id = p.id
ORDER BY p.codigo;

-- Disponibilidad de fondos por cada rubro de presupuesto de un proyecto.
-- Reemplazar :proyecto_id con el id del proyecto deseado.
SELECT
    pr.id,
    pr.rubro,
    COALESCE(d.total_donado, 0) AS total_donado,
    COALESCE(oc.total_gastado, 0) AS total_gastado,
    COALESCE(d.total_donado, 0) - COALESCE(oc.total_gastado, 0) AS disponible
FROM organizaciones_presupuesto AS pr
LEFT JOIN (
    SELECT presupuesto_id, SUM(monto) AS total_donado
    FROM organizaciones_donacion
    GROUP BY presupuesto_id
) AS d ON d.presupuesto_id = pr.id
LEFT JOIN (
    SELECT presupuesto_id, SUM(monto) AS total_gastado
    FROM organizaciones_lineaordencompra
    GROUP BY presupuesto_id
) AS oc ON oc.presupuesto_id = pr.id
WHERE pr.proyecto_id = 5
ORDER BY pr.rubro;
