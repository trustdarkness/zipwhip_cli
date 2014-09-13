#!/usr/bin/python3
import subprocess
import getpass
import pickle
import sys
import os
try:
  import WebCalls
except:
  print("Webcalls.py from the ZipWhip python API must be in your PYTHON_PATH")
  sys.exit(0)

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

home = os.path.expanduser("~")

SETTINGS_DIR = os.path.join(home, ".zwcli")
SETTINGS_FILE = os.path.join(home, ".zwcli", "settings")
zwc = WebCalls.WebCalls()

def authenticate():
  """
  Authenticate to ZipWhip and get a session key.  Offer to save user
  credentials locally (insecurely, for now).

  Returns:
    Session Key to be used in future operations.  Also optionally
    saves login information to ~/.zw/settings
  """
  autologin = False
  try:
    with open(SETTINGS_FILE, 'rb') as f: 
      u, p = pickle.load(f)
      autologin = True
  except:
    u = input("Enter zipwhip number: ")
    p = getpass.getpass("Enter password: ")
  r = zwc.user_login(u,p)
  s = r.get("response")
  if r.get("success"):
    print("You've successfully logged in.")
    if not autologin:
      print("Would you like to save this info? ")
      print("THIS IS NOT SECURE and will allow anyone with access to this")
      print("account on your computer the ability to send and recieve ")
      print("messages via your ZipWhip account")
      yn = input("Save? y/n ")
      if yn.upper() == "Y":
        subprocess.call(["mkdir", "-p", SETTINGS_DIR])
        with open(SETTINGS_FILE, 'wb') as f:
          pckl = (u, p)
          pickle.dump(pckl, f)
    return s 
  else:
    print("Bad username or password.")
    sys.exit(0)

def console_ui(s):
  """
  Basic interactive console UI for zipwhip.  Currently pretty limited.
  Ncurses UI coming.

  Args:
    s - String - session key.
  """
  print("Select one of the following options:")
  print("    1. See recent conversations")
  print("    2. Send a text")
  print(" ")
  response = input("selection: ")
  if int(response) == 1:
    cl = zwc.conversation_list(s)
    print("New? | %14s | Msg: " % "From:")
    for k,v in cl.items():
      if k == 'response':
        for i, d in enumerate(v):
          # d looks like
          # { 'class' : 'java class name'
          #   'bcc' :
          #   'lastUpdated' : (timestamp)
          #   'address' : 'ptn:/phone_number'
          #   ...
          #   'lastContactMobileNumber' : 'phone_number'
	  #   'lastContactName': 'name'
          #   'new' : True/False
          #   'lastMessageBody' : 'msg_body'
          if d.get('new'):
            star = '*'
          else:
            star = ' ' 
          lastMsg = d.get('lastMessageBody').replace('\n', ' ')
          if not d.get('lastContactFirstName') and not \
            d.get('lastContactLastName'):
            contact = d.get('lastContactMobileNumber')
          else:
            contact = "%s %s" % \
              (d.get('lastContactFirstName'), d.get('lastContactLastName'))
          multiline = False
          if len(lastMsg) > 56:
            multiline = True
            words = lastMsg.split()
            num_lines = int((len(lastMsg)/56))+2
            lines = [" "]*num_lines
            line = 0
            for word in words:
              if len(lines[line]) + len(word) < 56:
                lines[line] += "%s " % word
              else:
                line = line+1
                lines[line] += "%s " % word
          if multiline:
            line = 0
            print("%4s | %14s | %s" % (star, contact, lines[line]))
            while line < len(lines)-1:
              line = line+1
              print("%4s | %14s | %s" % (" ", " ", lines[line]))
          else:  
            print("%4s | %14s | %s" % (star, contact, lastMsg)) 
          if i > 1 and i % 19 == 0:
            yn = input("  <more> ")
  elif int(response) == 2:
    num = input("Phone Number to Text: ")
    msg = input("Message to send: ")
    print(" ")
    print("Getting ready to send")
    print(" ")
    print("     %s" % msg)
    print(" ")
    print("  to: %s" % num)
    yn = input("Confirm? y/n ")
    if yn.upper() == "Y":
      r = zwc.message_send(s, num, msg)
      if r.get("success"):
        print("Message sent successfully!")
             
if __name__ == "__main__":
  s = authenticate()
  console_ui(s) 
