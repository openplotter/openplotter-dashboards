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

import wx, os, webbrowser, subprocess, sys, time, re
import wx.richtext as rt

from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from openplotterSettings import selectKey

if os.path.dirname(os.path.abspath(__file__))[0:4] == '/usr':
	from .version import version
else:
	import version

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-dashboards',currentLanguage)

		self.process = ['influxdb', 'grafana-server']

		self.appsDict = []
	
		app = {
		'name': 'InfluxDB OSS 2.x',
		'show': "http://localhost:8086",
		'edit': 'editInfluxDB',
		'included': 'no',
		'plugin': '',
		'install': self.platform.admin+' python3 '+self.currentdir+'/installInfluxdb2.py',
		'uninstall': self.platform.admin+' python3 '+self.currentdir+'/uninstallInfluxdb2.py',
		}
		self.appsDict.append(app)

		app = {
		'name': 'Grafana',
		'show': "http://localhost:3001",
		'edit': '',
		'included': 'no',
		'plugin': '',
		'install': self.platform.admin+' python3 '+self.currentdir+'/installGrafana.py',
		'uninstall': self.platform.admin+' python3 '+self.currentdir+'/uninstallGrafana.py',
		}
		self.appsDict.append(app)

		show = ''
		edit = ''
		if self.platform.skPort:
			show = self.platform.http+'localhost:'+self.platform.skPort+'/plugins/signalk-node-red/redApi/ui/'
			edit = self.platform.http+'localhost:'+self.platform.skPort+'/plugins/signalk-node-red/redAdmin/'
		app = {
		'name': 'Node-Red Dashboard',
		'show': show,
		'edit': edit,
		'included': 'no',
		'plugin': 'node-red-dashboard',
		'install': self.platform.admin+' python3 '+self.currentdir+'/installNoderedDashboard.py',
		'uninstall': self.platform.admin+' python3 '+self.currentdir+'/uninstallNoderedDashboard.py',
		}
		self.appsDict.append(app)

		show = ''
		if self.platform.skPort:
			show = self.platform.http+'localhost:'+self.platform.skPort+'/@mxtommy/kip/'
		app = {
		'name': 'Kip',
		'show': show,
		'edit': '',
		'included': 'yes',
		'plugin': '',
		'install': '',
		'uninstall': '',
		}
		self.appsDict.append(app)

		show = ''
		if self.platform.skPort:
			show = self.platform.http+'localhost:'+self.platform.skPort+'/@signalk/instrumentpanel/'
		app = {
		'name': 'Instrument Panel',
		'show': show,
		'edit': '',
		'included': 'yes',
		'plugin': '',
		'install': '',
		'uninstall': '',
		}
		self.appsDict.append(app)

		show = ''
		app = {
		'name': 'SKipper app',
		'show': '/usr/local/bin/skipper/SkipperApp',
		'edit': '',
		'included': 'no',
		'plugin': '',
		'install': self.platform.admin+' python3 '+self.currentdir+'/installskipper.py',
		'uninstall': self.platform.admin+' python3 '+self.currentdir+'/uninstallskipper.py',
		}
		self.appsDict.append(app)

		if os.path.dirname(os.path.abspath(__file__))[0:4] == '/usr': 
			v = version
		else: v = version.version

		wx.Frame.__init__(self, None, title=_('Dashboards')+' '+v, size=(800,444))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/openplotter-dashboards.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)

		self.toolbar1 = wx.ToolBar(self, style=wx.TB_TEXT)
		toolHelp = self.toolbar1.AddTool(101, _('Help'), wx.Bitmap(self.currentdir+"/data/help.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolHelp, toolHelp)
		if not self.platform.isInstalled('openplotter-doc'): self.toolbar1.EnableTool(101,False)
		toolSettings = self.toolbar1.AddTool(106, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()
		self.refreshButton = self.toolbar1.AddTool(104, _('Refresh'), wx.Bitmap(self.currentdir+"/data/refresh.png"))
		self.Bind(wx.EVT_TOOL, self.OnRefreshButton, self.refreshButton)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.apps = wx.Panel(self.notebook)
		self.systemd = wx.Panel(self.notebook)		
		self.output = wx.Panel(self.notebook)
		self.notebook.AddPage(self.apps, _('Apps'))
		self.notebook.AddPage(self.systemd, _('Processes'))
		self.notebook.AddPage(self.output, '')
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/dashboard.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/process.png", wx.BITMAP_TYPE_PNG))
		img2 = self.il.Add(wx.Bitmap(self.currentdir+"/data/output.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)
		self.notebook.SetPageImage(2, img2)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.pageSystemd()
		self.pageApps()
		self.pageOutput()

		maxi = self.conf.get('GENERAL', 'maximize')
		if maxi == '1': self.Maximize()
		
		self.Centre() 

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0))

	def onTabChange(self, event):
		try:
			self.SetStatusText('')
		except:pass

	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/dashboards/dashboards_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event=0): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	################################################################################

	def pageSystemd(self):

		self.listSystemd = wx.ListCtrl(self.systemd, 152, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listSystemd.InsertColumn(0, _('Autostart'), width=90)
		self.listSystemd.InsertColumn(1, _('Process'), width=150)
		self.listSystemd.InsertColumn(2, _('Status'), width=150)
		self.listSystemd.InsertColumn(3, '  ', width=150)
		self.listSystemd.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSystemdSelected)
		self.listSystemd.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListSystemdDeselected)
		self.listSystemd.SetTextColour(wx.BLACK)
		self.listSystemd.EnableCheckBoxes(True)
		self.listSystemd.Bind(wx.EVT_LIST_ITEM_CHECKED, self.OnCheckItem)
		self.listSystemd.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.OnUnCheckItem)

		self.toolbar3 = wx.ToolBar(self.systemd, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.start = self.toolbar3.AddTool(301, _('Start'), wx.Bitmap(self.currentdir+"/data/start.png"))
		self.Bind(wx.EVT_TOOL, self.onStart, self.start)
		self.stop = self.toolbar3.AddTool(302, _('Stop'), wx.Bitmap(self.currentdir+"/data/stop.png"))
		self.Bind(wx.EVT_TOOL, self.onStop, self.stop)
		self.restart = self.toolbar3.AddTool(303, _('Restart'), wx.Bitmap(self.currentdir+"/data/restart.png"))
		self.Bind(wx.EVT_TOOL, self.onRestart, self.restart)	

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.listSystemd, 1, wx.EXPAND, 0)
		sizer.Add(self.toolbar3, 0)

		self.systemd.SetSizer(sizer)

	def onListSystemdSelected(self, e):
		i = e.GetIndex()
		valid = e and i >= 0
		if not valid: return
		self.toolbar3.EnableTool(301,True)
		self.toolbar3.EnableTool(302,True)
		self.toolbar3.EnableTool(303,True)

	def onListSystemdDeselected(self, event=0):
		self.toolbar3.EnableTool(301,False)
		self.toolbar3.EnableTool(302,False)
		self.toolbar3.EnableTool(303,False)

	def set_listSystemd(self):
		self.listSystemd.DeleteAllItems()
		for process in self.process:
			command = 'systemctl show ' + process + ' --no-page'
			output = subprocess.check_output(command.split(),universal_newlines=True)
			item = self.listSystemd.InsertItem(sys.maxsize, '')
			self.listSystemd.SetItem(item, 1, process)
			if 'ActiveState=active' in output: self.listSystemd.SetItem(item, 2, _('active'))
			else: self.listSystemd.SetItem(item, 2, _('inactive'))
			if 'SubState=running' in output: 
				self.listSystemd.SetItem(item, 3, _('running'))
				self.listSystemd.SetItemBackgroundColour(item,(0,255,0))
			else: 
				self.listSystemd.SetItem(item, 3, _('dead'))
				self.listSystemd.SetItemBackgroundColour(item,(-1,-1,-1))
			if 'UnitFileState=enabled' in output: self.listSystemd.CheckItem(item)
		self.onListSystemdDeselected()
		
	def onStart(self,e):
		index = self.listSystemd.GetFirstSelected()
		if index == -1: return
		self.ShowStatusBarYELLOW(_('Starting process...'))
		subprocess.call((self.platform.admin + ' systemctl start ' + self.process[index]).split())
		self.set_listSystemd()
		self.ShowStatusBarGREEN(_('Done'))

	def onStop(self,e):
		index = self.listSystemd.GetFirstSelected()
		if index == -1: return
		self.ShowStatusBarYELLOW(_('Stopping process...'))
		subprocess.call((self.platform.admin + ' systemctl stop ' + self.process[index]).split())
		self.set_listSystemd()
		self.ShowStatusBarGREEN(_('Done'))

	def onRestart(self,e):
		index = self.listSystemd.GetFirstSelected()
		if index == -1: return
		self.ShowStatusBarYELLOW(_('Restarting process...'))
		subprocess.call((self.platform.admin + ' systemctl restart ' + self.process[index]).split())
		self.set_listSystemd()
		self.ShowStatusBarGREEN(_('Done'))
		
	def OnCheckItem(self, index):
		if not self.started: return
		i = index.GetIndex()
		subprocess.call((self.platform.admin + ' systemctl enable ' + self.process[i]).split())

	def OnUnCheckItem(self, index):
		if not self.started: return
		i = index.GetIndex()
		subprocess.call((self.platform.admin + ' systemctl disable ' + self.process[i]).split())

	################################################################################

	def pageApps(self):
		self.listApps = wx.ListCtrl(self.apps, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
		self.listApps.InsertColumn(0, _('Name'), width=320)
		self.listApps.InsertColumn(1, _('status'), width=365)
		self.listApps.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListAppsSelected)
		self.listApps.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListAppsDeselected)
		self.listApps.SetTextColour(wx.BLACK)

		self.toolbar2 = wx.ToolBar(self.apps, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.editButton = self.toolbar2.AddTool(201, _('Edit'), wx.Bitmap(self.currentdir+"/data/edit.png"))
		self.Bind(wx.EVT_TOOL, self.OnEditButton, self.editButton)
		self.showButton = self.toolbar2.AddTool(202, _('Open'), wx.Bitmap(self.currentdir+"/data/show.png"))
		self.Bind(wx.EVT_TOOL, self.OnShowButton, self.showButton)
		self.toolbar2.AddSeparator()
		toolInstall= self.toolbar2.AddTool(203, _('Install'), wx.Bitmap(self.currentdir+"/data/install.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolInstall, toolInstall)
		toolUninstall= self.toolbar2.AddTool(205, _('Uninstall'), wx.Bitmap(self.currentdir+"/data/uninstall.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolUninstall, toolUninstall)

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.listApps, 1, wx.EXPAND, 0)
		sizer.Add(self.toolbar2, 0)
		self.apps.SetSizer(sizer)

		self.OnRefreshButton()

	def onListAppsSelected(self, e):
		self.SetStatusText('')
		i = e.GetIndex()
		valid = e and i >= 0
		if not valid: return
		self.onListAppsDeselected()
		if self.listApps.GetItemBackgroundColour(i) != (200,200,200):
			self.toolbar2.EnableTool(203,True)
			self.toolbar2.EnableTool(205,True)
			apps = list(reversed(self.appsDict))
			if apps[i]['edit']: self.toolbar2.EnableTool(201,True)
			if apps[i]['show']: self.toolbar2.EnableTool(202,True)
		else: self.toolbar2.EnableTool(203,True)

	def onListAppsDeselected(self, event=0):
		self.toolbar2.EnableTool(203,False)
		self.toolbar2.EnableTool(205,False)
		self.toolbar2.EnableTool(201,False)
		self.toolbar2.EnableTool(202,False)

	def OnRefreshButton(self, event=0):
		self.started = False
		self.listApps.DeleteAllItems()
		for i in self.appsDict:
			item = self.listApps.InsertItem(0, i['name'])

			if i['included'] == 'yes' and self.platform.skPort: self.listApps.SetItem(item, 1, _('installed'))
			elif i['plugin'] and self.platform.skPort:
				if self.platform.isSKpluginInstalled(i['plugin']): 
					self.listApps.SetItem(item, 1, _('installed'))
				else:
					self.listApps.SetItem(item, 1, _('not installed'))
					self.listApps.SetItemBackgroundColour(item,(200,200,200))
			elif not i['plugin']:
				if i['name'] == 'Grafana':
					if os.path.isfile('/usr/share/grafana/conf/defaults.ini'): self.listApps.SetItem(item, 1, _('installed'))
					else:
						self.listApps.SetItem(item, 1, _('not installed'))
						self.listApps.SetItemBackgroundColour(item,(200,200,200))
				elif i['name'] == 'InfluxDB OSS 2.x':
					if os.path.isfile('/etc/apt/sources.list.d/influxdb.list'): self.listApps.SetItem(item, 1, _('installed'))
					else:
						self.listApps.SetItem(item, 1, _('not installed'))
						self.listApps.SetItemBackgroundColour(item,(200,200,200))
				elif i['name'] == 'SKipper app':
					if os.path.isfile('/etc/apt/sources.list.d/openrepo-skipperapp.list'): self.listApps.SetItem(item, 1, _('installed'))
					else:
						self.listApps.SetItem(item, 1, _('not installed'))
						self.listApps.SetItemBackgroundColour(item,(200,200,200))
			else:
				self.listApps.SetItem(item, 1, _('not installed'))
				self.listApps.SetItemBackgroundColour(item,(200,200,200))
		self.onListAppsDeselected()
		self.set_listSystemd()
		self.started = True

	def OnToolInstall(self, e):
		index = self.listApps.GetFirstSelected()
		if index == -1: return
		apps = list(reversed(self.appsDict))
		name = apps[index]['name']
		command = apps[index]['install']
		plugin = apps[index]['plugin']
		if plugin and not self.platform.skPort: 
			self.ShowStatusBarRED(_('Please install "Signal K Installer" OpenPlotter app'))
			self.OnToolSettings()
		else: 
			if not command:
				self.ShowStatusBarRED(_('This dashboard can not be installed'))
				return
			msg = _('Are you sure you want to install ')+name+_(' and its dependencies?')
			dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
			if dlg.ShowModal() == wx.ID_YES:
				self.logger.Clear()
				self.notebook.ChangeSelection(2)
				self.ShowStatusBarYELLOW(_('Installing dashboard, please wait... '))
				popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
				for line in popen.stdout:
					if not 'Warning' in line and not 'WARNING' in line:
						self.logger.WriteText(line)
						self.logger.ShowPosition(self.logger.GetLastPosition())
						wx.GetApp().Yield()
				self.OnRefreshButton()
				self.ShowStatusBarGREEN(_('Done'))
				if plugin: self.restart_SK(0)
			dlg.Destroy()

	def OnToolUninstall(self, e):
		index = self.listApps.GetFirstSelected()
		if index == -1: return
		apps = list(reversed(self.appsDict))
		name = apps[index]['name']
		command = apps[index]['uninstall']
		plugin = apps[index]['plugin']
		if not command:
			self.ShowStatusBarRED(_('This dashboard can not be uninstalled'))
			return
		msg = _('Are you sure you want to uninstall ')+name+_(' and its dependencies?')
		dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
		if dlg.ShowModal() == wx.ID_YES:
			self.logger.Clear()
			self.notebook.ChangeSelection(2)
			self.ShowStatusBarYELLOW(_('Uninstalling dashboard, please wait... '))
			popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
			for line in popen.stdout:
				if not 'Warning' in line and not 'WARNING' in line:
					self.logger.WriteText(line)
					self.logger.ShowPosition(self.logger.GetLastPosition())
					wx.GetApp().Yield()
			self.OnRefreshButton()
			self.ShowStatusBarGREEN(_('Done'))
			if plugin: self.restart_SK(0)
		dlg.Destroy()

	def restart_SK(self, msg):
		if msg == 0: msg = _('Restarting Signal K server... ')
		seconds = 12
		for i in range(seconds, 0, -1):
			self.ShowStatusBarYELLOW(msg+str(i))
			time.sleep(1)
		self.ShowStatusBarGREEN(_('Signal K server restarted'))

	def OnEditButton(self, e):
		index = self.listApps.GetFirstSelected()
		if index == -1: return
		apps = list(reversed(self.appsDict))
		if apps[index]['edit'] == 'editInfluxDB':
			dlg = editInfluxDB()
			res = dlg.ShowModal()
			if res == wx.ID_OK:
				subprocess.call(['pkill', '-15', 'telegraf'])
				subprocess.Popen(['telegraf','--config-directory',self.conf.home+'/.openplotter/telegraf'])
				self.ShowStatusBarGREEN(_('Telegraf restarted'))
			dlg.Destroy()
		else: webbrowser.open(apps[index]['edit'], new=2)

	def OnShowButton(self, e):
		index = self.listApps.GetFirstSelected()
		if index == -1: return
		apps = list(reversed(self.appsDict))
		url = apps[index]['show']

		if url.startswith("http"):
			webbrowser.open(url, new=2)
		else:
			os.system(url)
		
	################################################################################

	def pageOutput(self):
		self.logger = rt.RichTextCtrl(self.output, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		self.logger.SetMargins((10,10))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.logger, 1, wx.EXPAND, 0)
		self.output.SetSizer(sizer)

################################################################################

class editInfluxDB(wx.Dialog):

	def __init__(self):
		self.conf = conf.Conf()
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		self.platform = platform.Platform()
		if self.conf.get('GENERAL', 'debug') == 'yes': self.debug = True
		else: self.debug = False

		wx.Dialog.__init__(self, None, title=_('Data to store in InfluxDB 2.x'), size=(750, 400))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		panel = wx.Panel(self)

		self.SK = wx.TextCtrl(panel,size=(-1, 25))
		SKedit = wx.Button(panel, label='Signal K key')
		SKedit.Bind(wx.EVT_BUTTON, self.onSKedit)

		intervalLabel= wx.StaticText(panel, label = _('Interval'))
		self.interval = wx.ComboBox(panel, choices = ['','5s','10s','15s','30s','45s','1m','5m','10m','15m','30m','45m','1h','5h','12h','24h'], style=wx.CB_READONLY,size=(-1, 25))

		orgLabel= wx.StaticText(panel, label = _('Organization'))
		self.org = wx.TextCtrl(panel,size=(-1, 25))

		bucketLabel= wx.StaticText(panel, label = 'Bucket')
		self.bucket = wx.TextCtrl(panel,size=(-1, 25))

		tokenLabel= wx.StaticText(panel, label = 'Token')
		self.token = wx.TextCtrl(panel,size=(-1, 25))

		self.listKeys = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listKeys.InsertColumn(0, _('Enabled'), width=70)
		self.listKeys.InsertColumn(1, 'Signal K key', width=350)
		self.listKeys.InsertColumn(2, _('Interval'), width=100)
		self.listKeys.InsertColumn(3, 'Bucket', width=100)
		self.listKeys.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListKeysSelected)
		self.listKeys.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListKeysDeselected)
		self.listKeys.EnableCheckBoxes(True)
		self.listKeys.Bind(wx.EVT_LIST_ITEM_CHECKED, self.OnCheckItem)
		self.listKeys.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.OnUnCheckItem)
		self.checking = False
		self.listKeys.SetTextColour(wx.BLACK)

		self.toolbar7 = wx.ToolBar(panel, style=wx.TB_VERTICAL)
		self.toolbar7.AddSeparator()
		addInput = self.toolbar7.AddTool(705, _('Add'), wx.Bitmap(self.currentdir+"/data/add.png"))
		self.Bind(wx.EVT_TOOL, self.onAddInput, addInput)
		self.toolbar7.AddSeparator()
		saveInput = self.toolbar7.AddTool(701, _('Save'), wx.Bitmap(self.currentdir+"/data/apply.png"))
		self.Bind(wx.EVT_TOOL, self.onSaveInput, saveInput)
		self.toolbar7.AddSeparator()
		deleteInput = self.toolbar7.AddTool(702, _('Delete'), wx.Bitmap(self.currentdir+"/data/cancel.png"))
		self.Bind(wx.EVT_TOOL, self.onDeleteInput, deleteInput)
		self.toolbar7.AddSeparator()

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.ok)

		h1 = wx.BoxSizer(wx.HORIZONTAL)
		h1.Add(self.SK, 1, wx.ALL | wx.EXPAND, 5)
		h1.Add(SKedit, 0, wx.ALL | wx.EXPAND, 5)
		h1.Add(intervalLabel, 0, wx.ALL | wx.EXPAND, 5)
		h1.Add(self.interval, 0, wx.ALL | wx.EXPAND, 5)

		h2 = wx.BoxSizer(wx.HORIZONTAL)
		h2.Add(orgLabel, 0, wx.ALL | wx.EXPAND, 5)
		h2.Add(self.org, 1, wx.ALL | wx.EXPAND, 5)
		h2.Add(bucketLabel, 0, wx.ALL | wx.EXPAND, 5)
		h2.Add(self.bucket , 1, wx.ALL | wx.EXPAND, 5)
		h2.Add(tokenLabel, 0, wx.ALL | wx.EXPAND, 5)
		h2.Add(self.token, 1, wx.ALL | wx.EXPAND, 5)

		v1 = wx.BoxSizer(wx.VERTICAL)
		v1.AddSpacer(5)
		v1.Add(h1, 0, wx.ALL | wx.EXPAND, 0)
		v1.Add(h2, 0, wx.ALL | wx.EXPAND, 0)
		v1.AddSpacer(5)
		v1.Add(self.listKeys, 1, wx.ALL | wx.EXPAND, 5)
		v1.AddSpacer(5)

		h3 = wx.BoxSizer(wx.HORIZONTAL)
		h3.Add(v1, 1, wx.ALL | wx.EXPAND, 0)
		h3.Add(self.toolbar7 , 0, wx.EXPAND, 0)

		actionbox = wx.BoxSizer(wx.HORIZONTAL)
		actionbox.AddStretchSpacer(1)
		actionbox.Add(cancelBtn, 0, wx.LEFT | wx.EXPAND, 10)
		actionbox.Add(okBtn, 0, wx.LEFT | wx.EXPAND, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(h3, 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(actionbox, 0, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(vbox)
		self.panel = panel

		self.Centre() 
		self.onRead()

	def onRead(self):
		try: self.inputs = eval(self.conf.get('DASHBOARDS', 'telegraf'))
		except: self.inputs = []
		self.onFill()

	def onFill(self):
		self.onListKeysDeselected()
		self.listKeys.DeleteAllItems()
		self.checking = False
		for i in self.inputs:
			index = self.listKeys.InsertItem(sys.maxsize, '')
			self.listKeys.SetItem(index, 1, i['key'])
			self.listKeys.SetItem(index, 2, i['interval'])
			self.listKeys.SetItem(index, 3, i['bucket'])
			if i['enabled']: self.listKeys.CheckItem(index)
		self.checking = True

	def onValidate(self):
		if not re.match('^[-:.0-9a-zA-Z]+$', self.SK.GetValue()):
			wx.MessageBox(_('Wrong Signal K key: characters not allowed.'), _('Info'), wx.OK | wx.ICON_INFORMATION)
			return False
		if self.interval.GetSelection() == -1 or self.interval.GetValue() == '':
			wx.MessageBox(_('Wrong Interval.'), _('Info'), wx.OK | wx.ICON_INFORMATION)
			return False
		if not self.org.GetValue():
			wx.MessageBox(_('Wrong Organization.'), _('Info'), wx.OK | wx.ICON_INFORMATION)
			return False
		if not self.bucket.GetValue():
			wx.MessageBox(_('Wrong Bucket.'), _('Info'), wx.OK | wx.ICON_INFORMATION)
			return False
		if not self.token.GetValue():
			wx.MessageBox(_('Wrong token.'), _('Info'), wx.OK | wx.ICON_INFORMATION)
			return False
		return True

	def onAddInput(self, e):
		if self.onValidate():
			self.inputs.append({'enabled':True,'key':self.SK.GetValue(),'interval':self.interval.GetValue(),'org':self.org.GetValue(),'bucket':self.bucket.GetValue(),'token':self.token.GetValue()})
			self.onFill()

	def onSaveInput(self, e):
		selected = self.listKeys.GetFirstSelected()
		if selected == -1: return
		if self.onValidate():
			items = self.SK.GetValue().split('.')
			if items[0] == 'vessels': del items[0]
			if items[0] != 'self' and items[0][0:12] != 'urn:mrn:imo:' and items[0][0:16] != 'urn:mrn:signalk:': items.insert(0, 'self')
			key = '.'.join(items)
			self.inputs[selected] = {'enabled':self.listKeys.IsItemChecked(selected),'key':key,'interval':self.interval.GetValue(),'org':self.org.GetValue(),'bucket':self.bucket.GetValue(),'token':self.token.GetValue()}
			self.onFill()

	def onDeleteInput(self, e):
		selected = self.listKeys.GetFirstSelected()
		if selected == -1: return
		self.inputs.pop(selected)
		self.onFill()

	def onListKeysSelected(self, e):
		selected = self.listKeys.GetFirstSelected()
		if selected == -1: return
		self.toolbar7.EnableTool(701,True)
		self.toolbar7.EnableTool(702,True)
		self.SK.SetValue(self.inputs[selected]['key'])
		self.interval.SetValue(self.inputs[selected]['interval'])
		self.org.SetValue(self.inputs[selected]['org'])
		self.bucket.SetValue(self.inputs[selected]['bucket'])
		self.token.SetValue(self.inputs[selected]['token'])

	def onListKeysDeselected(self, event=0):
		self.toolbar7.EnableTool(701,False)
		self.toolbar7.EnableTool(702,False)
		self.SK.SetValue('')
		self.interval.SetValue('')
		self.org.SetValue('')
		self.bucket.SetValue('')
		self.token.SetValue('')

	def OnCheckItem(self, index):
		if self.checking:
			i = index.GetIndex()
			self.inputs[i]['enabled'] = True
			self.onFill()

	def OnUnCheckItem(self, index):
		if self.checking:
			i = index.GetIndex()
			self.inputs[i]['enabled'] = False
			self.onFill()

	def onSKedit(self,e):
		dlg = selectKey.SelectKey(self.SK.GetValue(),1)
		res = dlg.ShowModal()
		if res == wx.OK:
			if ':' in dlg.selected_key:
				items = dlg.selected_key.split(':')
				key = items[0]
			else: key = dlg.selected_key
			key = dlg.selected_vessel+'.'+key
			self.SK.SetValue(key)
		dlg.Destroy()

	def ok(self,e):
		self.conf.set('DASHBOARDS', 'telegraf',str(self.inputs))
		os.system('rm -rf '+self.conf.home+'/.openplotter/telegraf')
		os.system('mkdir '+self.conf.home+'/.openplotter/telegraf')
		for i in self.inputs:
			if i['enabled']:
				url = self.platform.http+'localhost:'+self.platform.skPort
				name_override = i['key'].replace('urn:mrn:imo:','')
				name_override = name_override.replace('urn:mrn:signalk:','')
				content = '''[[inputs.http]]
  interval = "%s"
  name_override = "%s"
  urls = ["%s/signalk/v1/api/vessels/%s"]
  method = "GET"
  success_status_codes = [200]
  json_time_key = "timestamp"
  json_time_format = "RFC3339"
  tag_keys = ["$source"]
  data_format = "json"

[[outputs.influxdb_v2]]
  flush_interval = "%s"
  urls = ["http://localhost:8086"]
  token = "%s"
  organization = "%s"
  bucket = "%s"''' % (i['interval'],name_override,url,i['key'].replace('.','/'),i['interval'],i['token'],i['org'],i['bucket'])
				c = 0
				file = self.conf.home+'/.openplotter/telegraf/'+name_override+'.conf'
				while True:
					if os.path.isfile(file): 
						c = c + 1
						file = self.conf.home+'/.openplotter/telegraf/'+name_override+'_'+str(c)+'.conf'
					else: break
				fo = open(file, "w")
				fo.write(content)
				fo.close()
		self.EndModal(wx.ID_OK)

################################################################################

def main():
	app = wx.App()
	MyFrame().Show()
	time.sleep(1)
	app.MainLoop()

if __name__ == '__main__':
	main()
