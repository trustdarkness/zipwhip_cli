#Boa:Frame:respond

import wx
import sys
import zw_lib
import notify2

def create(parent, mfromName, mfromNum, msg):
    return respond(parent, mfromName, mfromNum, msg)

[wxID_RESPOND, wxID_RESPONDBODY_TEXT, wxID_RESPONDFROM_TEXT, 
 wxID_RESPONDRESPONSE, wxID_RESPONDSEND, 
] = [wx.NewId() for _init_ctrls in range(5)]

class respond(wx.Frame):
    def _init_ctrls(self, prnt, mfromName, mfromNum, msg):
        self.mfromName = mfromName
        self.mfromNum = mfromNum
        self.fromMsg = msg
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_RESPOND, name=u'respond', parent=prnt,
              pos=wx.Point(480, 245), size=wx.Size(493, 267),
              style=wx.DEFAULT_FRAME_STYLE, title=u'ZipWhip Message Response')
        self.SetClientSize(wx.Size(493, 267))

        self.from_text = wx.StaticBox(id=wxID_RESPONDFROM_TEXT,
              label=u'SMS From %s (%s)' % (mfromName, mfromNum), name=u'from_text', parent=self,
              pos=wx.Point(16, 8), size=wx.Size(464, 144), style=0)

        self.body_text = wx.StaticText(id=wxID_RESPONDBODY_TEXT, label=u'%s' % msg,
              name=u'body_text', parent=self, pos=wx.Point(32, 32),
              size=wx.Size(424, 104), style=0)

        self.response = wx.TextCtrl(id=wxID_RESPONDRESPONSE, name=u'response',
              parent=self, pos=wx.Point(16, 160), size=wx.Size(368, 96),
              style=wx.TE_MULTILINE, value=u'')

        self.send = wx.Button(id=wxID_RESPONDSEND, label=u'Send', name=u'send',
              parent=self, pos=wx.Point(392, 160), size=wx.Size(88, 96),
              style=0)
        self.send.Bind(wx.EVT_BUTTON, self.sendMessage,
              id=wxID_RESPONDSEND)
              
    def sendMessage(self, event):
        print("sending message to %s: %s" % (self.mfromNum, self.response.GetValue()))
        r = zw_lib.send_message(self.mfromNum, self.response.GetValue())
        notify2.init("ZipWhip")
        n = notify2.Notification("ZipWhip", r, "notification-message-im")
        n.show()
        sys.exit(0)

    def __init__(self, parent, mfromName, mfromNum, msg):
        self._init_ctrls(parent, mfromName, mfromNum, msg)
        
