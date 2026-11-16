# Demo QuestDB: monitoreo de sensores IoT en tiempo real

Simulador de 5 sensores (temperatura, humedad, vibración) que escribe en QuestDB por ILP sobre HTTP y un dashboard de Grafana que consulta por el protocolo PostgreSQL.

```
simulador (Python, ILP/HTTP :9000) --> QuestDB --> Grafana (pgwire :8812)
```

## Requisitos
- Docker Desktop (o Docker Engine + Compose v2)
- Puertos libres: 9000, 8812, 3000

## Ejecución
```bash
docker compose up -d --build
docker compose logs -f simulador     # debe mostrar "5 lecturas enviadas" cada segundo
```

| Servicio | URL | Credenciales |
|---|---|---|
| Consola QuestDB | http://localhost:9000 | sin autenticación (versión open source) |
| Grafana | http://localhost:3000 | admin / admin |

El dashboard "Monitoreo de sensores IoT (QuestDB)" se abre como página de inicio de Grafana y se actualiza cada 5 s.

## Consultas de la demo
Abrir la consola web y pegar las consultas de `consultas.sql` (últimas lecturas, `LATEST ON`, `SAMPLE BY`, alertas, resumen por ubicación y `table_partitions`).

## Detener
```bash
docker compose down        # conserva los datos
docker compose down -v     # borra también los volúmenes
```

## Solución de problemas
- **Grafana sin datos:** esperar ~10 s tras el arranque; verificar en Connections > Data sources > QuestDB > "Save & test". Usuario `admin`, contraseña `quest`, base `qdb`, SSL desactivado.
- **Tabla vacía:** `docker compose logs simulador`.
- **Puerto ocupado:** cambiar el mapeo en `docker-compose.yml`.
