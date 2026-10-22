import { useEffect, useState } from "react";

type Decision = { poses: Record<string, [number, number, number]>; assignment: Record<string, string>; placements: Record<string, string | number>[] };
type Trace = { event: number; iteration?: number; action?: string; layer?: string; before?: number; after?: number; accepted?: boolean; reason?: string; best_score?: number; decisions?: Decision };
interface JointResult {
  joint: { mode: string; status: string; proof_status: string; evaluations: number; initial_score: number; best: { score: number; components: number[]; decisions: Decision } | null;
    normalization: { scales: number[]; weights: number[] };
    trace: Trace[]; certificate?: { upper_bound_fraction: number[] | null; lower_bound_fraction: number[]; absolute_gap: number | null; evaluated_states: number; total_states: number; scope: string }; verification?: { status?: string }; holdout?: { score?: number; status?: string; scenario_seeds: number[] } };
  initial_decisions: Decision | null;
  shelves: { id: string; width_m: number; depth_m: number }[];
  floorplan: { boundary: number[][] };
}

function Layout({ decision, shelves, boundary, title }: { decision: Decision; shelves: JointResult["shelves"]; boundary: number[][]; title: string }) {
  const xs = boundary.map((p) => p[0]), ys = boundary.map((p) => p[1]);
  const minX = Math.min(...xs), minY = Math.min(...ys), width = Math.max(...xs) - minX, height = Math.max(...ys) - minY;
  return <figure><figcaption>{title}</figcaption><svg role="img" aria-label={title} viewBox={`${minX - 1} ${minY - 1} ${width + 2} ${height + 2}`} style={{ width: "100%", maxHeight: 260 }}>
    <polygon points={boundary.map((p) => p.join(",")).join(" ")} fill="#f3f6f1" stroke="#53715e" strokeWidth={0.05} />
    {shelves.map((s) => { const pose = decision.poses[s.id]; if (!pose) return null; const [x, y, angle] = pose;
      return <g key={s.id}><rect x={x} y={y} width={angle === 90 ? s.depth_m : s.width_m} height={angle === 90 ? s.width_m : s.depth_m} fill="#42735b" />
        <text x={x} y={y + .25} fontSize={.23} fill="white">{s.id}</text></g>; })}
  </svg></figure>;
}

