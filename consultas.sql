-- Consultas para la consola web de QuestDB (http://localhost:9000)

-- 1. Ultimas lecturas
SELECT * FROM sensores ORDER BY ts DESC LIMIT 20;

-- 2. Ultimo valor de cada sensor (LATEST ON)
SELECT * FROM sensores LATEST ON ts PARTITION BY sensor_id;

-- 3. Promedio por minuto y por sensor (SAMPLE BY)
SELECT ts, sensor_id, avg(temperatura) AS temp_prom, max(temperatura) AS temp_max
FROM sensores
WHERE ts > dateadd('h', -1, now())
SAMPLE BY 1m;

-- 4. Alertas: temperaturas superiores a 30 C en los ultimos 15 minutos
SELECT ts, sensor_id, ubicacion, temperatura
FROM sensores
WHERE temperatura > 30 AND ts > dateadd('m', -15, now())
ORDER BY ts DESC;

-- 5. Resumen por ubicacion
SELECT ubicacion, count() AS lecturas, avg(temperatura) AS temp_prom, max(vibracion) AS vib_max
FROM sensores
WHERE ts > dateadd('h', -1, now());

-- 6. Particiones de la tabla (para mostrar el almacenamiento por tiempo)
SELECT * FROM table_partitions('sensores');
