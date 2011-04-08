#!/usr/bin/env python

"""
Read sensor data from a laptop and feed to pachube.com

To make this work you need a file called keys.py with the following:

    API_KEY = 'YOUR PERSONAL API KEY'
    API_URL = 'YOUR PERSONAL API URL, LIKE /api/1275.xml'

You may also wish to configure the global variables PROC_TEMP and
PROC_BATTERY which should give the paths to the directoris in /proc
which contain status information about your temperature and battery.


Copyright (C) Sarah Mount, 2011.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


__author__ = 'Sarah Mount <snim2@snim2.org>'
__date__ = 'April 2011'

# pylint: disable=W0141

import eeml


PROC_TEMP = '/proc/acpi/thermal_zone/TZ01'
PROC_BATTERY = '/proc/acpi/battery/BAT1'


def get_temp():
    """

    temperature:             63 C
    critical (S5):           107 C
    """
    temp = open(PROC_TEMP + '/temperature', 'r').readline().strip()
    trip = open(PROC_TEMP + '/trip_points', 'r').readline().strip()
    temperature = temp.split(' ')[-2]
    trip_point = trip.split(' ')[-2]
    return (temperature, trip_point)


def get_battery():
    """
    """
    state = open(PROC_BATTERY + '/state', 'r').read()
    remaining = None
    for line in state.split('\n'):
        line_a = line.split(':')
        if line_a[0] == 'remaining capacity':
            remaining = line_a[-1].strip()
    info = open(PROC_BATTERY + '/info', 'r').read()
    last_full = None
    for line in info.split('\n'):
        line_a = line.split(':')
        if line_a[0] == 'last full capacity':
            last_full = line_a[-1].strip()
    return (remaining, last_full)


def get_load():
    """
    Code by Nick Booker:
    http://www.velocityreviews.com/forums/t587425-python-system-information.html
    
    -> 5-tuple containing the following numbers in order:
    - 1-minute load average (float)
    - 5-minute load average (float)
    - 15-minute load average (float)
    - Number of threads/processes currently executing (<= number of
    CPUs) (int)
    - Number of threads/processes that exist on the system (int)
    - The PID of the most recently-created process on the system (int)
    """
    loadavgstr = open('/proc/loadavg', 'r').readline().strip()
    data = loadavgstr.split()
    avg1, avg5, avg15 = map(float, data[:3])
    threads_and_procs_running, threads_and_procs_total = map(int, data[3].split('/'))
    most_recent_pid = int(data[4])
    return avg1, avg5, avg15, threads_and_procs_running, threads_and_procs_total, most_recent_pid


def push_data():
    """Get all available data and push to Pachube.

    Needs a file called keys.py with the following:

    API_KEY = 'YOUR PERSONAL API KEY'
    API_URL = 'YOUR PERSONAL API URL, LIKE /api/1275.xml'
    """
    import keys
    current_temp, critical_temp = get_temp()
    current, last_capacity = get_battery()
    load = get_load()
    load_av, threads_and_procs_running = load[1], load[4]
    pachube = eeml.Pachube(keys.API_URL, keys.API_KEY)
    pachube.update([eeml.Data(0, current_temp),
                    eeml.Data(1, load_av),
                    eeml.Data(2, threads_and_procs_running),
                    eeml.Data(3, current),
                    eeml.Data(4, last_capacity),
                    eeml.Data(5, critical_temp)])
    pachube.put()
    return


def test():
    """Test everything...
    """
    print 'Load info:', get_load()
    print 'Temp info:', get_temp()
    print 'Battery info:', get_battery()



if __name__ == '__main__':
    push_data()
