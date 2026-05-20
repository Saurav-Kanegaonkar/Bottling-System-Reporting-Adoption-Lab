import csv
import random
from datetime import date, timedelta
from pathlib import Path


random.seed(42)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


domains = [
    ("Customer Programs", "customer program funding and compliance"),
    ("Retailer POS", "sell-through and syndicated retail performance"),
    ("Bottler Invoice", "invoice-level bottler sales and adjustments"),
    ("Distributor Data", "secondary sales and distributor reconciliation"),
    ("Customer Hierarchy", "customer, banner, outlet, and route alignment"),
    ("FP&A Planning", "forecasting, plan variance, and scenario routines"),
]

audiences = [
    "national customer team",
    "bottler finance leads",
    "category management",
    "field sales operations",
    "supply planning",
    "commercial leadership",
]

owners = [
    "BI delivery",
    "data strategy",
    "reporting services",
    "customer data operations",
    "finance analytics",
    "governance and training",
]

sources = [
    "customer EDI gateway",
    "bottler invoice hub",
    "retailer POS feed",
    "customer hierarchy master",
    "trade program system",
    "planning workbook intake",
    "distributor reconciliation feed",
]

workspaces = [
    "Commercial Insights",
    "Customer Operations",
    "Bottler Finance",
    "Planning and Forecasting",
    "Reporting Services",
]

report_names = [
    "National Customer Scorecard",
    "Bottler Invoice Reconciliation",
    "Retailer POS Sell-Through",
    "Trade Program Funding Tracker",
    "Customer Hierarchy Health",
    "Distributor Volume Bridge",
    "Forecast Variance Review",
    "Outlet Segmentation Monitor",
    "Pricing Exception Digest",
    "Customer Onboarding Readiness",
    "Promotion Compliance View",
    "Route-to-Market Snapshot",
    "Monthly Business Review Pack",
    "Invoice Adjustment Explorer",
    "Retailer Data Quality Pulse",
    "Bottler Performance Summary",
    "Program Accrual Watchlist",
    "Executive KPI Overview",
    "Channel Penetration Trends",
    "Stakeholder Request Backlog",
    "Store Count Reconciliation",
    "Funding Claim Audit",
    "Planning Assumption Tracker",
    "Data Stewardship Queue",
    "Power BI Usage and Training",
    "Source Refresh Reliability",
    "Metric Definition Catalog",
    "Variance Contribution Workbench",
    "Churn and Penetration Monitor",
    "Change Contribution Review",
    "Sales Team Service Desk",
    "External Reporting Package",
]


def build_reports():
    rows = []
    for index, name in enumerate(report_names, start=1):
        domain, context = domains[(index - 1) % len(domains)]
        complexity = random.choice(["Low", "Medium", "High"])
        decision_value = random.randint(55, 240) * 1000
        rows.append(
            {
                "report_id": f"RPT{index:03d}",
                "report_name": name,
                "domain": domain,
                "business_context": context,
                "audience": audiences[(index + 1) % len(audiences)],
                "owner_group": owners[(index + 2) % len(owners)],
                "workspace": workspaces[index % len(workspaces)],
                "source_system": sources[index % len(sources)],
                "refresh_cadence": random.choice(["Daily", "Daily", "Weekly", "Intraday"]),
                "power_bi_asset_type": random.choice(["Dashboard", "Semantic model", "Paginated report", "Dataflow"]),
                "complexity": complexity,
                "rls_required": random.choice(["Yes", "No", "Yes"]),
                "decision_value": decision_value,
                "doc_status": random.choice(["Current", "Needs update", "Missing"]),
                "published_state": random.choice(["Certified", "Promoted", "Draft", "Legacy"]),
            }
        )
    return rows


def build_daily_metrics(reports):
    rows = []
    start = date.today() - timedelta(days=139)
    for report in reports:
        base_quality = random.uniform(82, 98)
        base_adoption = random.uniform(0.48, 0.92)
        base_latency = random.uniform(18, 160)
        for offset in range(140):
            day = start + timedelta(days=offset)
            weekday_lift = 1.08 if day.weekday() in [1, 2, 3] else 0.88
            quality = max(62, min(99.7, random.gauss(base_quality, 3.8)))
            active_users = int(random.randint(55, 460) * base_adoption * weekday_lift)
            target_users = int(active_users / max(0.35, base_adoption) + random.randint(25, 120))
            latency = max(8, random.gauss(base_latency, 24))
            export_count = int(active_users * random.uniform(0.06, 0.28))
            rows.append(
                {
                    "date": day.isoformat(),
                    "report_id": report["report_id"],
                    "active_users": active_users,
                    "target_users": target_users,
                    "view_count": int(active_users * random.uniform(1.2, 3.8)),
                    "export_count": export_count,
                    "avg_render_seconds": round(random.uniform(3.2, 18.5), 1),
                    "quality_score": round(quality, 1),
                    "refresh_latency_minutes": round(latency, 1),
                    "ticket_count": random.randint(0, 8),
                    "decision_value": report["decision_value"],
                }
            )
    return rows


