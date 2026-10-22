"""Isolated deployment checks. Secret values never appear in receipts or logs."""

import argparse
import json
import os
import secrets
import shutil
import socket
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen
from uuid import uuid4

from smart_retail.application import projects
from smart_retail.application.workflow import canonical_hash
from smart_retail.infrastructure.mongodb.client import connect
from smart_retail.workers.runner import work_once

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def atlas(output, record):
    uri = os.getenv("MONGODB_ATLAS_URI")
    if not uri:
        record.update(status="BLOCKED", blocker="BLOCKED_ATLAS_CREDENTIALS")
        return 2
    # Dedicated variable is explicit authorization to write to a fresh namespace;
    # never reuse the main application's URI/database as an implicit Atlas target.
    if not uri.startswith("mongodb+srv://") or ".mongodb.net" not in uri.split("?", 1)[0]:
        raise ValueError("Atlas SRV URI required privately in MONGODB_ATLAS_URI")
    name = "sr_atlas_verify_" + uuid4().hex[:20]
    store, factory = connect(uri, database=name)
    record["database"] = name
    try:
        # PyMongo SRV defaults TLS on; explicitly disallow opt-out/insecure TLS.
        from pymongo.uri_parser import parse_uri
        options = parse_uri(uri)["options"]
        if options.get("tls") is False or any(options.get(k) for k in (
            "tlsInsecure", "tlsAllowInvalidCertificates", "tlsAllowInvalidHostnames")):
            raise ValueError("Validated TLS is required for Atlas")
        store.ready()
        hello = store.database.command("hello")
        record["tls"] = "SRV TLS enabled with certificate validation; live ping succeeded"
        record["replica_set_detected"] = bool(hello.get("setName"))
        project = projects.create_project(store, "Isolated Atlas verification")
        sample = json.loads((ROOT / "datasets/samples/small_store.json").read_text(encoding="utf-8"))
        for section, value in sample.items():
            project = projects.save_section(store, project["id"], section, value, project["revision"])
        try:
            projects.save_section(store, project["id"], "demand", sample["demand"], 0)
            raise AssertionError("Stale revision accepted")
        except projects.ServiceError as exc:
            assert exc.status == 409
        job = projects.enqueue(store, project["id"])
        assert work_once(factory, output / "artifacts", heartbeat_id="atlas-verifier")
        final = store.get_run(job["id"])
        assert final.status == "SUCCEEDED"
        assert canonical_hash(final.result) == final.result_sha256
        record["checks"] = ["SRV/DNS/TLS/auth ping", "index creation", "CRUD",
                            "conditional revision", "atomic queue", "spawned T1-T4", "result SHA"]
        # Recreate the client for an explicit reconnect/readback check.
        store.dispose()
        store, _ = connect(uri, database=name)
        assert store.get_run(job["id"]).result_sha256 == final.result_sha256
        record["reconnect"] = "PASS"
        # Only documents created by this verifier, in its UUID namespace.
        store.database.optimization_runs.delete_one({"_id": job["id"]})
        store.database.projects.delete_one({"_id": project["id"]})
        record.update(status="PASS", test_documents_deleted=True, collections_retained=True)
        return 0
    finally:
        store.dispose()


