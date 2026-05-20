# Power BI Measure Catalog

These DAX-style measures show how the synthetic reporting operations data could be translated into reusable Power BI measures. They are examples for portfolio analysis and are not connected to a real workspace.

## Adoption

```DAX
Adoption Rate =
DIVIDE(
    SUM(daily_metrics[active_users]),
    SUM(daily_metrics[target_users])
)
```

```DAX
Adoption Gap =
MAX(0, 0.78 - [Adoption Rate])
```

## Quality

```DAX
Average Quality Score =
AVERAGE(daily_metrics[quality_score])
```

```DAX
Failed Quality Checks =
CALCULATE(
    COUNTROWS(quality_checks),
    quality_checks[result] = "Fail"
)
```

## Refresh Reliability

```DAX
Refresh Success Rate =
DIVIDE(
    CALCULATE(COUNTROWS(refresh_runs), refresh_runs[status] <> "Failed"),
    COUNTROWS(refresh_runs)
)
```

```DAX
Refresh SLA Misses =
CALCULATE(
    COUNTROWS(refresh_runs),
    refresh_runs[sla_met] = "No"
)
```

## Documentation and Certification

```DAX
Current Documentation Coverage =
DIVIDE(
    CALCULATE(COUNTROWS(documentation_assets), documentation_assets[status] = "Current"),
    COUNTROWS(documentation_assets)
)
```

```DAX
Certified Metric Coverage =
DIVIDE(
    CALCULATE(COUNTROWS(metric_definitions), metric_definitions[certification_state] = "Certified"),
    COUNTROWS(metric_definitions)
)
```

## Stakeholder Service

```DAX
Urgent Open Requests =
CALCULATE(
    COUNTROWS(stakeholder_requests),
    stakeholder_requests[status] <> "Closed",
    stakeholder_requests[priority] IN {"High", "Critical"}
)
```

```DAX
Ambiguous Open Requests =
CALCULATE(
    COUNTROWS(stakeholder_requests),
    stakeholder_requests[status] <> "Closed",
    stakeholder_requests[requirement_clarity] <> "Clear"
)
```
