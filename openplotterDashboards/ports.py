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

import os, sys, subprocess
from openplotterSettings import language
from openplotterSettings import platform

class Ports:
	def __init__(self,conf,currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-dashboards',currentLanguage)
		self.platform = platform.Platform()
		self.connections = []
		
	#TODO influxbd2
	def usedPorts(self):
		try:
			subprocess.check_output(['systemctl', 'is-active', 'chronograf.service']).decode(sys.stdin.encoding)
			self.connections.append({'id':'chronograf', 'description':'Chronograf', 'data':'', 'direction':'3', 'type':'TCP', 'mode':'server', 'address':'localhost', 'port':'8889', 'editable':'0'})
		except:pass
		try:
			subprocess.check_output(['systemctl', 'is-active', 'grafana-server.service']).decode(sys.stdin.encoding)
			self.connections.append({'id':'grafana', 'description':'Grafana', 'data':'', 'direction':'3', 'type':'TCP', 'mode':'server', 'address':'localhost', 'port':'3001', 'editable':'0'})
		except:pass
		try:
			subprocess.check_output(['systemctl', 'is-active', 'influxdb.service']).decode(sys.stdin.encoding)
			self.connections.append({'id':'influxdb1', 'description':'Influxdb HTTP', 'data':'', 'direction':'3', 'type':'TCP', 'mode':'server', 'address':'localhost', 'port':'8086', 'editable':'0'})
			self.connections.append({'id':'influxdb2', 'description':'Influxdb RPC', 'data':'', 'direction':'3', 'type':'TCP', 'mode':'server', 'address':'localhost', 'port':'8088', 'editable':'0'})
		except:pass
		try:
			subprocess.check_output(['systemctl', 'is-active', 'kapacitor.service']).decode(sys.stdin.encoding)
			self.connections.append({'id':'kapacitor', 'description':'Kapacitor', 'data':'', 'direction':'3', 'type':'TCP', 'mode':'server', 'address':'localhost', 'port':'9092', 'editable':'0'})
		except:pass
		return self.connections
