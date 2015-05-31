#!/usr/bin/python3
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk, GLib, GObject
from gi.repository import AppIndicator3 as appindicator
import zw_lib
import notify2
import time
import threading
import dbus
import dbus.service

__author__ = "voytek@trustdarkness.com"
__email__ = "voytek@trustdarkness.com"
__license__ = "GPL2"

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

def menuitem_response(w, buf):
  print(buf)

def check(buf):
  print("checking new messages")
  new = zw_lib.get_recent(s, 30)
  print("got %d recent msgs" % len(new))
  #notify2.init("Zipwhip")
  
  for row in new:
    if row[1] == "*":
      num = row[3]
      date = row[2]
      msg = row[4].strip()
      n = notify2.Notification("New SMS from: %s" % num, msg, 'phone')
      n.show()

def newmsg(buf):
  win = EntryWindow()
  win.connect("delete-event", Gtk.main_quit)
  win.show_all()
  Gtk.main()

def readmsgs(buf):
  s = zw_lib.authenticate()
  recent = zw_lib.get_recent(s, 40)
  win = CellRendererTextWindow(recent)
  win.connect("delete-event", Gtk.main_quit)
  win.show_all()
  Gtk.main()

def markread(buf):
  s = zw_lib.authenticate()
  zw_lib.show_recent(s, 40, False, True, False)
  notify2.init("Zipwhip")
  n = notify2.Notification("Zipwhip", 
        "All messages marked read", 
        "phone")
  n.show()

class EntryWindow(Gtk.Window):

  def __init__(self):
    Gtk.Window.__init__(self, title="Zipwhip: New SMS Message")
    self.set_size_request(250, 150)
    self.set_border_width(10)
    self.set_position(Gtk.WindowPosition.CENTER)
    self.set_default_icon_name('phone')
    self.timeout_id = None

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    self.add(vbox)

    self.numentry = Gtk.Entry()
    self.numentry.set_text("Enter Phone Number")
    vbox.pack_start(self.numentry, True, True, 0)
 
    self.msgentry = Gtk.Entry()
    self.msgentry.set_text("Enter Message")
    vbox.pack_start(self.msgentry, True, True, 0)

    hbox = Gtk.Box(spacing=6)
    vbox.pack_start(hbox, True, True, 0)

    button = Gtk.Button("Send SMS")
    button.connect("clicked", self.on_click_me_clicked)
    hbox.pack_start(button, True, True, 0)

  def on_click_me_clicked(self, button):
    num = self.numentry.get_text()
    msg = self.msgentry.get_text()
    sendMessage(num, msg) 
    time.sleep(0.1)
    self.destroy()
        
  def quit(self):
    self.emit("destroy")

def sendMessage(num, msg):
  print("sending message to %s: %s" % (num, msg))
  r = zw_lib.send_message(num, msg)
  notify2.init("Zipwhip")
  n = notify2.Notification("Zipwhip", r, "phone")
  n.show()

class CellRendererTextWindow(Gtk.Window):

    def __init__(self, listitems):
        Gtk.ScrolledWindow.__init__(self, title="Zipwhip: Recent SMS messages")
        self.set_default_size(500, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_vexpand(True)
        liststore = Gtk.ListStore(str, str, str)
        for row in listitems:
          num = row[3]
          date = row[2]
          msg = row[4].strip()
          liststore.append([num, date, msg])

        treeview = Gtk.TreeView(model=liststore)
        treeview.set_rules_hint( True )
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("From:", renderer_text, text=0)

        treeview.append_column(column_text)
        
        renderer_date = Gtk.CellRendererText()
        column_rtext = Gtk.TreeViewColumn("Date:", renderer_date, text=1)
        treeview.append_column(column_rtext)

        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property("wrap_mode", 2)
        renderer_editabletext.set_property("wrap_width", 300)

        column_editabletext = Gtk.TreeViewColumn("SMS Message:",
            renderer_editabletext, text=2)
        treeview.append_column(column_editabletext)

        renderer_editabletext.connect("edited", self.text_edited)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(treeview)
        self.add(scrolled)

    def text_edited(self, widget, path, text):
        self.liststore[path][1] = text


class MyDBUSService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.my.test', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/my/test')

    @dbus.service.method('org.my.test')
    def hello(self):
        """returns the string 'Hello, World!'"""
        return "Hello, World!"

    @dbus.service.method('org.my.test')
    def string_echo(self, s):
        """returns whatever is passed to it"""
        return s

    @dbus.service.method('org.my.test')
    def Quit(self):
        """removes this object from the DBUS connection and exits"""
        self.remove_from_connection()
        Gtk.main_quit()
        return

def background_run():
  while True:
    time.sleep(100)
    check(None) 

def app_main():
  thread = threading.Thread(target=background_run)
  #thread2 = threading.Thread(target=dbus_loop)
  thread.daemon = True
  #thread2.daemon = True
  #thread2.start()
  thread.start()

def dbus_loop():
  DBusGMainLoop(set_as_default=True)
  myservice = MyDBUSService()
 #  DBusGMainLoop(set_as_default=True)
 # loop = GObject.MainLoop()
 # dbus_loop = dbus.mainloop.glib.DBusGMainLoop()
 # dbus.set_default_main_loop(dbus_loop)
 # loop.run()
 
if __name__ == "__main__":
  s = zw_lib.authenticate()
  ind = appindicator.Indicator.new(
                        "zipwhip-client",
                        "phone",
                        appindicator.IndicatorCategory.APPLICATION_STATUS,
                       )
  ind.set_status (appindicator.IndicatorStatus.ACTIVE)
  ind.set_attention_icon ("phone")
#  dbus_loop = dbus.mainloop.glib.DBusGMainLoop()

#  mainLoop = GObject.MainLoop()

#  dbus_system = dbus.SystemBus(mainloop=dbus_loop)
#  dbus.set_default_main_loop(dbus_loop)

  # create a menu
  menu = Gtk.Menu()

  # create some 
  for i in range(4):
    if i == 0:
      buf = "Check for new messages"
    elif i == 1:
      buf = "Send a new message"
    elif i == 2:
      buf = "Mark all read"
    elif i == 3:
      buf = "View recent messages"

    menu_items = Gtk.MenuItem(buf)
    if i == 0:
      menu_items.connect("activate", check)
    elif i == 1:
      menu_items.connect("activate", newmsg)
    elif i == 2:
      menu_items.connect("activate", markread)
    elif i == 3:
      menu_items.connect("activate", readmsgs)

    menu.append(menu_items)

    # this is where you would connect your menu item up with a function:
    
    # menu_items.connect("activate", menuitem_response, buf)

    # show the items
    menu_items.show()
  menu_items = Gtk.MenuItem(("Quit"))
  menu.append(menu_items)
  menu_items.connect("activate", Gtk.main_quit )    
  # show the item
  menu_items.show()

  ind.set_menu(menu)
  check(None)
  app_main()
  Gtk.main()

