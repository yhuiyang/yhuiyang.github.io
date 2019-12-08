#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
# Copyright 2018 YH Yang <yhuiyang@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################

import os, argparse, subprocess

def find_serial_from_devices(serial, devices):
    '''Find first device within connected devices with partial matched serial.'''
    for device in devices:
        if device.get('s').startswith(serial):
            return device.get('s')
    return None

 
def pull():
    
    parser = argparse.ArgumentParser(description='Pull specificed database file of debuggable app from device.')
    parser.add_argument('-s', metavar='serial', dest='serial', help='device serial')
    parser.add_argument('-o', metavar='output_file', dest='output', help='output file name')
    parser.add_argument('-p', metavar='package', dest='package', required=True, help='package name')
    parser.add_argument('file', help='database file name')
    args = parser.parse_args()

    # TODO: parameter verification

    # collect connected devices info
    devices = list()  # [{'s':'serial', 'di':'device info'}, {}, ...]
    connected_devices = subprocess.check_output(['adb', 'devices', '-l'])
    for output in connected_devices.splitlines():
        s = None
        di = None
        if len(output) and not output.startswith('List of devices attached'):
            o = output.split()
            s = o[0]
            di = ' '.join(o[1:])
        if s is not None and di is not None:
            devices.append({'s':s, 'di':di})
    
    target_device_serial = None
    # quit if no device connected
    if len(devices) == 0:
        print 'No device connected, abort!\n'
        return
    # ask user if multiple devices connected and not specific in argument
    elif len(devices) > 1:

        msg = None
        if args.serial is None:
            msg = 'No specific device serial assigned. '
        elif find_serial_from_devices(args.serial, devices) is None:
            msg = 'Specificed device serial does not exists. '
        
        if msg is not None:
            print '%s Please select which device you want to pull database file from' % (msg,)
            for ask_user_attempt in range(5):
                for idx, val in enumerate(devices):
                    print(' %d) %s, %s' % (idx, val['s'], val['di']))
                user_select_str = raw_input('Your selection (0-%d)? ' % (idx,))
                try:
                    user_select_int = int(user_select_str)
                except ValueError:
                    print ''
                    continue
                if user_select_int >= 0 and user_select_int <= idx:
                    target_device_serial = devices[user_select_int].get('s')
                    break
                else:
                    print ''
            else:
                print 'Select invalid # too many times, bye bye!'
                return
        else:
            target_device_serial = find_serial_from_devices(args.serial, devices)
    # apply action on the only device
    else:
        target_device_serial = devices[0].get('s')

    if target_device_serial is None:
        print 'Oops! Not sure where to pull file from.'
        return

    print '''\nPulling database file '%s' from device %s...''' % (args.file, target_device_serial)
    
    # adb shell "run-as package.name chmod 666 /data/data/package.name/databases/file"
    # adb exec-out run-as package.name cat databases/file > newOutFileName
    # adb shell "run-as package.name chmod 600 /data/data/package.name/databases/file"

    #subprocess.call(['adb', '-s', target_device_serial, 'shell', 'run-as ' + args.package + ' chmod 666 /data/data/' + args.package + '/databases/' + args.file])
    print 'Speicificed file in device:'
    print subprocess.check_output(['adb', '-s', target_device_serial, 'shell', 'run-as ' + args.package + ' ls -l /data/data/' + args.package + '/databases/' + args.file])
    try:
        bytestring_content = subprocess.check_output(['adb', '-s', target_device_serial, 'exec-out', 'run-as', args.package, 'cat', 'databases/' + args.file])
        f = open(args.output if args.output else args.file, 'wb')
        f.write(bytestring_content)
        f.close()
    except CalledProcessError as e:
        print 'Return code: %d\nOutput: %s' % (e.returncode, e.output)
    #subprocess.call(['adb', '-s', target_device_serial, 'shell', 'run-as ' + args.package + ' chmod 600 /data/data/' + args.package + '/databases/' + args.file])
    
    
if __name__ == '__main__':
    pull()
