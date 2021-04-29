#!.env/bin/python3

from datetime import datetime
import rrdtool
from time import sleep
from pathlib import Path

def main():
    now = round(datetime.now().timestamp())
    oneminago = now - 60
    cmd = f'-s {oneminago} -e {now} --step 2 --json DEF:a=db.rrd:Package_id_0:AVERAGE XPORT:a'
    print(cmd)
    js = rrdtool.xport('-s', str(oneminago), '-e', str(now), '--step', '2', '--json', 'DEF:a=db.rrd:ssCpuUser:AVERAGE', 'XPORT:a')
    print(js)

if __name__ == '__main__':
    main()

    # rrdtool xport --step 5 --json DEF:a=db.rrd:Package_id_0:AVERAGE XPORT:a > test.json