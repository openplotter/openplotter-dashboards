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
	try:
		# https://docs.skipperapp.net/install-skipper.sh
		deb = 'deb [arch=any signed-by=/usr/share/keyrings/openrepo-skipperapp.gpg] http://packages.skipperapp.net/skipperapp/ stable main'
		sources = subprocess.check_output('apt-cache policy', shell=True).decode(sys.stdin.encoding)
		if not 'http://packages.skipperapp.net/skipperapp/' in sources:
			fo = open('/tmp/install-skipper.sh', "w")
			fo.write('apt update && apt install -y curl gnupg\n')
			fo.write('curl http://packages.skipperapp.net/skipperapp/public.gpg | gpg --yes --dearmor -o /usr/share/keyrings/openrepo-skipperapp.gpg\n')
			fo.write('echo "deb [arch=any signed-by=/usr/share/keyrings/openrepo-skipperapp.gpg] http://packages.skipperapp.net/skipperapp/ stable main" > /etc/apt/sources.list.d/openrepo-skipperapp.list\n')
			fo.write('apt update\n')
			fo.close()
			os.system('sudo bash /tmp/install-skipper.sh')
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Installing/Updating SKipper app...'))
	try:
		subprocess.call(['apt', 'install', '-y', 'skipperapp'])
		print(_('DONE'))
	except Exception as e: 
		print(_('FAILED: ')+str(e))


if __name__ == '__main__':
	main()
