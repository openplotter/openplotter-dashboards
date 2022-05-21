#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by Sailoog <https://github.com/openplotter/openplotter-dashboards>
#                  
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import os, subprocess, sys
from openplotterSettings import conf
from openplotterSettings import language

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-dashboards',currentLanguage)

	print(_('Checking sources...'))
	codeName = conf2.get('GENERAL', 'codeName')
	try:
		deb = 'deb https://repos.influxdata.com/debian '+codeName+' stable'
		sources = subprocess.check_output('apt-cache policy', shell=True).decode(sys.stdin.encoding)
		if not 'https://repos.influxdata.com/debian '+codeName in sources:
			fo = open('/etc/apt/sources.list.d/influxdb.list', "w")
			fo.write(deb)
			fo.close()
			os.system('cat '+currentdir+'/data/sources/influxdb.gpg.key | gpg --dearmor > "/etc/apt/trusted.gpg.d/influxdb.gpg"')
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Installing/Updating InfluxDB OSS 2.x...'))
	try:
		os.system('apt update')
		subprocess.call(['apt', 'install', '-y', 'influxdb2', 'telegraf'])
		subprocess.call(['systemctl', 'daemon-reload'])
		subprocess.call(['systemctl', 'disable', 'telegraf'])
		subprocess.call(['systemctl', 'stop', 'telegraf'])
		telegrafConf = '''[agent]
  interval = "10s"
  round_interval = false
  metric_batch_size = 1000
  metric_buffer_limit = 10000
  collection_jitter = "2s"
  collection_offset = "0s"
  flush_interval = "10s"
  flush_jitter = "2s"
  precision = "1s"
  omit_hostname = true'''
		fo = open('/etc/telegraf/telegraf.conf', "w")
		fo.write(telegrafConf)
		fo.close()
		subprocess.call(['systemctl', 'enable', 'influxdb'])
		subprocess.call(['systemctl', 'restart', 'influxdb'])

		print(_('DONE'))
	except Exception as e: 
		os.system('rm -f /etc/apt/sources.list.d/influxdb.list')
		print(_('FAILED: ')+str(e))


if __name__ == '__main__':
	main()