export function JointPanel({ campaign, jobs }: { campaign: string; jobs: { job_key: string; treatment: string; joint_objective?: number | null; proof_status?: string }[] }) {
  const jointJobs = jobs.filter((j) => j.joint_objective != null || j.proof_status != null);
  const [job, setJob] = useState("");
  const [data, setData] = useState<JointResult | null>(null);
  const [error, setError] = useState("");
  const [event, setEvent] = useState("best");
  const selected = jointJobs.some((j) => j.job_key === job) ? job : jointJobs[0]?.job_key;
  useEffect(() => {
    let active = true;
    if (!selected) return;
    fetch(`/api/research/campaigns/${campaign}/jobs/${selected}/joint`).then(async (response) => {
      if (!response.ok) throw new Error(await response.text()); return response.json() as Promise<JointResult>;
    }).then((value) => { if (active) { setData(value); setError(""); setEvent("best"); } }).catch((e) => { if (active) setError(String(e)); });
    return () => { active = false; };
  }, [campaign, selected]);
  if (!jointJobs.length) return null;
  const j = data?.joint;
  const edits = j?.trace.filter((t) => t.decisions) || [];
  const decision = event === "best" ? j?.best?.decisions : edits.find((e) => String(e.event) === event)?.decisions;
  const convergence = j?.trace.filter((e) => e.best_score != null) || [];
  const values = convergence.map((e) => e.best_score!);
  const min = Math.min(...values), max = Math.max(...values);
  const points = values.map((v, i) => `${20 + i * 560 / Math.max(1, values.length - 1)},${130 - (v - min) * 100 / Math.max(1e-12, max - min)}`).join(" ");
  return <section aria-label="Joint optimization evidence">
    <h2>Joint T1–T4 optimization</h2>
    <label>Joint job<select aria-label="Joint job" value={selected || ""} onChange={(e) => setJob(e.target.value)}>{jointJobs.map((r) => <option key={r.job_key} value={r.job_key}>{r.treatment} · {r.job_key.slice(0, 8)}</option>)}</select></label>
    {error && <p role="alert">{error}</p>}
    {j && <><p>Mode: <strong>{j.mode}</strong> · Stop: {j.status} · Evaluations: {j.evaluations}</p>
      <p>Initial objective: {j.initial_score?.toFixed(6)} · Best objective: {j.best?.score.toFixed(6)} · Proof: <strong>{j.proof_status}</strong></p>
      {j.best && <dl className="form-grid">{["Training mean route (m)", "Training mean wait (s)", "Stock shortfall ratio", "Late-order ratio"].map((label, i) => <div key={label}><dt>{label}</dt><dd>{(j.best!.components[i] * j.normalization.scales[i]).toFixed(6)}</dd></div>)}</dl>}
      <p>General model: JOINT_GENERAL_OPTIMALITY_NOT_PROVEN. Pareto scope: evaluated candidates only.</p>
      {j.certificate && <div><p>UB: {j.certificate.upper_bound_fraction?.join(" / ") ?? "None"} · LB: {j.certificate.lower_bound_fraction.join(" / ")} · Absolute gap: {j.certificate.absolute_gap ?? "None"}</p>
        <p>States: {j.certificate.evaluated_states}/{j.certificate.total_states} · Verification: {j.verification?.status}</p><p>{j.certificate.scope}</p></div>}
      {j.holdout && <p>Holdout objective: {j.holdout.score?.toFixed(6) ?? "Not evaluated"} · Status: {j.holdout.status} · Unseen seeds: {j.holdout.scenario_seeds.join(", ")}</p>}
      {values.length > 0 && <figure><figcaption>Best objective by completed feedback iteration</figcaption><svg aria-label="Feedback convergence" role="img" viewBox="0 0 600 160" style={{ width: "100%", maxHeight: 200 }}><polyline points={points} fill="none" stroke="#285b43" strokeWidth="2" />{values.map((v, i) => <text key={i} x={20 + i * 560 / Math.max(1, values.length - 1)} y={150} fontSize="10">{v.toFixed(4)}</text>)}</svg></figure>}
      <div className="table-scroll"><table><thead><tr><th>Iteration</th><th>Layer / action</th><th>Before</th><th>After</th><th>Accepted</th><th>Reason</th></tr></thead><tbody>{j.trace.filter((e) => e.action).map((e) => <tr key={e.event}><td>{e.iteration}</td><td>{e.layer} / {e.action}</td><td>{e.before?.toFixed(6)}</td><td>{e.after?.toFixed(6)}</td><td>{String(e.accepted)}</td><td>{e.reason}</td></tr>)}</tbody></table></div>
      <label>Inspect candidate<select aria-label="Inspect candidate" value={event} onChange={(e) => setEvent(e.target.value)}><option value="best">Best solution</option>{edits.map((e) => <option key={e.event} value={e.event}>Iteration {e.iteration} · {e.action} · {e.accepted ? "accepted" : "rejected"}</option>)}</select></label>
      {data?.initial_decisions && decision && <><div className="form-grid"><Layout title="Initial layout" decision={data.initial_decisions} shelves={data.shelves} boundary={data.floorplan.boundary} /><Layout title="Selected candidate layout" decision={decision} shelves={data.shelves} boundary={data.floorplan.boundary} /></div>
        <div className="table-scroll"><table><thead><tr><th>Category</th><th>Initial shelf</th><th>Selected shelf</th></tr></thead><tbody>{Object.entries(decision.assignment).map(([id, shelf]) => <tr key={id}><td>{id}</td><td>{data.initial_decisions?.assignment[id]}</td><td>{shelf}</td></tr>)}</tbody></table></div>
        <div className="table-scroll"><table><thead><tr><th>SKU</th><th>Initial shelf / level / face / facings</th><th>Selected shelf / level / face / facings</th></tr></thead><tbody>{decision.placements.map((row) => { const old = data.initial_decisions?.placements.find((p) => p.sku === row.sku); return <tr key={row.sku}><td>{row.sku}</td><td>{old && [old.shelf_id, old.level_id, old.face, old.facings].join(" / ")}</td><td>{[row.shelf_id, row.level_id, row.face, row.facings].join(" / ")}</td></tr>; })}</tbody></table></div></>}
      <a className="button" href={`/api/research/campaigns/${campaign}/jobs/${selected}/joint`} download="joint-result.json">Download joint trace and certificate JSON</a>
    </>}
  </section>;
}
