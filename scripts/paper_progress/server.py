"""Read-only local progress display for the running Smart Retail paper batch."""

import ctypes
import json
import shutil
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / "experiments/runtime/external"
ORDER = ["X1", "X4", "X2", "X2b", "X5", "X6", "X3"]
NAMES = {
    "X1": "Đúng đắn và exact",
    "X4": "Khả năng mở rộng",
    "X2": "So sánh chính",
    "X2b": "Mở rộng instance",
    "X5": "Ablation",
    "X6": "Độ nhạy",
    "X3": "Holdout cuối cùng",
}
cache = {}
lock = threading.Lock()


def read(p, fallback=None):
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return fallback


def alive(pid):
    k = ctypes.windll.kernel32
    k.OpenProcess.restype = ctypes.c_void_p
    k.CloseHandle.argtypes = [ctypes.c_void_p]
    k.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    h = k.OpenProcess(0x1000, False, pid)
    if not h:
        return False
    try:
        code = ctypes.c_ulong()
        return bool(k.GetExitCodeProcess(h, ctypes.byref(code)) and code.value == 259)
    finally:
        k.CloseHandle(h)


def snapshot():
    with lock:
        blocks = {
            b: {
                "id": b,
                "name": NAMES[b],
                "planned": 0,
                "done": 0,
                "ok": 0,
                "failed": 0,
                "active": 0,
            }
            for b in ORDER
        }
        active = []
        errors = []
        followups = {}
        retry_rows = read(ROOT / "var/paper-parallel/recovery/index.json", [])
        retry_done = retry_ok = 0
        for retry in retry_rows:
            retry_config = read(Path(retry["config"]), {})
            retry_root = (
                ROOT
                / "experiments/results/20261023-paper-v2"
                / retry_config.get("name", "missing")
            )
            requested = set(retry["target_job_keys"])
            retry_records = []
            for path in (retry_root / "records").glob("*.json"):
                key = str(path)
                if key not in cache or cache[key] is None:
                    cache[key] = read(path)
                if cache[key]:
                    retry_records.append(cache[key])
            for record in retry_records:
                if record["job_key"] in requested:
                    followups[(retry["source_campaign"], record["job_key"])] = record
                    retry_done += 1
                    retry_ok += record["status"] == "SUCCEEDED"
            owner = read(retry_root / ".supervisor.lock", {})
            if owner.get("pid") and alive(owner["pid"]):
                active.append(
                    {
                        "name": retry_config["name"] + " (chạy bù / chạy lại)",
                        "done": len(retry_records),
                        "planned": retry["jobs"],
                        "pid": owner["pid"],
                    }
                )
                blocks[retry["source_block"]]["active"] += 1
        recovery = read(RUNTIME / "disk-job-recovery-v2/recovery-receipt.json", {})
        index = read(ROOT / "experiments/configs/paper-v2/index.json", [])
        for row in index:
            cfg = read(ROOT / "experiments/configs/paper-v2" / row["config"], {})
            root = (
                ROOT
                / "experiments/results/20261023-paper-v2"
                / cfg.get("name", "missing")
            )
            b = blocks[row["block"]]
            b["planned"] += row["jobs"]
            owner = read(root / ".supervisor.lock", {})
            running = bool(owner.get("pid") and alive(owner["pid"]))
            records = []
            for p in (root / "records").glob("*.json"):
                key = str(p)
                if key not in cache or cache[key] is None:
                    cache[key] = read(p)
                if cache[key]:
                    records.append(cache[key])
            original_keys = {record["job_key"] for record in records}
            records.extend(
                record
                for (campaign, key), record in followups.items()
                if campaign == cfg["name"] and key not in original_keys
            )
            b["done"] += len(records)
            b["ok"] += sum(r["status"] == "SUCCEEDED" for r in records)
            b["failed"] += sum(r["status"] != "SUCCEEDED" for r in records)
            if running:
                b["active"] += 1
                active.append(
                    {
                        "name": cfg["name"],
                        "done": len(records),
                        "planned": row["jobs"],
                        "pid": owner["pid"],
                    }
                )
            for r in records:
                if r["status"] != "SUCCEEDED":
                    errors.append(
                        {
                            "campaign": cfg["name"],
                            "code": (r.get("error") or {}).get("code", r["status"]),
                            "seed": r.get("seed"),
                            "fold": r.get("cv_fold"),
                            "recovered": followups.get(
                                (cfg["name"], r["job_key"]), {}
                            ).get("status")
                            == "SUCCEEDED"
                            or recovery.get("status") == "RECOVERED_DIAGNOSTICALLY"
                            and recovery.get("original_job_key") == r["job_key"],
                        }
                    )
        recovery_root = RUNTIME / "disk-job-recovery-v2"
        recovery_owner = read(recovery_root / ".supervisor.lock", {})
        if recovery_owner.get("pid") and alive(recovery_owner["pid"]):
            cp = read(recovery_root / "checkpoint.json", {})
            active.append(
                {
                    "name": "Khôi phục job lỗi dung lượng — kiểm tra 10 fold",
                    "done": cp.get("completed", 0),
                    "planned": 10,
                    "pid": recovery_owner["pid"],
                }
            )
        watcher = read(ROOT / "var/paper-unattended/status.json", {})
        free_d = shutil.disk_usage(ROOT).free / 1024**3
        running = bool(active)
        state = "Đang chạy" if running else "Đang chuẩn bị / kiểm tra"
        if not running and free_d < 1:
            state = "Tạm dừng — ổ D hết dung lượng"
        elif not running and watcher.get("status") == "NEEDS_ATTENTION":
            state = "Tạm dừng — đang xử lý lỗi"
        done = sum(b["done"] for b in blocks.values())
        planned = sum(b["planned"] for b in blocks.values())
        return {
            "updated": datetime.now().astimezone().isoformat(timespec="seconds"),
            "state": state,
            "running": running,
            "blocks": list(blocks.values()),
            "active": active,
            "done": done,
            "planned": planned,
            "ok": sum(b["ok"] for b in blocks.values()),
            "failed": sum(b["failed"] for b in blocks.values()),
            "percent": round(done / max(1, planned) * 100, 2),
            "free_d_gib": round(free_d, 2),
            "free_c_gib": round(shutil.disk_usage("C:/").free / 1024**3, 1),
            "watcher": watcher.get("status", "Chưa có"),
            "errors": errors[-8:],
            "recovery": {
                "targets": sum(len(r["target_job_keys"]) for r in retry_rows),
                "executed": retry_done,
                "succeeded": retry_ok,
                "failed": retry_done - retry_ok,
                "paired_duplicates_excluded": sum(
                    len(r["paired_extra_job_keys"]) for r in retry_rows
                ),
            },
        }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.split("?")[0] == "/api/progress":
                data = json.dumps(snapshot(), ensure_ascii=False).encode()
                kind = "application/json; charset=utf-8"
            elif self.path.split("?")[0] == "/":
                data = (HERE / "index.html").read_bytes()
                kind = "text/html; charset=utf-8"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8766), Handler).serve_forever()
