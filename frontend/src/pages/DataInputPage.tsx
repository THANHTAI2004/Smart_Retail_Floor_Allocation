import { InputEditor } from "../components/InputEditor";
import { categoryDefinition } from "../features/categories/definition";
import { productDefinition } from "../features/products/definition";
import { shelfDefinition } from "../features/shelves/definition";
import { demandDefinition } from "../features/demand/definition";
import { orderDefinition } from "../features/orders/definition";
import { optimizationDefinition } from "../features/optimization/definition";
import type { Project, Section } from "../types/models";

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
