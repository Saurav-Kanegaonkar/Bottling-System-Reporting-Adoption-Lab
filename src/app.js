const paths = {
  reports: "data/entities.csv",
  priority: "analysis/outputs/priority_queue.csv",
  quality: "analysis/outputs/refresh_quality_summary.csv",
  lineage: "analysis/outputs/lineage_quality_queue.csv",
  adoption: "analysis/outputs/adoption_documentation_queue.csv",
  requests: "data/stakeholder_requests.csv",
  metrics: "data/metric_definitions.csv",
  summary: "analysis/outputs/summary.json",
};

const state = {
  domain: "All domains",
  data: {},
};

function parseCsv(text) {
  const rows = [];
  let field = "";
  let row = [];
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];
    if (char === '"' && quoted && next === '"') {
      field += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      row.push(field);
      field = "";
    } else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && next === "\n") index += 1;
      row.push(field);
      if (row.some((cell) => cell !== "")) rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }

  if (field || row.length) {
    row.push(field);
    rows.push(row);
  }

  const [headers, ...records] = rows;
  return records.map((record) =>
    Object.fromEntries(headers.map((header, index) => [header, record[index] ?? ""]))
  );
}

async function loadCsv(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Unable to load ${path}`);
  return parseCsv(await response.text());
}

async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Unable to load ${path}`);
  return response.json();
}

function number(value) {
  return Number(String(value).replace(/[$,%]/g, "")) || 0;
}

function percent(value) {
  return `${(number(value) * 100).toFixed(1)}%`;
}

function currency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(number(value));
}

function laneClass(lane) {
  if (lane === "Remediate before scale") return "risk";
  if (lane === "Validate with stakeholders") return "watch";
  return "ready";
}

function filteredPriority() {
  if (state.domain === "All domains") return state.data.priority;
  return state.data.priority.filter((row) => row.domain === state.domain);
}

function renderKpis() {
  const { summary } = state.data;
  const kpis = [
    ["Reporting assets", summary.report_count, `${summary.metric_definitions} metric definitions`],
    ["Avg adoption", percent(summary.avg_adoption_rate), `${summary.training_sessions} training sessions`],
    ["Avg quality", `${summary.avg_quality_score}%`, `${summary.failed_quality_checks} failed checks`],
    ["Urgent asks", summary.open_urgent_requests, "open high priority requests"],
    ["Docs to refresh", summary.stale_docs, "stale or missing assets"],
  ];

  document.querySelector("#kpiGrid").innerHTML = kpis
    .map(
      ([label, value, note]) => `
        <article class="kpi-card">
          <span>${label}</span>
          <strong>${value}</strong>
          <em>${note}</em>
        </article>
      `
    )
    .join("");
}

function renderFilter() {
  const domains = ["All domains", ...new Set(state.data.priority.map((row) => row.domain))];
  const select = document.querySelector("#domainFilter");
  select.innerHTML = domains.map((domain) => `<option>${domain}</option>`).join("");
  select.value = state.domain;
  select.addEventListener("change", (event) => {
    state.domain = event.target.value;
    renderPortfolio();
  });
}

