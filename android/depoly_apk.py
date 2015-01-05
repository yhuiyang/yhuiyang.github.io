#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
# Copyright 2015 YH Yang <yhuiyang@gmail.com>
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


def main():

	parser = argparse.ArgumentParser(description='Deploy android apk to specific/all devices.')
	parser.add_argument('apk_file', help='The apk file you want to install on devices.')
	parser.add_argument('--all', action='store_true', help='deploy to all connected simulators and devices.')

	args = parser.parse_args()

	# verify apk file
	if not args.apk_file.endswith('.apk'):
		print('Specific file is not an apk file, do nothing and quit.')
		return
	if not os.path.isfile(args.apk_file):
		print("Specific apk file, '%s', doesn't exist, do nothing and quit." % args.apk_file)
		return

	# list connected devices
	adb_devices_detail = subprocess.check_output(['adb', 'devices', '-l'])

	# collect device info
	devices = list()
	for device_detail in adb_devices_detail.splitlines()[1:]:
		if len(device_detail):
			device = dict()
			details = device_detail.split(' ')
			device['serial'] = details[0]
			for info in details:
				if len(info):
					if info.startswith('product:'):
						device['product'] = info.split(':')[1]
					elif info.startswith('model:'):
						device['model'] = info.split(':')[1]
					elif info.startswith('device:'):
						device['device'] = info.split(':')[1]
			devices.append(device)

	# deploy to devices
	if len(devices) == 0:
		print('No device connected, do nothing and quit')
	elif len(devices) == 1 or (len(devices) > 1 and args.all):
		for device in devices:
			dev_serial = device['serial']
			deploy_to(device['serial'], args.apk_file)
	else:
		print('Multiple devices connected. Select device you want to deploy:')
		for idx, val in enumerate(devices):
			print(' %d) %s, product[%s], model[%s]' % (idx, val['serial'], val['product'], val['model']))
		print(' %d) deploy to all connected devices' % (idx + 1))
		user_select_str = raw_input('Your selection (0-%d)? ' % (idx + 1))
		try:
			user_select_int = int(user_select_str)
			if user_select_int < len(devices):
				deploy_to(devices[user_select_int]['serial'], args.apk_file)
			else:
				for device in devices:
					deploy_to(device['serial'], args.apk_file)
		except ValueError:
			print('Unknown selection, do nothing and quit.')


def deploy_to(serial, apk_file):
	print('Deploying %s to device: %s' % (os.path.basename(apk_file), serial))
	subprocess.call(['adb', '-s', serial, 'install', '-r', apk_file])


if __name__ == '__main__':
	main()
