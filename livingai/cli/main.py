"""
LivingAI CLI Main
================

Main CLI entry point.
"""

import sys
from livingai.agentic_loop import agentic_loop


def main():
    """Main CLI entry point."""
    print("LivingAI CLI - Starting agentic loop...")
    loop = agentic_loop
    loop.run_continuous()
    print("Press Ctrl+C to stop...")
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        loop.stop()
        print("Agentic loop stopped.")


if __name__ == '__main__':
    main()