function renderPortfolio() {
  const rows = filteredPriority().slice(0, 10);
  document.querySelector("#priorityRows").innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td><strong>${row.report_name}</strong><small>${row.domain} | ${row.workspace}</small></td>
          <td>${row.audience}</td>
          <td><span class="score-pill">${row.priority_score}</span></td>
          <td>${percent(row.adoption_rate)}</td>
          <td>${row.avg_quality_score}%</td>
          <td><span class="status ${laneClass(row.recommended_lane)}">${row.recommended_lane}</span></td>
        </tr>
      `
    )
    .join("");

  const domainMap = new Map();
  state.data.priority.forEach((row) => {
    const bucket = domainMap.get(row.domain) ?? { score: 0, reports: 0, value: 0, requests: 0 };
    bucket.score += number(row.priority_score);
    bucket.reports += 1;
    bucket.value += number(row.decision_value);
    bucket.requests += number(row.urgent_requests);
    domainMap.set(row.domain, bucket);
  });

  const domains = [...domainMap.entries()]
    .map(([domain, values]) => ({
      domain,
      score: values.score / values.reports,
      value: values.value,
      requests: values.requests,
    }))
    .sort((a, b) => b.score - a.score);
  const maxScore = Math.max(...domains.map((row) => row.score));

  document.querySelector("#domainRisk").innerHTML = domains
    .map(
      (row) => `
        <div class="bar-row">
          <div>
            <strong>${row.domain}</strong>
            <span>${row.requests} urgent asks | ${currency(row.value)} decision value</span>
          </div>
          <meter min="0" max="${maxScore}" value="${row.score}"></meter>
          <b>${row.score.toFixed(1)}</b>
        </div>
      `
    )
    .join("");
}

function renderQuality() {
  const { quality, lineage } = state.data;
  const failedRuns = quality.reduce((sum, row) => sum + number(row.failed_runs), 0);
  const slaMisses = quality.reduce((sum, row) => sum + number(row.sla_misses), 0);
  const failedChecks = quality.reduce((sum, row) => sum + number(row.failed_quality_checks), 0);
  const criticalOpen = lineage.filter(
    (row) => row.dependency_tier === "Critical" && row.open_exception === "Yes"
  ).length;

  document.querySelector("#qualityStats").innerHTML = [
    ["Failed refreshes", failedRuns, "modeled refresh exceptions"],
    ["SLA misses", slaMisses, "late or failed refresh runs"],
    ["Failed checks", failedChecks, "freshness, completeness, and reconciliation"],
    ["Critical lineage", criticalOpen, "open source dependencies"],
  ]
    .map(
      ([label, value, note]) => `
        <article class="mini-card">
          <span>${label}</span>
          <strong>${value}</strong>
          <em>${note}</em>
        </article>
      `
    )
    .join("");

  document.querySelector("#qualityRows").innerHTML = quality
    .slice(0, 10)
    .map(
      (row) => `
        <tr>
          <td><strong>${row.report_name}</strong><small>${row.source_system}</small></td>
          <td>${row.failed_runs}</td>
          <td>${row.sla_misses}</td>
          <td>${row.failed_quality_checks}</td>
          <td>${row.avg_latency_minutes} min</td>
          <td>${row.recommended_fix}</td>
        </tr>
      `
    )
    .join("");

  document.querySelector("#lineageCards").innerHTML = lineage
    .slice(0, 8)
    .map(
      (row) => `
        <article class="lineage-card">
          <span>${row.pipeline_stage}</span>
          <h3>${row.report_name}</h3>
          <p>${row.source_system} | ${row.business_impact}</p>
          <footer>
            <b>${row.risk_score}</b>
            <em>${row.dependency_tier}, ${row.open_exception === "Yes" ? "open exception" : "validated"}</em>
          </footer>
        </article>
      `
    )
    .join("");
}

function renderAdoption() {
  const { adoption, requests, metrics } = state.data;
  document.querySelector("#adoptionRows").innerHTML = adoption
    .slice(0, 10)
    .map(
      (row) => `
        <tr>
          <td><strong>${row.report_name}</strong><small>${row.audience}</small></td>
          <td>${percent(row.adoption_rate)}</td>
          <td>${row.training_sessions}</td>
          <td>${row.stale_or_missing_docs}</td>
          <td>${row.ambiguous_requests}</td>
          <td>${row.service_action}</td>
        </tr>
      `
    )
    .join("");

  const openRequests = requests.filter((row) => row.status !== "Closed").slice(0, 8);
  document.querySelector("#requestCards").innerHTML = openRequests
    .map(
      (row) => `
        <article class="request-card">
          <span>${row.priority} ${row.request_type}</span>
          <h3>${row.stakeholder_group}</h3>
          <p>${row.service_action}</p>
          <footer>${row.requirement_clarity} | ${row.age_days} days open</footer>
        </article>
      `
    )
    .join("");

  const metricBuckets = metrics.reduce((acc, row) => {
    acc[row.certification_state] = (acc[row.certification_state] || 0) + 1;
    return acc;
  }, {});
  document.querySelector("#metricCertification").innerHTML = Object.entries(metricBuckets)
    .map(
      ([label, count]) => `
        <div class="cert-row">
          <span>${label}</span>
          <strong>${count}</strong>
        </div>
      `
    )
    .join("");
}

async function init() {
  const [reports, priority, quality, lineage, adoption, requests, metrics, summary] =
    await Promise.all([
      loadCsv(paths.reports),
      loadCsv(paths.priority),
      loadCsv(paths.quality),
      loadCsv(paths.lineage),
      loadCsv(paths.adoption),
      loadCsv(paths.requests),
      loadCsv(paths.metrics),
      loadJson(paths.summary),
    ]);

  state.data = { reports, priority, quality, lineage, adoption, requests, metrics, summary };
  renderKpis();
  renderFilter();
  renderPortfolio();
  renderQuality();
  renderAdoption();
}

init().catch((error) => {
  document.querySelector("main").innerHTML = `<section class="panel"><h1>Unable to load artifact data</h1><p>${error.message}</p></section>`;
});
