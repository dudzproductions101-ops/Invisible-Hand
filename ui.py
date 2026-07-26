import os
import sys

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def progress_bar(current, total, width=20):
    if total <= 0:
        return "[" + "-" * width + "] 0%"
    ratio = current / total
    if ratio > 1:
        ratio = 1
    filled = int(ratio * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"

def sparkline(data):
    if not data:
        return ""
    chars = "▁▂▃▄▅▆▇█"
    mn = min(data)
    mx = max(data)
    if mx == mn:
        return chars[0] * len(data)
    out = []
    for v in data:
        idx = int((v - mn) / (mx - mn) * (len(chars) - 1))
        out.append(chars[idx])
    return "".join(out)

def dashboard(stats, active_threads, total_threads, smart_mode, banner):
    sys.stdout.write("\033[H")
    sys.stdout.write(banner + "\n")
    sys.stdout.write("INVISIBLE HAND v7.4 — LIVE DASHBOARD\n")
    sys.stdout.write("──────────────────────────────────────────────────────────────────────────────\n")

    total = stats["total"]
    errors = stats["errors"]
    timeouts = stats["timeouts"]
    times = stats["times"]

    sys.stdout.write(f" THREADS: {active_threads}/{total_threads}    SMART MODE: {'ON' if smart_mode else 'OFF'}\n")
    sys.stdout.write(f" REQUESTS: {total}    ERRORS: {errors}    TIMEOUTS: {timeouts}\n\n")

    sys.stdout.write(" WORKERS:\n")

    left = []
    right = []

    for i in range(total_threads):
        bar = progress_bar(i + 1, total_threads)
        txt = f"worker {i+1} {bar}"
        if i % 2 == 0:
            left.append(txt)
        else:
            right.append(txt)

    rows = max(len(left), len(right))

    for r in range(rows):
        l = left[r] if r < len(left) else ""
        rr = right[r] if r < len(right) else ""
        sys.stdout.write(f"{l:<35}{rr}\n")

    sys.stdout.write("\n LATENCY GRAPH:\n")
    if times:
        sys.stdout.write(" " + sparkline(times[-40:]) + "\n")
    else:
        sys.stdout.write(" (no data yet)\n")

    sys.stdout.write("\n CONTROLS: Q = Stop | P = Pause | R = Resume\n")
    sys.stdout.write("──────────────────────────────────────────────────────────────────────────────\n")
    sys.stdout.flush()
