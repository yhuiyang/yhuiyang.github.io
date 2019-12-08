#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import subprocess

# See https://stackoverflow.com/questions/33441138/how-to-find-out-activity-names-in-a-package-android-adb-shell
# adb shell dumpsys package | grep -Eo "^[[:space:]]+[0-9a-f]+[[:space:]]+com.whatsapp/[^[:space:]]+" | grep -oE "[^[:space:]]+$"

def get_device_list(prefer=None):
    connected_devices = list()
    adb_devices_detail = subprocess.check_output(['adb', 'devices'])
    for device_detail in adb_devices_detail.splitlines()[1:]:
        if len(device_detail):
            details = device_detail.split('\t')
            serial = details[0]
            status = details[1]
            if len(serial) and status == 'device':
                connected_devices.append(serial)

    if prefer and len(prefer) > 0 and len(connected_devices) > 0:
        preferred_devices = list()
        if type(prefer) is list:
            for p in prefer:
                if p in connected_devices:
                    preferred_devices.append(p)
            return preferred_devices
        elif type(prefer) is str:
            if prefer in connected_devices:
                preferred_devices.append(prefer)
            return preferred_devices
        else:
            print('Unrecognized prefer type {}'.format(type(prefer)))

    return connected_devices


def main():

    parser = argparse.ArgumentParser(description='Dump activities, services, and broad receviers for specific package on device.')
    parser.add_argument('-s', '--serial', action='append', type=str, default=list(), help='device serial number.')
    parser.add_argument('package', help='The app package name.')

    args = parser.parse_args()

    devices = get_device_list(args.serial)

    for d in devices:
        print('''Dump package '{}' on device '{}'.'''.format(args.package, d))

        cmd1 = ['adb', '-s', d, 'shell', 'dumpsys', 'package']
        cmd2 = ['grep', '-Eo', '^[[:space:]]+[0-9a-f]+[[:space:]]+{}/[^[:space:]]+'.format(args.package)]
        cmd3 = ['grep', '-oE', '[^[:space:]]+$']

        p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(cmd2, stdin=p1.stdout, stdout=subprocess.PIPE)
        p3 = subprocess.Popen(cmd3, stdin=p2.stdout, stdout=subprocess.PIPE)
        print p3.communicate()[0]
        p2.wait()
        p1.wait()

if __name__ == '__main__':
    main()
