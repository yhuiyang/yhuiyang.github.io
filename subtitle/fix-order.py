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

import os, argparse
from operator import itemgetter


def main():

	parser = argparse.ArgumentParser(description='Fix out of order movie subtitile. (only for srt format).')
	parser.add_argument('src_file', help='The source subtitle file you want to fix the order.')
	parser.add_argument('dst_file', help='The destination subtitle file you want to write to.')

	args = parser.parse_args()

	# verify scr file
	if not args.src_file.endswith('.srt'):
		print('Specific source subtitle file is not a scr file, do nothing and quit.')
		return
	if not args.dst_file.endswith('.srt'):
		print('Specific destination subtitle file is not a scr file, do nothing and quit.')
		return
	if not os.path.isfile(args.src_file):
		print("Specific source subtitle file, '%s', doesn't exist, do nothing and quit." % args.src_file)
		return

	# read source file
	subtitle_list = list()
	subtitle = list()
	for line in open(args.src_file, 'r'):
		stripped_line = line.strip()
		if len(stripped_line) == 0: # end mark
			if len(subtitle) > 0:
				subtitle_list.append(subtitle)
			subtitle = list()
		else:
			subtitle.append(stripped_line)

	sorted_subtitle_list = sorted(subtitle_list, key=itemgetter(1), reverse=False)

	idx = 1
	f = open(args.dst_file, 'w')
	for subtitle in sorted_subtitle_list:
		f.write('%d\n' % idx)
		f.write('%s\n' % subtitle[1])
		i = 2
		while i < len(subtitle):
			f.write('%s\n' % subtitle[i])
			i += 1
		f.write('\n')
		idx += 1
	f.close()


if __name__ == '__main__':
	main()
