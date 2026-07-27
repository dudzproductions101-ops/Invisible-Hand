import os
import sys


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def progress_bar(current, total, width=18):
    if total <= 0:
        return "[" + "░" * width + "]"

    ratio = max(0.0, min(current / total, 1.0))
    filled = round(ratio * width)

    return "[" + ("█" * filled) + ("░" * (width - filled)) + "]"


def sparkline(data):
    if not data:
        return ""

    chars = "▁▂▃▄▅▆▇█"

    lo = min(data)
    hi = max(data)

    if lo == hi:
        return chars[0] * len(data)

    return "".join(
        chars[int((v - lo) / (hi - lo) * (len(chars) - 1))]
        for v in data
    )


def dashboard(stats, active_threads, total_threads, smart_mode, banner):
    import sys

    sys.stdout.write("\033[H")

    WIDTH = 76

    def line(text=""):
        text = str(text)
        return "| " + text.ljust(WIDTH - 2)[:WIDTH - 2] + " |\n"

    def border(char="-"):
        return "+" + (char * WIDTH) + "+\n"

    total = stats.get("total", 0)
    errors = stats.get("errors", 0)
    timeouts = stats.get("timeouts", 0)
    times = stats.get("times", [])

    sys.stdout.write(banner.rstrip() + "\n")

    sys.stdout.write(border("="))
    sys.stdout.write(line("SYSTEM DASHBOARD"))
    sys.stdout.write(border("="))

    sys.stdout.write(
        line(
            f"Threads: {active_threads}/{total_threads}    "
            f"Smart Mode: {'ON' if smart_mode else 'OFF'}"
        )
    )

    sys.stdout.write(
        line(
            f"Requests: {total}    Errors: {errors}    Timeouts: {timeouts}"
        )
    )

    sys.stdout.write(border("-"))

    sys.stdout.write(line("Workers"))

    for i in range(total_threads):
        bar = progress_bar(i + 1, total_threads)
        sys.stdout.write(
            line(f"Worker {i+1:02d} {bar}")
        )

    sys.stdout.write(border("-"))

    sys.stdout.write(line("Latency"))

    graph = sparkline(times[-50:]) if times else "(no data)"
    sys.stdout.write(line(graph))

    sys.stdout.write(border("-"))
    sys.stdout.write(line("Q Quit | P Pause | R Resume"))
    sys.stdout.write(border("="))

    sys.stdout.flush()
