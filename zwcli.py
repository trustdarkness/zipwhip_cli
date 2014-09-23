#!/usr/bin/python3
import subprocess
import argparse
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
    show_recent(s, interactive=True)
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

def show_recent(s, num="all", interactive=False, mark_read=False):
  """Get recent text messages and display them to the console.  

  Args:
    s - String - session key
    num - int - number of recent messages to show.  If not specified, we'll 
      show them all.
    interactive - boolean - if True, we'll break the screen every so often
      for console reading.
  """
  cl = zwc.conversation_list(s)
  print("New? | %14s | Last Msg: " % "Conv With:")
  unread_ids = []
  for k,v in cl.items():
    if k == 'response':
      for i, d in enumerate(v):
        if num != "all" and i > num:
          break
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
        #print(d)
        #print(dir(zwc))
        #print(help(zwc.message_read))
        #sys.exit(0)        
        if d.get('unreadCount') > 0:
          star = '*'
          unread_ids.append(d.get('fingerprint'))
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
       
        if interactive:
          if i > 1 and i % 19 == 0:
            yn = input("  <more> ")
  
  if mark_read:
    for msg in unread_ids:
      r = zwc.message_read(s, msg)
      if r.get("success"):
        print("Successfully marked msg %s as read." % msg)
      else:
        print(r,msg)

           
if __name__ == "__main__":
  p = argparse.ArgumentParser()
  p.add_argument("-c", "--cron", action="store_true",
   help=" ".join([
      "Run in 'cron' mode, or non-interactively... meant for cron jobs",
      "or watch processes.  Defaults to 'read' mode, reading recent texts",
      "to standard out.  Can be combined with -s for send or -r for read,"]))
  p.add_argument("-r", "--read", action="store", type=int, default=10,
    dest="read", help=" ".join([
      "Read the last X text messages to std out. Can be run like",
      "./zwcli.py -r20 to read only the last 20 messages, defaults to 10"]))
  p.add_argument("-s", "--send", action="store_true",
    dest="send", help=" ".join([
      "Run in send mode.  Must be combined with -t and -m (but may be",
      "also be combined with -u and -p to specify a user and password,",
      "for use with cron, etc."]))
  p.add_argument("-t", "--to", action="store", default=None,
    dest="to", help=" ".join([
      "Number to send a message to, must be combined with -s and -t",
      "Currently must be a phone number, a named contacts will not work."]))
  p.add_argument("-m", "--msg", action="store", default=None,
    dest="msg", help="\n".join([
      "Message to send.  Must be combined with -s and -t.  Length is",
      "limited by either zipwhip or your carrier.  Nothing is guaranteed.",
      "enclose your message in quotes for best results, like:",
      " ",
      "./zwcli.py -s -t5555555555 -m'LOL ROFLMAOBBQ!!!' "]))
  p.add_argument("-u", "--user", action="store", default=None,
    dest="user", help=" ".join([
      "Username / Phonenumber to send from.  Currently must be a 10 digit",
      "phone number that is already setup on zipwhip in the form 5555555555.",
      "If you don't supply a username, we will try to use a previously",
      "saved one or prompt you on the console."]))
  p.add_argument("-p", "--password", action="store", default=None,
    dest="password", help=" ".join([ 
      "Password for zipwhip account to send from.  Beware bash history!",
      "If you don't supply a password, we will try to use a previously",
      "saved one or prompt you on the console."]))
  p.add_argument("-R", "--markread", action="store_true", 
    dest="mark_read", help="Mark all messages as read.  Must be used with -r.") 

  args = p.parse_args()
  if args.user and args.password:
    r = zwc.user_login(args.user,args.password)
    s = r.get("response")
    if r.get("success"):
      print("You've successfully logged in.")
  elif args.user or args.password:
    print("-u and -p must always go together")
    sys.exit(0)
  else:
    s = authenticate()
  if args.cron and args.send:
    if not args.to or not args.msg:
      print("-s must be combined with -t and -m at a minimum")
      sys.exit(0)
    else:
      r = zwc.message_send(s, args.to, args.msg)
      if r.get("success"):
        print("Message sent successfully!")
  elif args.send:
    if not args.to or not args.msg:
      print("-s must be combined with -t and -m at a minimum")
      sys.exit(0)
    else:
      r = zwc.message_send(s, args.to, args.msg)
      if r.get("success"):
        print("Message sent successfully!")
  elif args.to and args.msg:
    r = zwc.message_send(s, args.to, args.msg)
    if r.get("success"):
      print("Message sent successfully!")
  elif args.to or args.msg:
    print("-t and -m must always go together")

  elif args.cron:
    show_recent(s, args.read, mark_read=args.mark_read) 
  else:
    console_ui(s) 
