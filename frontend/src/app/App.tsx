import { AppShell } from "./AppShell";
import { useWorkspace } from "./useWorkspace";
export default function App() { return <AppShell model={useWorkspace()} />; }
