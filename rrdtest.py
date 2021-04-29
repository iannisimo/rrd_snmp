#!.env/bin/python3

from datetime import datetime
import rrdtool
from time import sleep
from pathlib import Path

def main():
    rrdtool.xport

if __name__ == '__main__':
    main()

    rrdtool xport --step 5 \
        DEF:access=db.rrd:ssCpuUser:AVERAGE \
        XPORT:access:"average"