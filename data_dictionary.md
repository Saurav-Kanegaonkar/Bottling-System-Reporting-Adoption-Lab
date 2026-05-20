# Data Dictionary

## Source Tables

| Table | Grain | Key fields | Purpose |
|---|---|---|---|
| `entities.csv` | report asset | `report_id`, `domain`, `audience`, `owner_group`, `source_system`, `decision_value` | Catalog of BI reporting products and ownership context |
| `daily_metrics.csv` | report by day | `date`, `report_id`, `active_users`, `target_users`, `quality_score`, `refresh_latency_minutes` | Adoption, usage, report performance, quality, and ticket signals |
| `refresh_runs.csv` | refresh run | `run_id`, `date`, `report_id`, `status`, `sla_met`, `failure_reason` | Refresh reliability and performance evidence |
| `quality_checks.csv` | validation check | `check_id`, `report_id`, `check_type`, `severity`, `result`, `recommended_fix` | Data quality controls across freshness, completeness, uniqueness, reconciliation, and schema drift |
| `lineage_map.csv` | report dependency | `lineage_id`, `report_id`, `source_system`, `pipeline_stage`, `dependency_tier`, `open_exception` | Source lineage and dependency risk evidence |
| `metric_definitions.csv` | metric definition | `metric_id`, `report_id`, `metric_name`, `business_definition`, `grain`, `certification_state` | Metric catalog and semantic model readiness |
| `stakeholder_requests.csv` | request | `request_id`, `report_id`, `request_type`, `priority`, `age_days`, `requirement_clarity` | Reporting services intake and requirement clarity |
| `documentation_assets.csv` | documentation asset | `doc_id`, `report_id`, `doc_type`, `status`, `last_reviewed_days` | Documentation coverage and review state |
| `training_sessions.csv` | session | `session_id`, `report_id`, `audience`, `attendance`, `satisfaction_score`, `adoption_lift_pct` | Training and adoption support |
| `source_events.csv` | operating event | `event_id`, `event_date`, `report_id`, `event_type`, `severity`, `estimated_impact` | Reporting events and service history |
| `recommended_actions.csv` | action | `action_id`, `report_id`, `action_type`, `expected_lift_pct`, `effort_hours`, `status` | Candidate remediation and adoption actions |

## Output Tables

| Table | Grain | Purpose |
|---|---|---|
| `analysis/outputs/priority_queue.csv` | report asset | Ranked portfolio triage with lane and next action |
| `analysis/outputs/refresh_quality_summary.csv` | report asset | Refresh, SLA, quality check, and fix theme summary |
| `analysis/outputs/lineage_quality_queue.csv` | report dependency | Ranked source dependency risk queue |
| `analysis/outputs/adoption_documentation_queue.csv` | report asset | Adoption, training, documentation, request clarity, and service action summary |
| `analysis/outputs/summary.json` | portfolio | Summary metrics loaded by the browser UI |

## Scoring Inputs

The priority score combines decision value, quality gap, failed quality checks, refresh failures, SLA misses, adoption gap, urgent stakeholder requests, ambiguous requirements, stale documentation, uncertified metrics, and critical lineage exceptions.
