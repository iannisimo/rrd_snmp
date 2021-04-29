#!.env/bin/python3

from easysnmp import Session
from datetime import datetime
import rrdtool
from time import sleep
from pathlib import Path

hostname     = 'localhost'
community    = 'public'
version      = 2

# RRD Consts
rrd_filename = 'db.rrd' 
step         = 2
# heartbeat    = (step * 20) // 100
heartbeat    = 1
min_temp     = 0
max_temp     = 100
min_usage    = 0
max_usage    = 100

def clean_str(str):
    return str.replace(' ', '_').replace(':', '-')

def getTemps(session):
    temps = {}
    idxs = sorted({idx.value for idx in session.bulkwalk('LM-SENSORS-MIB::lmTempSensorsIndex')}, key=int)
    for idx in idxs:
        name = session.get(f'LM-SENSORS-MIB::lmTempSensorsDevice.{idx}').value
        value = str(round(int(session.get(f'LM-SENSORS-MIB::lmTempSensorsValue.{idx}').value) / 1000))
        temps[clean_str(name)] = value
    return temps

def getCpuUsage(session):
    loads = {}
    tmp = session.get(['ssCpuUser.0', 'ssCpuSystem.0', 'ssCpuIdle.0'])
    for val in tmp:
        loads[clean_str(val.oid)] = val.value
    return loads

def make_ds(name, hb, min_val, max_val):
    return f'DS:{name}:GAUGE:{hb}:{min_val}:{max_val}'

def make_rra(rra_type, xff, steps, rows):
    return f'RRA:{rra_type}:{xff}:{steps}:{rows}'

def create_rrd(temps, loads):
    rrd_file = Path(rrd_filename)
    # TODO: Non cancellare
    if(rrd_file.is_dir()):
        print(f'{rrd_filename} is a fu***ng directory, delete it or GTFO')
        exit(1)
    if(rrd_file.is_file()):
        print(f'{rrd_filename} already exists')
        return False
    ds_rra = [rrd_filename, '--step', str(step)]
    for temp in temps:
        ds_rra.append(make_ds(temp, heartbeat, min_temp, max_temp))
    for load in loads:
        ds_rra.append(make_ds(load, heartbeat, min_usage, max_usage))
    ds_rra.append(make_rra('AVERAGE', 0.5, 2, 60))
    for a in ds_rra:
        print(a)
    rrdtool.create(*ds_rra)

def main():
    session = Session(hostname, version, community)
    temps = getTemps(session)
    # print(temps)
    loads = getCpuUsage(session)
    # print(loads)
    create_rrd(temps, loads)
    update_loop(session)

def make_update(temps, loads):
    update_str = 'N'
    template_str = ''
    for t in temps:
        template_str += f':{t}'
        update_str += f':{temps[t]}'
    for l in loads:
        template_str += f':{l}'
        update_str += f':{loads[l]}'
    return (template_str[1:], update_str)

def update_loop(session):
    next_start = datetime.utcnow().timestamp()
    while(1):
        temps = getTemps(session)
        loads = getCpuUsage(session)
        (template_string, update_string) = make_update(temps, loads)
        # print(template_string)
        # print(update_string)
        print(rrd_filename, '--template', template_string, update_string)
        rrdtool.update(rrd_filename, '--template', template_string, update_string)
        next_start += step
        now = datetime.utcnow().timestamp()
        sleep((next_start - now))

if __name__ == '__main__':
    main()