def build_refresh_runs(reports):
    rows = []
    start = date.today() - timedelta(days=59)
    for report in reports:
        for offset in range(60):
            day = start + timedelta(days=offset)
            failure_chance = 0.04 if report["complexity"] == "Low" else 0.08 if report["complexity"] == "Medium" else 0.14
            failed = random.random() < failure_chance
            duration = random.uniform(8, 95)
            rows.append(
                {
                    "run_id": f"RUN-{report['report_id']}-{offset:03d}",
                    "date": day.isoformat(),
                    "report_id": report["report_id"],
                    "status": "Failed" if failed else random.choice(["Succeeded", "Succeeded", "Succeeded", "Warning"]),
                    "duration_minutes": round(duration, 1),
                    "sla_met": "No" if failed or duration > 72 else "Yes",
                    "rows_processed": random.randint(18000, 950000),
                    "failure_reason": random.choice(
                        ["source delay", "gateway timeout", "credential expiry", "schema drift", "capacity queue", "none"]
                    )
                    if failed
                    else "none",
                }
            )
    return rows


def build_quality_checks(reports):
    check_types = ["freshness", "completeness", "uniqueness", "referential integrity", "metric reconciliation", "schema drift"]
    rows = []
    for report in reports:
        for index, check_type in enumerate(check_types, start=1):
            severity = random.choice(["Low", "Medium", "High", "Critical"])
            observed = random.uniform(0.0, 7.5) if check_type != "freshness" else random.uniform(2, 190)
            result = random.choices(["Pass", "Warning", "Fail"], weights=[58, 25, 17])[0]
            rows.append(
                {
                    "check_id": f"CHK-{report['report_id']}-{index}",
                    "report_id": report["report_id"],
                    "check_type": check_type,
                    "severity": severity,
                    "threshold": "24 hours" if check_type == "freshness" else "2.0 percent",
                    "observed_value": round(observed, 2),
                    "result": result,
                    "recommended_fix": random.choice(
                        [
                            "confirm source owner and rerun validation",
                            "add exception handling to transformation",
                            "document metric grain and filter logic",
                            "reconcile against invoice control total",
                            "refresh customer hierarchy mapping",
                            "publish data quality note to consumers",
                        ]
                    ),
                }
            )
    return rows


def build_lineage(reports):
    stages = ["landing", "validation", "warehouse model", "semantic model", "published report"]
    rows = []
    for report in reports:
        for stage in stages:
            rows.append(
                {
                    "lineage_id": f"LIN-{report['report_id']}-{stage.replace(' ', '-')}",
                    "report_id": report["report_id"],
                    "source_system": report["source_system"],
                    "pipeline_stage": stage,
                    "dependency_tier": random.choice(["Standard", "Important", "Critical"]),
                    "owner": random.choice(owners),
                    "last_validated_days": random.randint(0, 65),
                    "open_exception": random.choice(["No", "No", "Yes"]),
                    "business_impact": random.choice(
                        ["metric delay", "incorrect segmentation", "missing store mapping", "late invoice adjustment", "none"]
                    ),
                }
            )
    return rows


def build_metric_definitions(reports):
    metrics = [
        ("penetration_rate", "covered outlets divided by eligible outlets"),
        ("churn_rate", "outlets with no qualifying transaction after active baseline"),
        ("change_contribution", "period change decomposed by volume, price, mix, and account movement"),
        ("program_compliance", "validated activity divided by funded activity"),
        ("refresh_success_rate", "successful refresh runs divided by attempted refresh runs"),
    ]
    rows = []
    for report in reports:
        for metric_name, definition in random.sample(metrics, 3):
            rows.append(
                {
                    "metric_id": f"MET-{report['report_id']}-{metric_name}",
                    "report_id": report["report_id"],
                    "metric_name": metric_name,
                    "business_definition": definition,
                    "grain": random.choice(["customer by week", "outlet by month", "report by day", "program by period"]),
                    "certification_state": random.choice(["Certified", "Peer review", "Needs owner", "Draft"]),
                    "sql_test_coverage": random.choice(["Full", "Partial", "Missing"]),
                    "owner": random.choice(owners),
                }
            )
    return rows


