-- Reporting portfolio priority queue
select
  r.report_id,
  r.report_name,
  r.domain,
  r.audience,
  r.owner_group,
  avg(d.quality_score) as avg_quality_score,
  avg(d.active_users / nullif(d.target_users, 0)) as adoption_rate,
  sum(case when q.result = 'Fail' then 1 else 0 end) as failed_quality_checks,
  sum(case when sr.status <> 'Closed' and sr.priority in ('High', 'Critical') then 1 else 0 end) as urgent_open_requests
from entities r
join daily_metrics d
  on r.report_id = d.report_id
left join quality_checks q
  on r.report_id = q.report_id
left join stakeholder_requests sr
  on r.report_id = sr.report_id
group by
  r.report_id,
  r.report_name,
  r.domain,
  r.audience,
  r.owner_group
order by urgent_open_requests desc, failed_quality_checks desc, avg_quality_score asc;

-- Refresh reliability and SLA triage
select
  r.report_id,
  r.report_name,
  r.source_system,
  count(*) as refresh_runs,
  sum(case when rr.status = 'Failed' then 1 else 0 end) as failed_runs,
  sum(case when rr.sla_met = 'No' then 1 else 0 end) as sla_misses,
  avg(rr.duration_minutes) as avg_duration_minutes
from entities r
join refresh_runs rr
  on r.report_id = rr.report_id
group by
  r.report_id,
  r.report_name,
  r.source_system
having failed_runs > 0 or sla_misses > 0
order by failed_runs desc, sla_misses desc;

-- Data quality controls by reporting domain
select
  r.domain,
  q.check_type,
  q.severity,
  q.result,
  count(*) as check_count
from quality_checks q
join entities r
  on q.report_id = r.report_id
group by
  r.domain,
  q.check_type,
  q.severity,
  q.result
order by r.domain, check_count desc;

-- Critical lineage exceptions that need owner follow-up
select
  r.report_name,
  l.source_system,
  l.pipeline_stage,
  l.dependency_tier,
  l.owner,
  l.last_validated_days,
  l.business_impact
from lineage_map l
join entities r
  on l.report_id = r.report_id
where l.dependency_tier = 'Critical'
  and l.open_exception = 'Yes'
order by l.last_validated_days desc;

-- Metric definitions that are not ready for certification
select
  r.report_name,
  m.metric_name,
  m.business_definition,
  m.grain,
  m.certification_state,
  m.sql_test_coverage,
  m.owner
from metric_definitions m
join entities r
  on m.report_id = r.report_id
where m.certification_state <> 'Certified'
   or m.sql_test_coverage <> 'Full'
order by r.report_name, m.metric_name;

-- Adoption and documentation service queue
select
  r.report_id,
  r.report_name,
  r.audience,
  avg(d.active_users / nullif(d.target_users, 0)) as adoption_rate,
  sum(case when da.status <> 'Current' then 1 else 0 end) as stale_or_missing_docs,
  sum(case when sr.status <> 'Closed' and sr.requirement_clarity <> 'Clear' then 1 else 0 end) as ambiguous_open_requests
from entities r
join daily_metrics d
  on r.report_id = d.report_id
left join documentation_assets da
  on r.report_id = da.report_id
left join stakeholder_requests sr
  on r.report_id = sr.report_id
group by
  r.report_id,
  r.report_name,
  r.audience
order by stale_or_missing_docs desc, ambiguous_open_requests desc, adoption_rate asc;
