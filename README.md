# Bottling System Reporting Adoption Lab

I built this because bottling system BI reporting adoption needs more than a dashboard: it needs a decision artifact that connects source data, analysis, and next actions.

![Bottling System Reporting Adoption Lab](docs/images/dashboard.png)

## What this project is

This project is a lab for bottling system BI reporting adoption. It uses synthetic but workflow-shaped data to rank reporting product-level risks and convert the output into stakeholder-ready recommendations.

## Data sources

- `entities.csv` - 36 reporting product records
- `daily_metrics.csv` - 5,040 daily operating rows
- `source_events.csv` - 760 event, exception, QA, and stakeholder-request records
- `recommended_actions.csv` - 220 action candidates

## Analysis outputs

- `analysis/executive_findings.md`
- `analysis/analysis_plan.md`
- `analysis/sql_checks.sql`
- `analysis/outputs/priority_queue.csv`

## Recommendation

Use the priority queue to focus stakeholder attention on the reporting product segments where performance upside, measurement risk, and operational readiness overlap.

## Run locally

```bash
python3 -m http.server 4173
```
