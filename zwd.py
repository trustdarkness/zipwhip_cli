import wx
import daemon

class SysTray(wx.TaskBarIcon):  
  def __init__(self, parent, icon, text):  
    wx.TaskBarIcon.__init__(self)  
    self.parentApp = parent  
    self.SetIcon(icon, text)  
    self.CreateMenu()  

  def CreateMenu(self):  
    self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.ShowMenu)  
    self.menu=wx.Menu()  
    self.menu.Append(wx.ID_OPEN, "Show")  
    self.menu.Append(wx.ID_EXIT, "Close")  

  def ShowMenu(self,event):  
    self.PopupMenu(self.menu) 

class zwDaemon
