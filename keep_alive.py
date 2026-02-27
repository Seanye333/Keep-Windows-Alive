"""
Keep Windows active and prevent sleep/screensaver while running.
Uses Windows SetThreadExecutionState API — no pip install required.
Optionally moves the mouse slightly every interval as a secondary method.

Usage:
    python keep_alive.py              # default: API only, runs until Ctrl+C
    python keep_alive.py --mouse      # also nudge mouse every 60s
    python keep_alive.py --interval 30 --mouse
"""

import ctypes
import time
import sys
import argparse
import signal

# Windows execution state flags
ES_CONTINUOUS       = 0x80000000
ES_SYSTEM_REQUIRED  = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002  # keeps screen on too

def prevent_sleep():
    """Tell Windows not to sleep or turn off the display."""
    result = ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )
    if result == 0:
        print("[ERROR] SetThreadExecutionState failed. Are you on Windows?")
        sys.exit(1)

def allow_sleep():
    """Restore normal sleep behaviour when the script exits."""
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

def nudge_mouse():
    """Move the mouse 1 pixel right then back — barely noticeable."""
    try:
        import ctypes
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        ctypes.windll.user32.SetCursorPos(pt.x + 1, pt.y)
        time.sleep(0.05)
        ctypes.windll.user32.SetCursorPos(pt.x, pt.y)
    except Exception as e:
        print(f"[WARN] Mouse nudge failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Keep Windows awake.")
    parser.add_argument("--mouse", action="store_true",
                        help="Also nudge the mouse every interval")
    parser.add_argument("--interval", type=int, default=60,
                        help="Seconds between mouse nudges (default: 60)")
    args = parser.parse_args()

    # Restore sleep on Ctrl+C
    def on_exit(sig, frame):
        print("\n[INFO] Restoring normal sleep settings...")
        allow_sleep()
        sys.exit(0)

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    prevent_sleep()
    print("[INFO] Keep-alive active. Press Ctrl+C to stop.")
    if args.mouse:
        print(f"[INFO] Mouse nudge enabled every {args.interval}s.")

    try:
        while True:
            # Re-assert the execution state each loop (good practice)
            prevent_sleep()

            if args.mouse:
                nudge_mouse()

            time.sleep(args.interval)
    finally:
        allow_sleep()

if __name__ == "__main__":
    main()
