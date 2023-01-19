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

import os, subprocess, sys
from openplotterSettings import conf
from openplotterSettings import language

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-dashboards',currentLanguage)

	print(_('Checking sources...'))
	try:
		deb = 'deb https://apt.grafana.com stable main'
		sources = subprocess.check_output('apt-cache policy', shell=True).decode(sys.stdin.encoding)
		if not 'https://apt.grafana.com stable' in sources:
			fo = open('/etc/apt/sources.list.d/grafana.list', "w")
			fo.write(deb)
			fo.close()
			os.system('cat '+currentdir+'/data/sources/grafana.gpg.key | gpg --dearmor > "/etc/apt/trusted.gpg.d/grafana.gpg"')
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Installing/Updating Grafana...'))
	try:
		os.system('apt update')
		subprocess.call(['apt', 'install', '-y', 'grafana'])
		subprocess.call(['grafana-cli', 'plugins', 'install', 'golioth-websocket-datasource'])
		subprocess.call(['sed', '-i', 's/http_port = 3000/http_port = 3001/g', '/usr/share/grafana/conf/defaults.ini'])
		subprocess.call(['sed', '-i', 's/;http_port = 3000/http_port = 3001/g', '/etc/grafana/grafana.ini'])
		subprocess.call(['systemctl', 'daemon-reload'])
		subprocess.call(['systemctl', 'enable', 'grafana-server.service'])
		subprocess.call(['systemctl', 'restart', 'grafana-server'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
