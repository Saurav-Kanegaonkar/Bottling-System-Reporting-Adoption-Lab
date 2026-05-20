import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"


def read_csv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def priority_label(score):
    if score >= 74:
        return "Remediate before scale"
    if score >= 52:
        return "Validate with stakeholders"
    return "Publish and monitor"


def average(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def main():
    reports = read_csv(DATA / "entities.csv")
    daily = read_csv(DATA / "daily_metrics.csv")
    refresh = read_csv(DATA / "refresh_runs.csv")
    quality = read_csv(DATA / "quality_checks.csv")
    lineage = read_csv(DATA / "lineage_map.csv")
    requests = read_csv(DATA / "stakeholder_requests.csv")
    docs = read_csv(DATA / "documentation_assets.csv")
    training = read_csv(DATA / "training_sessions.csv")
    metrics = read_csv(DATA / "metric_definitions.csv")

    daily_by_report = defaultdict(list)
    refresh_by_report = defaultdict(list)
    quality_by_report = defaultdict(list)
    lineage_by_report = defaultdict(list)
    request_by_report = defaultdict(list)
    docs_by_report = defaultdict(list)
    training_by_report = defaultdict(list)
    metrics_by_report = defaultdict(list)

    for row in daily:
        daily_by_report[row["report_id"]].append(row)
    for row in refresh:
        refresh_by_report[row["report_id"]].append(row)
    for row in quality:
        quality_by_report[row["report_id"]].append(row)
    for row in lineage:
        lineage_by_report[row["report_id"]].append(row)
    for row in requests:
        request_by_report[row["report_id"]].append(row)
    for row in docs:
        docs_by_report[row["report_id"]].append(row)
    for row in training:
        training_by_report[row["report_id"]].append(row)
    for row in metrics:
        metrics_by_report[row["report_id"]].append(row)

    priority_rows = []
    quality_rows = []
    lineage_rows = []
    adoption_rows = []

    for report in reports:
        report_id = report["report_id"]
        daily_rows = daily_by_report[report_id]
        refresh_rows = refresh_by_report[report_id]
        quality_checks = quality_by_report[report_id]
        lineage_checks = lineage_by_report[report_id]
        request_rows = request_by_report[report_id]
        doc_rows = docs_by_report[report_id]
        training_rows = training_by_report[report_id]
        metric_rows = metrics_by_report[report_id]

        avg_quality = average(number(row["quality_score"]) for row in daily_rows)
        adoption_rate = average(
            number(row["active_users"]) / max(1.0, number(row["target_users"])) for row in daily_rows
        )
        avg_latency = average(number(row["refresh_latency_minutes"]) for row in daily_rows)
        failed_refreshes = sum(1 for row in refresh_rows if row["status"] == "Failed")
        sla_misses = sum(1 for row in refresh_rows if row["sla_met"] == "No")
        failed_checks = sum(1 for row in quality_checks if row["result"] == "Fail")
        warning_checks = sum(1 for row in quality_checks if row["result"] == "Warning")
        critical_lineage = sum(
            1
            for row in lineage_checks
            if row["dependency_tier"] == "Critical" and row["open_exception"] == "Yes"
        )
        open_requests = [row for row in request_rows if row["status"] != "Closed"]
        urgent_requests = sum(1 for row in open_requests if row["priority"] in ["High", "Critical"])
        ambiguous_requests = sum(
            1 for row in open_requests if row["requirement_clarity"] != "Clear"
        )
        stale_docs = sum(1 for row in doc_rows if row["status"] != "Current")
        uncertified_metrics = sum(
            1 for row in metric_rows if row["certification_state"] != "Certified"
        )
        training_lift = average(number(row["adoption_lift_pct"]) for row in training_rows)

        quality_risk = max(0.0, 96.0 - avg_quality) * 1.3 + failed_checks * 5 + warning_checks * 2
        refresh_risk = failed_refreshes * 1.8 + sla_misses * 0.9 + max(0.0, avg_latency - 60) * 0.08
        adoption_risk = max(0.0, 0.78 - adoption_rate) * 55
        request_risk = urgent_requests * 3.4 + ambiguous_requests * 2.2
        doc_risk = stale_docs * 4.5 + uncertified_metrics * 2.4
        lineage_risk = critical_lineage * 8.5
        value_weight = number(report["decision_value"]) / 42000
        priority_score = min(
            100.0,
            value_weight + quality_risk + refresh_risk + adoption_risk + request_risk + doc_risk + lineage_risk,
        )

        priority_rows.append(
            {
                "report_id": report_id,
                "report_name": report["report_name"],
                "domain": report["domain"],
                "audience": report["audience"],
                "owner_group": report["owner_group"],
                "workspace": report["workspace"],
                "priority_score": round(priority_score, 1),
                "adoption_rate": round(adoption_rate, 3),
                "avg_quality_score": round(avg_quality, 1),
                "refresh_sla_misses": sla_misses,
                "failed_quality_checks": failed_checks,
                "urgent_requests": urgent_requests,
                "stale_docs": stale_docs,
                "critical_lineage_exceptions": critical_lineage,
                "decision_value": int(number(report["decision_value"])),
                "recommended_lane": priority_label(priority_score),
                "next_action": next_action(failed_checks, critical_lineage, stale_docs, urgent_requests, adoption_rate),
            }
        )

        quality_rows.append(
            {
                "report_id": report_id,
                "report_name": report["report_name"],
                "source_system": report["source_system"],
                "runs": len(refresh_rows),
                "failed_runs": failed_refreshes,
                "sla_misses": sla_misses,
                "failed_quality_checks": failed_checks,
                "warning_quality_checks": warning_checks,
                "avg_latency_minutes": round(avg_latency, 1),
                "recommended_fix": quality_fix(failed_checks, sla_misses, avg_latency),
            }
        )

        lineage_rows.extend(
            {
                "report_id": report_id,
                "report_name": report["report_name"],
                "source_system": row["source_system"],
                "pipeline_stage": row["pipeline_stage"],
                "dependency_tier": row["dependency_tier"],
                "owner": row["owner"],
                "last_validated_days": row["last_validated_days"],
                "open_exception": row["open_exception"],
                "business_impact": row["business_impact"],
                "risk_score": lineage_score(row),
            }
            for row in lineage_checks
        )

        adoption_rows.append(
            {
                "report_id": report_id,
                "report_name": report["report_name"],
                "audience": report["audience"],
                "adoption_rate": round(adoption_rate, 3),
                "training_sessions": len(training_rows),
                "avg_training_lift_pct": round(training_lift, 1),
                "stale_or_missing_docs": stale_docs,
                "open_requests": len(open_requests),
                "ambiguous_requests": ambiguous_requests,
                "service_action": adoption_action(stale_docs, ambiguous_requests, adoption_rate),
            }
        )

    priority_rows.sort(key=lambda row: number(row["priority_score"]), reverse=True)
    quality_rows.sort(
        key=lambda row: (number(row["failed_quality_checks"]), number(row["sla_misses"])),
        reverse=True,
    )
    lineage_rows.sort(key=lambda row: number(row["risk_score"]), reverse=True)
    adoption_rows.sort(
        key=lambda row: (number(row["stale_or_missing_docs"]), number(row["ambiguous_requests"]), 1 - number(row["adoption_rate"])),
        reverse=True,
    )

    write_csv(OUTPUTS / "priority_queue.csv", priority_rows, list(priority_rows[0].keys()))
    write_csv(OUTPUTS / "refresh_quality_summary.csv", quality_rows, list(quality_rows[0].keys()))
    write_csv(OUTPUTS / "lineage_quality_queue.csv", lineage_rows, list(lineage_rows[0].keys()))
    write_csv(OUTPUTS / "adoption_documentation_queue.csv", adoption_rows, list(adoption_rows[0].keys()))

    summary = {
        "report_count": len(reports),
        "daily_metric_rows": len(daily),
        "refresh_runs": len(refresh),
        "quality_checks": len(quality),
        "lineage_dependencies": len(lineage),
        "stakeholder_requests": len(requests),
        "metric_definitions": len(metrics),
        "documentation_assets": len(docs),
        "training_sessions": len(training),
        "avg_adoption_rate": round(average(number(row["adoption_rate"]) for row in priority_rows), 3),
        "avg_quality_score": round(average(number(row["avg_quality_score"]) for row in priority_rows), 1),
        "top_priority_report": priority_rows[0]["report_name"],
        "top_priority_score": priority_rows[0]["priority_score"],
        "open_urgent_requests": sum(number(row["urgent_requests"]) for row in priority_rows),
        "stale_docs": sum(number(row["stale_docs"]) for row in priority_rows),
        "failed_quality_checks": sum(number(row["failed_quality_checks"]) for row in priority_rows),
    }
    with (OUTPUTS / "summary.json").open("w") as handle:
        json.dump(summary, handle, indent=2)

    print(f"Wrote {len(priority_rows)} report priority rows")
    print(f"Top priority: {priority_rows[0]['report_name']} at {priority_rows[0]['priority_score']}")


def next_action(failed_checks, critical_lineage, stale_docs, urgent_requests, adoption_rate):
    if failed_checks > 1 or critical_lineage:
        return "Investigate data quality and source lineage before next stakeholder release"
    if stale_docs > 0:
        return "Refresh documentation and certify metric definitions"
    if urgent_requests > 2:
        return "Run requirement clarification session with business owners"
    if adoption_rate < 0.7:
        return "Schedule training and publish adoption guidance"
    return "Publish in operating review and monitor"


def quality_fix(failed_checks, sla_misses, avg_latency):
    if failed_checks:
        return "Prioritize failed validation checks and reconcile against source controls"
    if sla_misses > 8:
        return "Tune refresh path and confirm capacity window"
    if avg_latency > 80:
        return "Review source latency and semantic model load time"
    return "Keep in monitoring lane"


def lineage_score(row):
    tier = {"Standard": 10, "Important": 24, "Critical": 38}[row["dependency_tier"]]
    exception = 35 if row["open_exception"] == "Yes" else 0
    age = min(25, number(row["last_validated_days"]) * 0.4)
    impact = 12 if row["business_impact"] != "none" else 0
    return round(tier + exception + age + impact, 1)


def adoption_action(stale_docs, ambiguous_requests, adoption_rate):
    if stale_docs:
        return "Publish refreshed metric guide and report walkthrough"
    if ambiguous_requests:
        return "Translate open asks into acceptance criteria"
    if adoption_rate < 0.7:
        return "Run training with examples from current business routines"
    return "Maintain office hours and monitor adoption"


if __name__ == "__main__":
    main()
