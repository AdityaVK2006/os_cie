#!/usr/bin/env python3
import csv
import json
import statistics
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evidence" / "locality.csv"
PROGRAM = ROOT / "locality"


def locality_data():
    with RESULTS.open(newline="") as result_file:
        rows = list(csv.DictReader(result_file))
    timings = {
        order: [float(row["seconds"]) for row in rows if row["order"] == order]
        for order in ("row-major", "column-major")
    }
    medians = {order: statistics.median(values) for order, values in timings.items()}
    return {"runs": rows, "median_seconds": medians,
            "speedup": medians["column-major"] / medians["row-major"]}


def system_data():
    cpu = json.loads(subprocess.check_output(["lscpu", "-J"], text=True))
    cpu_fields = {item["field"].rstrip(":"): item["data"]
                  for item in cpu["lscpu"]}
    with open("/proc/cpuinfo") as cpuinfo:
        first_cpu = cpuinfo.read().split("\n\n", 1)[0]
    flags_line = next((line for line in first_cpu.splitlines()
                       if line.startswith(("flags", "Features"))), "")
    flags = set(flags_line.split(":", 1)[-1].split())
    isa_flags = [flag for flag in ("sse2", "avx", "avx2", "avx512f", "aes")
                 if flag in flags]

    memory = {}
    with open("/proc/meminfo") as meminfo:
        for line in meminfo:
            key, value = line.split(":", 1)
            memory[key] = int(value.split()[0]) * 1024
    total = memory["MemTotal"]
    available = memory["MemAvailable"]

    process_output = subprocess.check_output(
        ["ps", "-eo", "pid=,stat=,comm=,%cpu=,%mem=", "--sort=-%cpu"],
        text=True,
    )
    processes = []
    for line in process_output.splitlines()[:5]:
        pid, state, *values = line.split()
        cpu_percent, memory_percent = values[-2:]
        name = " ".join(values[:-2])
        processes.append({"pid": int(pid), "state": state, "name": name,
                          "cpu": float(cpu_percent), "memory": float(memory_percent)})

    return {
        "cpu": {
            "model": cpu_fields.get("Model name", "Unknown"),
            "architecture": cpu_fields.get("Architecture", "Unknown"),
            "logical": cpu_fields.get("CPU(s)", "Unknown"),
            "cores": cpu_fields.get("Core(s) per socket", "Unknown"),
            "threads_per_core": cpu_fields.get("Thread(s) per core", "Unknown"),
            "isa_flags": isa_flags,
        },
        "memory": {"total": total, "used": total - available,
                   "available": available},
        "processes": processes,
        "locality": locality_data(),
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/status":
            body = json.dumps(system_data()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path in ("/", "/index.html"):
            body = (Path(__file__).parent / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404)

    def do_POST(self):
        if self.path != "/api/locality":
            self.send_error(404)
            return
        result = subprocess.run([str(PROGRAM)], check=True, capture_output=True,
                                text=True)
        RESULTS.write_text(result.stdout)
        body = json.dumps(locality_data()).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        print("%s - %s" % (self.log_date_time_string(), format_string % args))


if __name__ == "__main__":
    print("System Detective dashboard: http://127.0.0.1:8765")
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()