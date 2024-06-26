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
		self.initialMessage = _('Starting Dashboards...')

	def start(self):
		green = ''
		black = ''
		red = ''

		if os.path.isdir(self.conf.home+'/.openplotter/telegraf'):
			arr = os.listdir(self.conf.home+'/.openplotter/telegraf')
			if arr:
				subprocess.call(['pkill', '-15', 'telegraf'])
				subprocess.Popen(['telegraf','--config-directory',self.conf.home+'/.openplotter/telegraf'])
				time.sleep(1)
				black = _('Telegraf started')
		return {'green': green,'black': black,'red': red}

class Check():
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-dashboards',currentLanguage)
		self.platform = platform.Platform()
		self.nodeRed = self.platform.isSKpluginInstalled('node-red-dashboard')
		try:
			subprocess.check_output(['systemctl', 'is-enabled', 'influxdb.service']).decode(sys.stdin.encoding)
			self.influx = True
		except: self.influx = False
		try:
			subprocess.check_output(['systemctl', 'is-enabled', 'grafana-server.service']).decode(sys.stdin.encoding)
			self.grafana = True
		except: self.grafana = False

		if self.nodeRed or self.influx or self.grafana: self.initialMessage = _('Checking Dashboards...')
		else: self.initialMessage = ''

	def check(self):
		green = ''
		black = ''
		red = ''

		if self.nodeRed:
			if self.platform.isSKpluginEnabled('signalk-node-red') or not os.path.exists(self.platform.skDir+'/plugin-config-data/signalk-node-red.json'):
				txt = _('Node-Red enabled')
				if not black: black = txt
				else: black += ' | '+txt
			else:
				txt = _('Node-Red is disabled. Please enable it in Signal K -> Server -> Plugin Config -> Node Red -> Active')
				if not red: red = txt
				else: red += '\n   '+txt
		else:
			txt = _('Node-Red not enabled')
			if not black: black = txt
			else: black += ' | '+txt

		if self.grafana:
			try:
				subprocess.check_output(['systemctl', 'is-active', 'grafana-server.service']).decode(sys.stdin.encoding)
				txt = _('Grafana running')
				if not green: green = txt
				else: green += ' | '+txt
			except:
				txt = _('Grafana still not running, try later')
				if not black: black = txt
				else: black += ' | '+txt
		else:
			txt = _('Grafana not enabled')
			if not black: black = txt
			else: black += ' | '+txt

		if self.influx:
			try:
				subprocess.check_output(['systemctl', 'is-active', 'influxdb.service']).decode(sys.stdin.encoding)
				txt = _('Influxdb running')
				if not green: green = txt
				else: green += ' | '+txt
			except:
				txt = _('Influxdb still not running, try later')
				if not black: black = txt
				else: black += ' | '+txt

			if os.path.isdir(self.conf.home+'/.openplotter/telegraf'):
				arr = os.listdir(self.conf.home+'/.openplotter/telegraf')
				if arr:
					test = subprocess.check_output(['ps','aux']).decode(sys.stdin.encoding)
					if 'telegraf' in test: 
						txt = _('Telegraf running')
						if not green: green = txt
						else: green += ' | '+txt
					else:
						subprocess.Popen(['telegraf','--config-directory',self.conf.home+'/.openplotter/telegraf'])
						time.sleep(2)
						test = subprocess.check_output(['ps','aux']).decode(sys.stdin.encoding)
						if 'telegraf' in test:
							txt = _('Telegraf running')
							if not green: green = txt
							else: green += ' | '+txt
						else:
							msg = _('Telegraf not running')
							if red: red += '\n   '+msg
							else: red = msg
		else:
			txt = _('Influxdb not enabled')
			if not black: black = txt
			else: black += ' | '+txt

		return {'green': green,'black': black,'red': red}
