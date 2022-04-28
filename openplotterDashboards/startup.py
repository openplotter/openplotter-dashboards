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

import time, os, subprocess, sys
from openplotterSettings import language
from openplotterSettings import platform

class Start():
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-dashboards',currentLanguage)
		self.initialMessage = ''

	def start(self):
		green = ''
		black = ''
		red = ''

		return {'green': green,'black': black,'red': red}

class Check():
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-dashboards',currentLanguage)
		self.platform = platform.Platform()
		self.nodeRed = self.platform.isSKpluginInstalled('node-red-dashboard')
		self.influx = self.platform.isSKpluginInstalled('signalk-to-influxdb')
		if os.path.isfile('/usr/share/grafana/conf/defaults.ini'): self.grafana = True
		else: self.grafana = False

		if self.nodeRed or self.influx or self.grafana: self.initialMessage = _('Checking Dashboards...')
		else: self.initialMessage = ''

	def check(self):
		green = ''
		black = ''
		red = ''

		if self.nodeRed:
			if self.platform.isSKpluginEnabled('signalk-node-red') or not os.path.exists(self.platform.skDir+'/plugin-config-data/signalk-node-red.json'):
				txt = 'Node-Red enabled'
				if not black: black = txt
				else: black += ' | '+txt
			else:
				txt = _('Node-Red is disabled. Please enable it in Signal K -> Server -> Plugin Config -> Node Red -> Active')
				if not red: red = txt
				else: red += '\n'+txt

		if self.grafana:
			try:
				subprocess.check_output(['systemctl', 'is-active', 'grafana-server.service']).decode(sys.stdin.encoding)
				txt = 'Grafana running'
				if not black: black = txt
				else: black += ' | '+txt
			except:
				txt = _('Grafana is not running')
				if not red: red = txt
				else: red += '\n'+txt
				
		#TODO influxbd2
		if self.influx:
			if self.platform.isSKpluginEnabled('signalk-to-influxdb'):
				txt = 'signalk-to-influxdb plugin enabled'
				if not black: black = txt
				else: black += ' | '+txt
			else:
				txt = _('signalk-to-influxdb plugin is disabled. Please enable it in Signal K -> Server -> Plugin Config -> InfluxDb writer -> Active')
				if not red: red = txt
				else: red += '\n'+txt
			try:
				subprocess.check_output(['systemctl', 'is-active', 'influxdb.service']).decode(sys.stdin.encoding)
				txt = 'Influxdb running'
				if not black: black = txt
				else: black += ' | '+txt
			except:
				txt = _('Influxdb is not running')
				if not red: red = txt
				else: red += '\n'+txt
			try:
				subprocess.check_output(['systemctl', 'is-active', 'kapacitor.service']).decode(sys.stdin.encoding)
				txt = 'Kapacitor running'
				if not black: black = txt
				else: black += ' | '+txt
			except:
				txt = _('Kapacitor is not running')
				if not red: red = txt
				else: red += '\n'+txt
			try:
				subprocess.check_output(['systemctl', 'is-active', 'chronograf.service']).decode(sys.stdin.encoding)
				txt = 'Chronograf running'
				if not black: black = txt
				else: black += ' | '+txt
			except:
				txt = _('Chronograf is not running')
				if not red: red = txt
				else: red += '\n'+txt

		return {'green': green,'black': black,'red': red}
