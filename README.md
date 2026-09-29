# System Detective - CIE-1

Evidence and programs for a live Linux system inspection. System-command output was captured on 2026-09-27; locality runs and dashboard screenshots were captured across 2026-09-27 and 2026-09-28 on this Omarchy Linux host. Live memory and process values will naturally differ on a later run.

## Reproduce

From this directory:

```sh
lscpu
free -h
top -b -n 1
ps -eLf
strace -c /usr/bin/true
```

The captured outputs are saved in `evidence/`. Rebuild and repeat the row-major/column-major experiment with:

```sh
gcc -O2 -fno-tree-vectorize -Wall -Wextra -std=c11 locality.c -o locality
./locality | tee evidence/locality.csv
```

There are three paired runs; the first order alternates to reduce order bias. The benchmark traverses the same 4096 x 4096 `uint64_t` matrix and prints a checksum so both loop orders can be checked against each other.

Start the dashboard with:

```sh
/usr/bin/python dashboard/server.py
```

Open <http://127.0.0.1:8765>. It reads the CPU model from `lscpu`, memory from `/proc/meminfo`, and process state/usage from `ps` on each refresh. The locality button reruns the compiled program and updates `evidence/locality.csv`. The server binds only to localhost.

## Before submitting

Replace the roll-number/name placeholders in the report, put the final report and AI log PDFs in this folder, and create the requested ZIP using the filename format supplied by the course. Rewrite the report interpretation in your own words and verify the live dashboard during your demo.

## Two-day finish plan

- **Day 1:** Rerun the five commands, capture any refreshed output, run the locality program at least three paired times, start the dashboard, and save screenshots of the real readings.
- **Day 2:** Check the CPU/memory/process readings and PDF pages, fill in your identity, review the AI log against the saved `ps` manual excerpt, create the ZIP, and rehearse the 2-3 minute live demo.