"""Run on the board through mpremote, not directly with desktop Python."""

import sys


def main():
    if sys.implementation.name != "micropython":
        print("Run this script ON THE BOARD using mpremote run board_info.py.")
        return

    import os
    import machine

    print("BOARD DIAGNOSTIC")
    print("Python version:", sys.version)
    print("Implementation:", sys.implementation)
    print("Firmware-reported board:", os.uname())
    print("I2S class available:", hasattr(machine, "I2S"))
    print("Current directory:", os.getcwd())
    print("Root entries:", os.listdir("/"))
    stats = os.statvfs("/")
    unit = stats[1]
    total = unit * stats[2]
    free = unit * stats[3]
    available = unit * stats[4]
    print("Filesystem total bytes:", total)
    print("Filesystem free bytes:", free)
    print("Filesystem available bytes:", available)
    print("Filesystem total MiB: {:.3f}".format(total / (1024 * 1024)))
    print("Filesystem available MiB: {:.3f}".format(available / (1024 * 1024)))
    print("Reported filesystem size is not a physical flash-capacity test.")
    print("I2S class presence does not verify wiring or audio output.")


if __name__ == "__main__":
    main()