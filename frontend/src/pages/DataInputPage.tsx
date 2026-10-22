import { InputEditor } from "../components/InputEditor";
import { categoryDefinition } from "../features/categories/definition";
import { productDefinition } from "../features/products/definition";
import { shelfDefinition } from "../features/shelves/definition";
import { demandDefinition } from "../features/demand/definition";
import { orderDefinition } from "../features/orders/definition";
import { optimizationDefinition } from "../features/optimization/definition";
import type { Project, Section } from "../types/models";
import { useState } from "react";

type DataSection = Exclude<Section, "floorplan">;
interface Definition {
  title: string;
  defaultValue: unknown;
  template?: Record<string, unknown>;
  note: string;
}
const definitions: Record<DataSection, Definition> = {
  shelves: shelfDefinition,
  categories: categoryDefinition,
  products: productDefinition,
  demand: demandDefinition,
  orders: orderDefinition,
  optimization: optimizationDefinition,
};
export function DataInputPage({
  project,
  section,
  busy,
  onSave,
}: {
  project: Project;
  section: DataSection;
  busy: boolean;
  onSave: (value: unknown) => Promise<void>;
}) {
  const definition = definitions[section];
  const [csvError, setCsvError] = useState("");
  const [importing, setImporting] = useState(false);
  const tabular = ["shelves", "categories", "products", "orders"].includes(section);
  const template =
    section === "products"
      ? {
        ...definition.template,
        category_id:
          (
            project.sections.categories?.items as { id: string }[] | undefined
          )?.[0]?.id || "CAT1",
      }
      : definition.template;
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>{definition.title}</h2>
        <span>{project.completion[section] ? "Đã lưu" : "Chưa lưu"}</span>
      </div>
      <p className="notice">{definition.note}</p>
      <div className="actions">
        <a className="button" href={`/api/projects/${project.id}/inputs/${section}/export?format=json`} download={`${section}.json`}>Xuất JSON đã lưu</a>
        {tabular && <>
          <a className="button" href={`/api/projects/${project.id}/inputs/${section}/export?format=csv`} download={`${section}.csv`}>Xuất CSV đã lưu</a>
          <label className="file-button">{importing ? "Đang nhập CSV…" : "Nhập và lưu CSV"}
            <input type="file" accept=".csv,text/csv" disabled={busy || importing} onChange={async (event) => {
              const file = event.target.files?.[0];
              if (!file) return;
              setImporting(true); setCsvError("");
              try {
                if (file.size > 10000000) throw new Error("CSV vượt giới hạn 10 MB");
                const response = await fetch(`/api/projects/${project.id}/inputs/${section}/import-csv`, {
                  method: "POST", headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ text: await file.text(), expected_revision: project.revision }),
                });
                if (!response.ok) throw new Error(`${response.status}: ${await response.text()}`);
                window.location.reload();
              } catch (error) { setCsvError(String(error)); setImporting(false); }
            }} />
          </label>
        </>}
      </div>
      {csvError && <p role="alert" className="notice error">{csvError}</p>}
      <InputEditor
        key={`${project.id}-${section}-${project.revision}`}
        label={`JSON ${section}`}
        value={project.sections[section] || definition.defaultValue}
        template={template}
        busy={busy}
        onSave={onSave}
      />
    </section>
  );
}