def build_requests(reports):
    rows = []
    request_types = ["new metric", "data anomaly", "training", "access", "performance", "definition clarification", "custom extract"]
    for report in reports:
        for index in range(random.randint(4, 8)):
            rows.append(
                {
                    "request_id": f"REQ-{report['report_id']}-{index + 1}",
                    "report_id": report["report_id"],
                    "request_type": random.choice(request_types),
                    "stakeholder_group": report["audience"],
                    "priority": random.choice(["Low", "Medium", "High", "Critical"]),
                    "age_days": random.randint(1, 44),
                    "status": random.choice(["Open", "In review", "Waiting on stakeholder", "Closed"]),
                    "requirement_clarity": random.choice(["Clear", "Needs acceptance criteria", "Ambiguous"]),
                    "service_action": random.choice(
                        [
                            "schedule metric walkthrough",
                            "publish annotated workbook",
                            "add SQL validation evidence",
                            "create stakeholder FAQ",
                            "confirm business owner",
                            "separate one-off extract from recurring report",
                        ]
                    ),
                }
            )
    return rows


def build_docs_and_training(reports):
    docs = []
    training = []
    for report in reports:
        for doc_type in ["metric guide", "refresh note"]:
            docs.append(
                {
                    "doc_id": f"DOC-{report['report_id']}-{doc_type.replace(' ', '-')}",
                    "report_id": report["report_id"],
                    "doc_type": doc_type,
                    "status": random.choice(["Current", "Needs update", "Missing"]),
                    "last_reviewed_days": random.randint(2, 120),
                    "owner": random.choice(owners),
                }
            )
        for index in range(random.randint(1, 4)):
            training.append(
                {
                    "session_id": f"TRN-{report['report_id']}-{index + 1}",
                    "report_id": report["report_id"],
                    "audience": report["audience"],
                    "attendance": random.randint(8, 85),
                    "satisfaction_score": round(random.uniform(3.1, 4.9), 1),
                    "follow_up_requests": random.randint(0, 9),
                    "adoption_lift_pct": round(random.uniform(0.5, 9.5), 1),
                }
            )
    return docs, training


def build_recommended_actions(reports):
    action_types = [
        "metric certification",
        "source quality remediation",
        "training and documentation",
        "refresh performance tuning",
        "stakeholder requirement clarification",
    ]
    rows = []
    for index in range(220):
        report = random.choice(reports)
        rows.append(
            {
                "action_id": f"ACT{index + 1:03d}",
                "report_id": report["report_id"],
                "action_type": random.choice(action_types),
                "expected_lift_pct": round(random.uniform(1.5, 14.0), 1),
                "effort_hours": random.randint(2, 38),
                "owner_group": random.choice(owners),
                "status": random.choice(["Ready", "Queued", "Needs stakeholder input", "In progress"]),
            }
        )
    return rows


def build_source_events(reports):
    event_types = [
        "refresh exception",
        "quality alert",
        "definition question",
        "stakeholder training ask",
        "lineage ownership update",
        "performance review",
    ]
    rows = []
    start = date.today() - timedelta(days=119)
    for index in range(760):
        report = random.choice(reports)
        rows.append(
            {
                "event_id": f"EVT{index + 1:04d}",
                "event_date": (start + timedelta(days=random.randint(0, 119))).isoformat(),
                "report_id": report["report_id"],
                "event_type": random.choice(event_types),
                "severity": random.choice(["Low", "Medium", "High", "Critical"]),
                "stakeholder_group": report["audience"],
                "estimated_impact": random.randint(1200, 54000),
                "resolution_state": random.choice(["Open", "In review", "Resolved", "Monitoring"]),
                "note": random.choice(
                    [
                        "source owner confirmation needed",
                        "metric definition requires clarification",
                        "training material should be refreshed",
                        "refresh evidence attached to operating review",
                        "quality exception tied to customer hierarchy mapping",
                    ]
                ),
            }
        )
    return rows


def main():
    reports = build_reports()
    daily = build_daily_metrics(reports)
    refresh = build_refresh_runs(reports)
    quality = build_quality_checks(reports)
    lineage = build_lineage(reports)
    metrics = build_metric_definitions(reports)
    requests = build_requests(reports)
    docs, training = build_docs_and_training(reports)
    actions = build_recommended_actions(reports)
    source_events = build_source_events(reports)

    write_csv(DATA / "entities.csv", reports, list(reports[0].keys()))
    write_csv(DATA / "daily_metrics.csv", daily, list(daily[0].keys()))
    write_csv(DATA / "refresh_runs.csv", refresh, list(refresh[0].keys()))
    write_csv(DATA / "quality_checks.csv", quality, list(quality[0].keys()))
    write_csv(DATA / "lineage_map.csv", lineage, list(lineage[0].keys()))
    write_csv(DATA / "metric_definitions.csv", metrics, list(metrics[0].keys()))
    write_csv(DATA / "stakeholder_requests.csv", requests, list(requests[0].keys()))
    write_csv(DATA / "documentation_assets.csv", docs, list(docs[0].keys()))
    write_csv(DATA / "training_sessions.csv", training, list(training[0].keys()))
    write_csv(DATA / "recommended_actions.csv", actions, list(actions[0].keys()))
    write_csv(DATA / "source_events.csv", source_events, list(source_events[0].keys()))

    OUTPUTS.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
