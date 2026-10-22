export function Badge({ status }: { status: string }) {
  return <span className={`badge ${status.toLowerCase()}`}>{status.replaceAll("_", " ")}</span>;
}
