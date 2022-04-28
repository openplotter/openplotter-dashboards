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

import wx, os, webbrowser, subprocess, sys, time
import wx.richtext as rt

from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

#TODO influxbd2

if os.path.dirname(os.path.abspath(__file__))[0:4] == '/usr':
	from .version import version
else:
	import version

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, height):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(650, height))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-dashboards',currentLanguage)

		self.process = ['influxdb', 'kapacitor', 'chronograf', 'grafana-server']

		self.appsDict = []
		
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

		edit = ''
		install = ''
		uninstall = ''
		if self.platform.skPort:
			edit = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/plugins/signalk-to-influxdb'
			install = self.platform.admin+' python3 '+self.currentdir+'/installInfluxdb1.py'
			uninstall = self.platform.admin+' python3 '+self.currentdir+'/uninstallInfluxdb1.py'			
		app = {
		'name': 'Influxdb/Chronograf/Kapacitor',
		'show': "http://localhost:8889",
		'edit': edit,
		'included': 'no',
		'plugin': 'signalk-to-influxdb',
		'install': install,
		'uninstall': uninstall,
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
		'included': 'no',
		'plugin': '@mxtommy/kip',
		'install': self.platform.admin+' python3 '+self.currentdir+'/installKip.py',
		'uninstall': self.platform.admin+' python3 '+self.currentdir+'/uninstallKip.py',
		}
		self.appsDict.append(app)

		show = ''
		if self.platform.skPort:
			show = self.platform.http+'localhost:'+self.platform.skPort+'/@signalk/sailgauge/'
		app = {
		'name': 'Sail Gauge',
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
		self.started = False

		self.listSystemd = CheckListCtrl(self.systemd, 152)
		self.listSystemd.InsertColumn(0, _('Autostart'), width=90)
		self.listSystemd.InsertColumn(1, _('Process'), width=150)
		self.listSystemd.InsertColumn(2, _('Status'), width=150)
		self.listSystemd.InsertColumn(3, '  ', width=150)
		self.listSystemd.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSystemdSelected)
		self.listSystemd.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListSystemdDeselected)
		self.listSystemd.SetTextColour(wx.BLACK)

		self.listSystemd.OnCheckItem = self.OnCheckItem

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

		self.started = True

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
		
	def OnCheckItem(self, index, flag):
		if not self.started: return
		if flag:
			subprocess.call((self.platform.admin + ' systemctl enable ' + self.process[index]).split())
		else:
			subprocess.call((self.platform.admin + ' systemctl disable ' + self.process[index]).split())

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
			else:
				self.listApps.SetItem(item, 1, _('not installed'))
				self.listApps.SetItemBackgroundColour(item,(200,200,200))
		self.onListAppsDeselected()
		self.set_listSystemd()

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
				popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
				for line in popen.stdout:
					if not 'Warning' in line and not 'WARNING' in line:
						self.logger.WriteText(line)
						self.ShowStatusBarYELLOW(_('Installing dashboard, please wait... ')+line)
						self.logger.ShowPosition(self.logger.GetLastPosition())
				self.OnRefreshButton()
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
			popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
			for line in popen.stdout:
				if not 'Warning' in line and not 'WARNING' in line:
					self.logger.WriteText(line)
					self.ShowStatusBarYELLOW(_('Uninstalling dashboard, please wait... ')+line)
					self.logger.ShowPosition(self.logger.GetLastPosition())
			self.OnRefreshButton()
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
		webbrowser.open(apps[index]['edit'], new=2)

	def OnShowButton(self, e):
		index = self.listApps.GetFirstSelected()
		if index == -1: return
		apps = list(reversed(self.appsDict))
		webbrowser.open(apps[index]['show'], new=2)
		
################################################################################

	def pageOutput(self):
		self.logger = rt.RichTextCtrl(self.output, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		self.logger.SetMargins((10,10))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.logger, 1, wx.EXPAND, 0)
		self.output.SetSizer(sizer)

def main():
	app = wx.App()
	MyFrame().Show()
	time.sleep(1)
	app.MainLoop()

if __name__ == '__main__':
	main()
