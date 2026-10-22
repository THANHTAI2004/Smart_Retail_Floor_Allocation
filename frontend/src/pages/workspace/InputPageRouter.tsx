import { DataInputPage } from "../DataInputPage";
import type { Section } from "../../types/models";
import { sections } from "../../app/useWorkspace";
import type { WorkspaceModel } from "../../app/useWorkspace";

export function InputPageRouter({ model }: { model: WorkspaceModel }) {
  const { project, page, busy, act, save } = model;
  return (<>{project &&
    sections.includes(page as Section) &&
    page !== "floorplan" && (
      <DataInputPage
        project={project}
        section={page as Exclude<Section, "floorplan">}
        busy={busy}
        onSave={(value) =>
          act(async () => save(page as Section, value))
        }
      />
    )}</>);
}
