import { useEffect, useState } from "react";
import { researchApi, type Campaign, type Dataset, type ResearchSpec } from "./api";
import { JointPanel } from "./JointPanel";

export function ResearchPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [configs, setConfigs] = useState<{ id: string; configuration: ResearchSpec }[]>([]);
  const [configId, setConfigId] = useState("pilot");
  const [datasetId, setDatasetId] = useState("configured");
  const [experimentId, setExperimentId] = useState("all");
  const [seedCount, setSeedCount] = useState(1);
  const [firstSeed, setFirstSeed] = useState(100);
  const [timeLimit, setTimeLimit] = useState(20);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selected, setSelected] = useState("");
  const [detail, setDetail] = useState<Campaign | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [jsonOpen, setJsonOpen] = useState(false);
  const [jointMode, setJointMode] = useState("preset");
  const [algorithms, setAlgorithms] = useState<Record<string, Record<string, string>>>({});
  useEffect(() => {
    let alive = true;
    Promise.all([researchApi.datasets(), researchApi.configurations()]).then(([d, c]) => {
      if (alive) { setDatasets(d); setConfigs(c); }
    }).catch((e) => { if (alive) setError(String(e)); });
    return () => { alive = false; };
  }, []);
  useEffect(() => {
    let alive = true;
    const refresh = async () => {
      try {
        const list = await researchApi.campaigns();
        if (!alive) return;
        setCampaigns(list);
        if (selected) {
          const value = await researchApi.detail(selected);
          if (alive) setDetail(value);
        }
      } catch (e) { if (alive) setError(String(e)); }
    };
    void refresh();
    const timer = setInterval(() => void refresh(), 1500);
    return () => { alive = false; clearInterval(timer); };
  }, [selected]);
  const config = configs.find((c) => c.id === configId)?.configuration;
  const act = async (action: () => Promise<void>) => {
    setBusy(true); setError("");
    try { await action(); } catch (e) { setError(String(e)); } finally { setBusy(false); }
  };
  const start = () => act(async () => {
    if (!config) return;
    const spec = structuredClone(config);
    spec.seeds = Array.from({ length: seedCount }, (_, i) => firstSeed + i);
    spec.job_time_limit_s = timeLimit;
    if (experimentId !== "all") spec.experiments = spec.experiments.filter((e) => e.id === experimentId);
    spec.experiments.forEach((e) => e.treatments.forEach((t) => {
      if (jointMode !== "preset") {
        const optimization = t.overrides.optimization as Record<string, unknown> || {};
        t.overrides.optimization = { ...optimization, joint: {
          ...(optimization.joint as Record<string, unknown> || { scenario_seeds: [0, 101], scenario_seed_policy: "job_seed_offsets" }), mode: jointMode,
        } };
      }
      const edits = algorithms[`${e.id}/${t.id}`];
      if (!edits) return;
      const { routing_policy, ...rawOptimization } = edits;
      const optimization = Object.fromEntries(Object.entries(rawOptimization).map(([key, value]) => [key,
        ["travel_weight", "wait_weight", "stock_weight"].includes(key) ? Number(value) : value]));
      t.overrides = { ...t.overrides, optimization: { ...(t.overrides.optimization as Record<string, unknown> || {}), ...optimization } };
      if (routing_policy) t.overrides.demand = { ...(t.overrides.demand as Record<string, unknown> || {}), routing_policy };
    }));
    if (datasetId !== "configured") {
      spec.datasets = [{ id: datasetId, scale: datasetId, seed: 101, scenario: "feasible" }];
      spec.experiments.forEach((e) => { e.datasets = [datasetId]; });
    }
    const value = await researchApi.start(spec);
    setSelected(value.id); setDetail(null);
  });
  const active = detail && ["QUEUED", "READY", "RUNNING"].includes(detail.status);
  const reportBase = detail ? `/api/research/campaigns/${detail.id}/report` : "";
  return <>
    {error && <div className="notice error" role="alert">{error}</div>}
    <section className="panel">
      <h2>Dataset nghiên cứu</h2>
      <p className="muted">Dữ liệu SYNTHETIC. Snapshot, phiên bản và SHA-256 cụ thể được lưu trong manifest của campaign.</p>
      <div className="table-scroll"><table><thead><tr><th>Dataset</th><th>Nguồn</th><th>Kệ</th><th>Ngành</th><th>SKU</th><th>Đơn</th></tr></thead>
        <tbody>{datasets.map((d) => <tr key={d.id}><td>{d.id} · v{d.version}</td><td>{d.data_origin}</td><td>{d.counts.shelves}</td><td>{d.counts.categories}</td><td>{d.counts.products}</td><td>{d.counts.orders}</td></tr>)}</tbody></table></div>
    </section>
    <section className="panel">
      <h2>Chạy thí nghiệm</h2>
      <div className="form-grid">
        <label>Optimization mode<select aria-label="Optimization mode" value={jointMode} onChange={(e) => setJointMode(e.target.value)}>
          <option value="preset">Use campaign design</option><option value="sequential">Sequential</option><option value="multistart">Multistart</option><option value="random_search">Random Search — equal evaluation budget</option><option value="annealing">Simulated Annealing — equal evaluation budget</option><option value="feedback">Closed-Loop Feedback</option><option value="exact">Exact Joint — requires declared finite space</option><option value="hybrid">Hybrid — requires declared finite space</option>
        </select></label>
        <label>Cấu hình campaign<select aria-label="Cấu hình campaign" value={configId} onChange={(e) => { setConfigId(e.target.value); setExperimentId("all"); }}>
          {configs.map((c) => <option key={c.id} value={c.id}>{c.id}</option>)}</select></label>
        <label>Thí nghiệm<select aria-label="Thí nghiệm" value={experimentId} onChange={(e) => setExperimentId(e.target.value)}><option value="all">Tất cả theo cấu hình</option>
          {config?.experiments.map((e) => <option key={e.id} value={e.id}>{e.id}</option>)}</select></label>
        <label>Dataset<select aria-label="Dataset" value={datasetId} onChange={(e) => setDatasetId(e.target.value)}><option value="configured">Theo cấu hình</option>
          {datasets.map((d) => <option key={d.id} value={d.id}>{d.id}</option>)}</select></label>
        <label>Số seed độc lập<input type="number" min={1} max={10} value={seedCount} onChange={(e) => setSeedCount(Number(e.target.value))} /></label>
        <label>Seed bắt đầu<input type="number" min={0} max={2147483637} value={firstSeed} onChange={(e) => setFirstSeed(Number(e.target.value))} /></label>
        <label>Giới hạn mỗi job (s)<input type="number" min={0.1} max={3600} step={0.1} value={timeLimit} onChange={(e) => setTimeLimit(Number(e.target.value))} /></label>
      </div>
      {config && <p>Ngân sách mỗi job: {timeLimit} s · Giới hạn RSS: {config.memory_limit_mb === null ? "Không giới hạn" : `${config.memory_limit_mb} MiB`} · Một worker · Campaign: {config.max_wall_s} s.</p>}
      <details open={jsonOpen} onToggle={(e) => setJsonOpen(e.currentTarget.open)}><summary>Thuật toán từng tầng và cấu hình đầy đủ</summary>
        {config?.experiments.filter((e) => experimentId === "all" || e.id === experimentId).flatMap((e) => e.treatments.map((t) => {
          const id = `${e.id}/${t.id}`;
          const options = [
            ["layout_algorithm", "T1", ["grid", "local_search"], "grid"],
            ["algorithm", "T2", ["greedy", "milp"], "milp"],
            ["slotting_algorithm", "T3", ["first_fit", "milp"], "first_fit"],
            ["routing_policy", "T4", ["nearest", "return", "exact"], "nearest"],
          ] as const;
          return <fieldset key={id}><legend>{id}</legend><div className="form-grid">{options.map(([key, label, choices, fallback]) => {
            const group = (key === "routing_policy" ? t.overrides.demand : t.overrides.optimization) as Record<string, string> | undefined;
            return <label key={key}>{label} {id}<select value={algorithms[id]?.[key] || group?.[key] || fallback}
              onChange={(event) => setAlgorithms({ ...algorithms, [id]: { ...algorithms[id], [key]: event.target.value } })}>
              {choices.map((choice) => <option key={choice} value={choice}>{choice}</option>)}</select></label>;
            })}{(["travel_weight", "wait_weight", "stock_weight"] as const).map((key) => {
              const group = t.overrides.optimization as Record<string, number> | undefined;
              return <label key={key}>{key} {id}<input type="number" min={0} step={0.1}
                value={algorithms[id]?.[key] ?? group?.[key] ?? (key === "travel_weight" ? 1 : 0)}
                onChange={(event) => setAlgorithms({ ...algorithms, [id]: { ...algorithms[id], [key]: event.target.value } })} /></label>;
            })}</div></fieldset>;
        }))}
        <pre style={{ overflow: "auto", maxHeight: 300 }}>{JSON.stringify(config, null, 2)}</pre>
      </details>
      <button className="primary" disabled={busy || !config || seedCount < 1 || seedCount > 10 || timeLimit <= 0 || timeLimit > 3600 || firstSeed < 0} onClick={() => void start()}>Bắt đầu campaign</button>
    </section>
    <section className="panel">
      <h2>Campaign và kết quả thực tế</h2>
      <label>Chọn campaign<select aria-label="Chọn campaign" value={selected} onChange={(e) => setSelected(e.target.value)}><option value="">Chọn campaign</option>
        {campaigns.map((c) => <option key={c.id} value={c.id}>{c.id.slice(0, 8)} · {c.status}</option>)}</select></label>
      {detail && <>
        <p role="status">Trạng thái campaign: <strong>{detail.status}</strong> · {detail.completed || 0}/{detail.planned || "…"} job · Chưa chạy: {detail.not_executed ?? "…"}</p>
        {detail.datasets?.map((d) => <p key={d.dataset_id} className="muted">{d.dataset_id} · v{d.version} · SHA-256: <code style={{ overflowWrap: "anywhere" }}>{d.sha256}</code></p>)}
        {(detail.error || detail.supervisor?.error) && <p role="alert">{detail.error || detail.supervisor?.error}</p>}
        <div className="actions">
          <button disabled={busy || !active} onClick={() => void act(async () => { await researchApi.action(detail.id, "cancel"); })}>Hủy campaign</button>
          <button disabled={busy || !["PAUSED_PARTIAL", "FAILED"].includes(detail.status)} onClick={() => void act(async () => { await researchApi.action(detail.id, "resume"); })}>Tiếp tục campaign</button>
          <button disabled={busy || !!active} onClick={() => void act(async () => { const value = await researchApi.action(detail.id, "replay"); setSelected(value.id); setDetail(null); })}>Replay campaign</button>
        </div>
        <div className="table-scroll"><table><thead><tr><th>Thí nghiệm</th><th>Nhánh</th><th>Seed</th><th>Trạng thái</th><th>Wall (s)</th><th>RSS (MiB)</th><th>Route TB (m)</th><th>Replay độc lập</th></tr></thead>
          <tbody>{detail.records?.map((r) => <tr key={r.job_key}><td>{r.experiment}/{r.dataset}</td><td>{r.treatment}</td><td>{r.seed}</td><td title={r.error?.message}>{r.status}</td><td>{r.wall_s.toFixed(3)}</td><td>{r.peak_child_rss_bytes ? (r.peak_child_rss_bytes / 1048576).toFixed(1) : "—"}</td><td>{r.mean_distance_m?.toFixed(3) ?? "—"}</td><td>{r.validation.status}</td></tr>)}</tbody></table></div>
        <JointPanel campaign={detail.id} jobs={detail.records || []} />
        {detail.supervisor?.report && <>
          {detail.records?.some((r) => r.joint_objective != null) && <div className="actions">{["joint-comparison.csv", "joint-trace.csv", "joint-examples.json", "figures/joint-convergence.svg"].map((name) => <a className="button" key={name} href={`${reportBase}/${name}`} download>{name}</a>)}</div>}
          <div className="actions">{["results.csv", "results.json", "statistics.json", "comparisons.csv", "failures.csv", "manifest.json", "summary.md"].map((name) => <a className="button" key={name} href={`${reportBase}/${name}`} download>{name}</a>)}</div>
          <a href={`${reportBase}/figures/wall_s.svg`} download>Tải biểu đồ SVG</a>
          <img src={`${reportBase}/figures/wall_s.png`} alt="Thời gian trung bình của các nhánh từ kết quả campaign đã chạy" style={{ width: "100%", maxWidth: 1000 }} />
        </>}
      </>}
    </section>
  </>;
}
