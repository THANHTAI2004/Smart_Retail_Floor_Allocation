// Vai trò: Ghép hook trạng thái workspace với khung giao diện chính của ứng dụng.
import { AppShell } from "./AppShell";
import { useWorkspace } from "./useWorkspace";
// Ghép trạng thái workspace với khung giao diện chính.
export default function App() { return <AppShell model={useWorkspace()} />; }
