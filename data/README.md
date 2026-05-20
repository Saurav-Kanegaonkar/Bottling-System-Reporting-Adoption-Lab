# Data Sources

All data in this folder is synthetic and generated with a fixed random seed by `scripts/generate_bi_data.py`.

The datasets model a shared-services BI reporting environment for a beverage bottling system. They do not represent real company, customer, bottler, invoice, retailer, employee, or point-of-sale data.

| File | Grain | Rows | Purpose |
|---|---:|---:|---|
| `entities.csv` | report asset | 32 | Reporting product catalog and ownership context |
| `daily_metrics.csv` | report by day | 4,480 | Adoption, performance, latency, quality, and ticket signals |
| `refresh_runs.csv` | refresh run | 1,920 | Refresh reliability, SLA, rows processed, and failure reason |
| `quality_checks.csv` | validation check | 192 | Freshness, completeness, uniqueness, reconciliation, and schema checks |
| `lineage_map.csv` | source dependency | 160 | Source system, pipeline stage, owner, exception state, and impact |
| `metric_definitions.csv` | metric definition | 96 | Business definitions, grains, certification, and SQL coverage |
| `stakeholder_requests.csv` | service request | 195 | Prioritized stakeholder asks and requirement clarity |
| `documentation_assets.csv` | documentation item | 64 | Metric guides and refresh notes with review state |
| `training_sessions.csv` | training session | 77 | Attendance, satisfaction, follow-up asks, and adoption lift |
| `source_events.csv` | operating event | 760 | Reporting service events, severity, impact, and resolution state |
| `recommended_actions.csv` | action | 220 | Candidate actions with expected lift, effort, owner, and status |

The synthetic structure is designed to support SQL joins, aggregations, anomaly research, report portfolio prioritization, data lineage review, metric certification, documentation stewardship, and adoption analysis.
