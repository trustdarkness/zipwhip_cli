#!/usr/bin/python3

from gi.repository import Gtk, GLib, GObject
from gi.repository import AppIndicator3 as appindicator
import zw_lib
import notify2
import time
import threading

def menuitem_response(w, buf):
  print(buf)

def check(buf):
  s = zw_lib.authenticate()
  zw_lib.show_recent(s, 40, False, False, True)

def newmsg(buf):
  win = EntryWindow()
  win.connect("delete-event", Gtk.main_quit)
  win.show_all()
  Gtk.main()

def markread(buf):
  s = zw_lib.authenticate()
  zw_lib.show_recent(s, 40, False, True, False)
  notify2.init("ZipWhip")
  n = notify2.Notification("ZipWhip", 
        "All messages marked read", 
        "notification-message-im")
  n.show()


class EntryWindow(Gtk.Window):

  def __init__(self):
    Gtk.Window.__init__(self, title="Zipwhip: New SMS Message")
    self.set_size_request(250, 150)
    self.set_border_width(10)
    self.set_position(Gtk.WindowPosition.CENTER)

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
  notify2.init("ZipWhip")
  n = notify2.Notification("ZipWhip", r, "notification-message-im")
  n.show()

def background_run():
  while True:
    time.sleep(100)
    zw_lib.show_recent(s, 40, False, False, True)

def app_main():
  thread = threading.Thread(target=background_run)
  thread.daemon = True
  thread.start()

if __name__ == "__main__":
  s = zw_lib.authenticate()
  ind = appindicator.Indicator.new_with_path (
                        "zipwhip-client",
                        "indicator-demo-icon-normal",
                        appindicator.IndicatorCategory.APPLICATION_STATUS,
                        "./data")
  ind.set_status (appindicator.IndicatorStatus.ACTIVE)
  ind.set_attention_icon ("indicator-messages-new")

  # create a menu
  menu = Gtk.Menu()

  # create some 
  for i in range(3):
    if i == 0:
      buf = "Check for new messages"
    elif i == 1:
      buf = "Send a new message"
    else:
      buf = "Mark all read"

    menu_items = Gtk.MenuItem(buf)
    if i == 0:
      menu_items.connect("activate", check)
    elif i == 1:
      menu_items.connect("activate", newmsg)
    elif i == 2:
      menu_items.connect("activate", markread)

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
  zw_lib.show_recent(s, 40, False, False, True)

  app_main()
  Gtk.main()

