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

def check(buf, num=30):
  """
  Get the first X new messages.  Defaults to 30.
 
  Args:
    buf - buffer passed from the menu object
    num - number of messages to get
  """
  print("checking new messages")
  new = zw_lib.get_recent(s, num)
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
  """
  Create a window to send a new message.
 
  Args:
    buf - buffer passed from the menu object
  """
  win = EntryWindow()
  win.connect("delete-event", Gtk.main_quit)
  win.show_all()
  Gtk.main()

def readmsgs(buf, num=30):
  """
  View recent messages in a list window.

  Args:
    buf - buffer passed from the menu object
    num - number of messages to get
  """
  s = zw_lib.authenticate()
  recent = zw_lib.get_recent(s, num)
  win = CellRendererTextWindow(recent)
  win.connect("delete-event", Gtk.main_quit)
  win.show_all()
  Gtk.main()

def markread(buf, num=30):
  """
  Mark recent messages read.

  Args:
    buf - buffer passed from the menu object
    num - number of messages to get
  """
  s = zw_lib.authenticate()
  zw_lib.show_recent(s, num, False, True, False)
  notify2.init("Zipwhip")
  n = notify2.Notification("Zipwhip", 
        "All messages marked read", 
        "phone")
  n.show()

def sendMessage(num, msg):
  """
  Send a message and notify the user of success.

  Args:
    num - number to send message to
    msg - message to send
  """
  print("sending message to %s: %s" % (num, msg))
  r = zw_lib.send_message(num, msg)
  notify2.init("Zipwhip")
  n = notify2.Notification("Zipwhip", r, "phone")
  n.show()


class EntryWindow(Gtk.Window):
  """Window to send a message."""

  def __init__(self):
    """ 
    Initialize class.
    """
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
    """
    Method to handle click event on Send SMS button.
 
    Args:
      button - the button 
    """
    num = self.numentry.get_text()
    msg = self.msgentry.get_text()
    sendMessage(num, msg) 
    time.sleep(0.1)
    self.destroy()
        

class CellRendererTextWindow(Gtk.Window):
  """List window for recent messages"""

  def __init__(self, listitems):
    """initialization method

    Args:
      listitmes - the things to list in the window.
    """
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
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled.add(treeview)
    self.add(scrolled)


def background_run(refresh_interval=100):
  """
  Loop to run in the thread to check for new messages regularly.

  Args:
    refresh_interval - interval in seconds to refresh -- default to 100
  """
  while True:
    time.sleep(refresh_interval)
    check(None) 

def app_main():
  """
  Main loop for background threads.
  """
  thread = threading.Thread(target=background_run)
  thread.daemon = True
  thread.start()

if __name__ == "__main__":
  s = zw_lib.authenticate()
  ind = appindicator.Indicator.new(
                        "zipwhip-client",
                        "phone",
                        appindicator.IndicatorCategory.APPLICATION_STATUS,
                       )
  ind.set_status (appindicator.IndicatorStatus.ACTIVE)
  ind.set_attention_icon ("phone")
  menu = Gtk.Menu()

  # create some 
  # TODO (voytek): de-uglify this -- here's to following tutorials!
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

