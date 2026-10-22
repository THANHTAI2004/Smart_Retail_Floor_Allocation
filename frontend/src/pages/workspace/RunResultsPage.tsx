import { PlanogramViewer } from "../../features/results/PlanogramViewer";
import { SimulationAnalytics } from "../../features/results/SimulationAnalytics";
import { ReportsPage } from "../ReportsPage";
import { Suspense } from "react";
import { ArrowRight, Layers } from "lucide-react";
import { FloorplanEditor } from "../../app/FloorplanCanvas";
import type { WorkspaceModel } from "../../app/useWorkspace";
import { Badge } from "../../components/Badge";

export function RunResultsPage({ model }: { model: WorkspaceModel }) {
  const { project, page, selectRun, result, run, go, successful, comparison, compareId, setCompareId } = model;
  return (<>{project &&
    ["layout", "planogram", "simulation", "reports"].includes(page) && (
      <>
        {selectRun}
        {!result ? (
          <section className="panel empty">
            <Layers size={28} />
            <h2>
              {run ? `Trạng thái ${run.status}` : "Chưa có kết quả"}
            </h2>
            <p>
              {run?.error?.message ||
                "Chạy baseline T1–T4 để tạo phương án đầu tiên."}
            </p>
            <button onClick={() => go("runs")}>Đến lần chạy</button>
          </section>
        ) : (
          <>
            <div className="result-meta">
              <Badge status={run.status} />
              <span>Đầu vào revision {run.project_revision}</span>
              <code title={run.input_sha256}>
                SHA {run.input_sha256.slice(0, 16)}
              </code>
            </div>
            {page === "layout" && (
              <section className="panel">
                <div className="panel-heading">
                  <h2>Mặt bằng nghiệm T1</h2>
                  <span>{result.stages.T1.status}</span>
                </div>
                <Suspense
                  fallback={
                    <div className="notice">
                      Loading floorplan editor...
                    </div>
                  }
                >
                  <FloorplanEditor
                    floor={result.floorplan}
                    shelves={result.stages.T1.shelves}
                    onFloor={() => { }}
                    onShelves={() => { }}
                    readonly
                  />
                </Suspense>
                <div className="assignment-list">
                  {Object.entries(result.stages.T2.assignment).map(
                    ([c, s]) => (
                      <span key={c}>
                        {c}
                        <ArrowRight size={12} />
                        <strong>{s}</strong>
                      </span>
                    ),
                  )}
                </div>
                <small className="muted">
                  Nghiệm kệ thuộc snapshot của lần chạy. Bản vẽ nền sẽ
                  dùng snapshot khi tải chi tiết bên dưới.
                </small>
              </section>
            )}
            {page === "planogram" && (
              <PlanogramViewer result={result} />
            )}
            {page === "simulation" && (
              <SimulationAnalytics result={result} />
            )}
            {page === "reports" && (
              <ReportsPage
                run={run}
                result={result}
                successful={successful}
                comparison={comparison}
                compareId={compareId}
                setCompareId={setCompareId}
              />
            )}
          </>
        )}
      </>
    )}</>);
}
