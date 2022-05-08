#!/usr/bin/env python3

# This file is part of OpenPlotter.
# Copyright (C) 2022 by Sailoog <https://github.com/openplotter/openplotter-dashboards>
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

import os, subprocess
from openplotterSettings import conf
from openplotterSettings import language

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-dashboards',currentLanguage)

	print(_('Uninstalling InfluxDB OSS 2.x...'))
	try:
		subprocess.call(['systemctl', 'disable', 'influxdb'])
		subprocess.call(['systemctl', 'disable', 'telegraf'])
		subprocess.call(['systemctl', 'stop', 'telegraf'])
		subprocess.call(['pkill','-15','telegraf'])
		subprocess.call(['systemctl', 'stop', 'influxdb'])
		os.system('rm -rf '+conf2.home+'/.openplotter/telegraf')
		subprocess.call(['apt', 'autoremove', '-y', 'influxdb2', 'telegraf'])
		subprocess.call(['systemctl', 'daemon-reload'])
		os.system('rm -f /etc/apt/sources.list.d/influxdb.list')
		os.system('apt update')
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
