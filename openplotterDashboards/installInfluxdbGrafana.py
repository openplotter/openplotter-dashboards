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

import os, subprocess
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-dashboards',currentLanguage)

	try:
		platform2 = platform.Platform()

		subprocess.call(['apt', 'install', '-y', 'grafana', 'influxdb', 'kapacitor', 'chronograf'])

		subprocess.call(['npm', 'i', '--verbose', 'signalk-to-influxdb'], cwd = platform2.skDir)
		subprocess.call(['chown', '-R', conf2.user, platform2.skDir])

		subprocess.call(['systemctl', 'stop', 'chronograf'])
		subprocess.call(['systemctl', 'stop', 'influxdb'])
		subprocess.call(['systemctl', 'stop', 'kapacitor'])
		subprocess.call(['systemctl', 'stop', 'grafana-server'])

		subprocess.call(['sed', '-i', 's/http_port = 3000/http_port = 3001/g', '/usr/share/grafana/conf/defaults.ini'])
		subprocess.call(['sed', '-i', 's/;http_port = 3000/http_port = 3001/g', '/etc/grafana/grafana.ini'])

		fo = open('/etc/default/chronograf', "w")
		fo.write( 'PORT=8889')
		fo.close()

		subprocess.call(['systemctl', 'unmask', 'influxdb.service'])
		subprocess.call(['systemctl', 'enable', 'influxdb.service'])
		subprocess.call(['systemctl', 'start', 'influxdb'])
		subprocess.call(['systemctl', 'enable', 'kapacitor.service'])
		subprocess.call(['systemctl', 'start', 'kapacitor'])
		subprocess.call(['systemctl', 'enable', 'grafana-server.service'])
		subprocess.call(['systemctl', 'start', 'grafana-server'])
		subprocess.call(['systemctl', 'start', 'chronograf'])

		subprocess.call(['systemctl', 'stop', 'signalk.service'])
		subprocess.call(['systemctl', 'stop', 'signalk.socket'])
		subprocess.call(['systemctl', 'start', 'signalk.socket'])
		subprocess.call(['systemctl', 'start', 'signalk.service'])

		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