def compose(output, record):
    docker = shutil.which("docker")
    if not docker and sys.platform == "win32":
        candidate = Path(os.environ["LOCALAPPDATA"]) / "Programs/DockerDesktop/resources/bin/docker.exe"
        docker = str(candidate) if candidate.is_file() else None
    if not docker:
        record.update(status="BLOCKED", blocker="BLOCKED_DOCKER_RUNTIME")
        return 2
    # Freshly installed per-user Docker may not yet be in this parent's PATH;
    # buildx also needs the adjacent credential helper, not only docker.exe.
    os.environ["PATH"] = str(Path(docker).parent) + os.pathsep + os.environ.get("PATH", "")
    project = "srverify" + uuid4().hex[:12]
    database = "sr_compose_" + uuid4().hex[:16]
    api_port, web_port = free_port(), free_port()
    password = secrets.token_urlsafe(32)
    uri = f"mongodb://verify:{password}@database:27017/?authSource=admin"
    private = ROOT / "var" / (project + ".env")
    private.parent.mkdir(exist_ok=True)
    private.write_text(f"MONGODB_ROOT_USER=verify\nMONGODB_ROOT_PASSWORD={password}\nMONGODB_URI={uri}\n"
                       f"MONGODB_DATABASE={database}\nSMART_RETAIL_API_PORT={api_port}\nSMART_RETAIL_WEB_PORT={web_port}\n")
    base = [docker, "compose", "--project-name", project, "--env-file", str(private),
            "-f", str(ROOT / "docker-compose.yml")]
    record.update(project=project, database=database, api_port=api_port, web_port=web_port,
                  volumes_retained=True, private_env_in_ignored_var=True)
    commands = record.setdefault("commands", [])

    def run(*args, input_text=None, timeout=600):
        started = datetime.now(UTC).isoformat()
        result = subprocess.run([*base, *args], input=input_text, capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=timeout)
        # Never persist compose config, expanded URI, authenticated command output.
        commands.append({"arguments": list(args) if not input_text else list(args[:3]) + ["<verification code via stdin>"],
                         "started_utc": started, "ended_utc": datetime.now(UTC).isoformat(),
                         "exit_code": result.returncode})
        if args[0] != "config":
            for label, content in [("stdout", result.stdout), ("stderr", result.stderr)]:
                sanitized = content.replace(uri, "<private-uri>").replace(password, "<private-password>")
                (output / f"command-{len(commands)-1:02d}.{label}.log").write_text(sanitized, encoding="utf-8")
        if result.returncode:
            raise RuntimeError("Compose check failed; command index " + str(len(commands) - 1))
        return result.stdout

    def request(path, value=None, method=None):
        raw = json.dumps(value).encode() if value is not None else None
        req = Request(f"http://127.0.0.1:{api_port}" + path, data=raw, method=method,
                      headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=15) as response:
            return json.load(response)

    started = False
    try:
        run("config", "--quiet")
        record["compose_config_validation"] = "PASS"
        if subprocess.run([docker, "info"], check=False, capture_output=True, timeout=30).returncode:
            record.update(status="BLOCKED", blocker="BLOCKED_DOCKER_RUNTIME", reason="Docker installed; engine unavailable")
            return 2
        run("build", "backend", "frontend")
        started = True
        run("up", "-d", "--wait", timeout=300)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            try:
                if request("/api/health")["worker_online"]:
                    break
            except Exception:
                pass
            time.sleep(.5)
        else:
            raise TimeoutError("Compose API/worker readiness")
        run("exec", "-T", "backend", "python", "-c", "from pymongo import MongoClient; from pymongo.errors import OperationFailure; c=MongoClient('mongodb://database:27017',serverSelectionTimeoutMS=3000);\ntry: c.smart_retail.projects.find_one(); raise AssertionError('Authentication disabled')\nexcept OperationFailure as e: assert e.code==13")
        p = request("/api/projects", {"name": "Compose isolated verification"})
        sample = json.loads((ROOT / "datasets/samples/small_store.json").read_text(encoding="utf-8"))
        for section, value in sample.items():
            p = request(f"/api/projects/{p['id']}/inputs/{section}?expected_revision={p['revision']}", value, "PUT")
        job = request(f"/api/projects/{p['id']}/runs", {}, "POST")
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            final = request(f"/api/runs/{job['id']}")
            if final["status"] in ("SUCCEEDED", "FAILED", "TIMED_OUT", "INFEASIBLE"):
                break
            time.sleep(.5)
        assert final["status"] == "SUCCEEDED"
        assert canonical_hash(final["result"]) == final["result_sha256"]
        request(f"/api/runs/{job['id']}/report")
        with urlopen(f"http://127.0.0.1:{web_port}", timeout=10) as response:
            assert response.status == 200
        run("restart", "database", "backend", "worker", "frontend")
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            try:
                saved = request(f"/api/runs/{job['id']}")
                if saved["result_sha256"] == final["result_sha256"]:
                    break
            except Exception:
                pass
            time.sleep(.5)
        else:
            raise TimeoutError("Persistence after restart")
        run("stop", "worker")
        cancelled = request(f"/api/projects/{p['id']}/runs", {}, "POST")
        request(f"/api/runs/{cancelled['id']}/cancel", {}, "POST")
        assert request(f"/api/runs/{cancelled['id']}")["status"] == "CANCELLED"
        lost = request(f"/api/projects/{p['id']}/runs", {}, "POST")
        # Expire an owner in the isolated test database, then restart real worker.
        code = f"from smart_retail.infrastructure.mongodb.client import connect; import time; s,_=connect(); r=s.claim('dead-compose-owner',time.time()); assert r.id=={lost['id']!r}; s.database.optimization_runs.update_one({{'_id':r.id}},{{'$set':{{'lease_until':time.time()-1}}}})"
        run("exec", "-T", "backend", "python", "-", input_text=code)
        run("start", "worker")
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if request(f"/api/runs/{lost['id']}")["status"] == "TIMED_OUT":
                break
            time.sleep(.5)
        else:
            raise TimeoutError("Expired worker recovery")
        record.update(status="PASS", checks=["config/build", "auth", "indexes", "API/worker/frontend",
                      "seven inputs", "T1-T4/result/report/SHA", "restart persistence", "queued cancel", "expired worker recovery"])
        return 0
    finally:
        if started:
            result = subprocess.run([*base, "logs", "--no-color"], capture_output=True,
                                    text=True, encoding="utf-8", errors="replace", timeout=30)
            sanitized = result.stdout.replace(uri, "<private-uri>").replace(password, "<private-password>")
            (output / "compose.log").write_text(sanitized, encoding="utf-8")
            # Only this UUID project's services; no deletion and no down -v.
            subprocess.run([*base, "stop"], capture_output=True, timeout=60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", choices=["atlas", "compose"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    record = {"target": args.target, "started_utc": datetime.now(UTC).isoformat(),
              "platform": sys.platform, "status": "FAIL"}
    try:
        code = atlas(args.output, record) if args.target == "atlas" else compose(args.output, record)
    except Exception as exc:
        # PyMongo/DNS/URI exceptions can contain secrets: only publish the type.
        record.update(status="FAIL", error_type=type(exc).__name__)
        code = 1
    record.update(ended_utc=datetime.now(UTC).isoformat(), exit_code=code)
    (args.output / "verification.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(record["status"], record.get("blocker", args.target))
    return code


if __name__ == "__main__":
    sys.exit(main())
