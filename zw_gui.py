#!/usr/bin/python3
import wx
import zw_respond
import sys

class zwApp(wx.App):

    def OnInit(self):
      return True
 
    def create_window(self):
        self.main = zw_respond.create(None, self.mfromName, self.mfromNum, self.msg)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

    def add_from_name(self, mfromName):
      self.mfromName = mfromName

    def add_from_num(self, mfromNum):
      self.mfromNum = mfromNum

    def add_msg(self, msg):
      self.msg = msg
    
def main(mfromName, mfromNum, msg):
    application = zwApp(0)
    application.add_from_name(mfromName)
    application.add_from_num(mfromNum)
    application.add_msg(msg)
    application.create_window()
    application.MainLoop()
    
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
