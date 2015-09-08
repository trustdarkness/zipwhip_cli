import pickle
import getpass
import subprocess
import keyring
import os
import sys
import zw_notify
from datetime import datetime
from dateutil import parser

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
debug = 1

try:
  import WebCalls
except:
  print("Webcalls.py from the ZipWhip python API must be in your PYTHON_PATH")
  sys.exit(0)

try:
  import pytz # $ pip install pytz
  from tzlocal import get_localzone # $ pip install tzlocal
except:
  print("pytz and tzlocal are required.  sudo easy_install3 pytz tzlocal")
  sys.exit(0)
      
# get local timezone    
local_tz = get_localzone()


zwh = WebCalls.WebCalls()
home = os.path.expanduser("~")
SETTINGS_DIR = os.path.join(home, ".zwcli")
SETTINGS_FILE = os.path.join(home, ".zwcli", "settings")
CONTACTS_FILE = os.path.join(SETTINGS_DIR, "contacts")

def get_handle():
  return zwh

def authenticate(username=None, password=None, auto=True):
  """
  Authenticate to ZipWhip and get a session key.  Offer to save user
  credentials locally (insecurely, for now).

  Returns:
    Session Key to be used in future operations.  Also optionally
    saves login information to ~/.zw/settings
  """
  if username and password:
    u = username
    p = password
  else:
    try:
      with open(SETTINGS_FILE, 'rb') as f: 
        # p is here for historical reasons only, we store the password in the
        # system keychain now.
        u, p = pickle.load(f)
        p = keyring.get_password("Zipwhip", u)
        autologin = True
    except:
      u = input("Enter zipwhip number: ")
      p = getpass.getpass("Enter password: ")
  r = zwh.user_login(u,p)
  s = r.get("response")
  if r.get("success"):
    if not auto:
      print("You've successfully logged in.")
      print("Would you like to save this info? ")
      yn = input("Save? y/n ")
      if yn.upper() == "Y":
        success = keyring.set_password("Zipwhip", u, p)   
        # TODO (voytek): make this more pythonic)
        subprocess.call(["mkdir", "-p", SETTINGS_DIR])
        with open(SETTINGS_FILE, 'wb') as f:
          p = "passwordstoredinsystemkeychain"
          pckl = (u, p)
          pickle.dump(pckl, f)
    else:
      success = keyring.set_password("Zipwhip", u, p)
      # TODO (voytek): make this more pythonic)
      subprocess.call(["mkdir", "-p", SETTINGS_DIR])
      with open(SETTINGS_FILE, 'wb') as f:
        p = "passwordstoredinsystemkeychain"
        pckl = (u, p)
        pickle.dump(pckl, f)

    try:
      with open(CONTACTS_FILE, 'rb') as f:
        c = pickle.load(f)
    except:
      with open(CONTACTS_FILE, 'wb') as f:
        c = {}
        pickle.dump(c, f)

        
    return s 
  else:
    print("Bad username or password.")
    sys.exit(0)

def mark_read(msg_id):
  s = authenticate()
  zwh.message_read(s,msg_id)
 
def delete(msg_id):
  s = authenticate()
  zwh.message_delete(s,msg_id)

def send_message(to, body):
  s = authenticate()
  if (len(to) != 10 and len(to) != 11): # TODO: make this less hackish
    c = get_contacts()
    to = c[to]
  if debug:
    print("sending message to %s" % to)
  r = zwh.message_send(s, to, body)
  if r.get("success"):
    return 1
  else:
    return "Sending failed."

def get_contacts():
  with open(CONTACTS_FILE, "rb") as f:
    return pickle.load(f)
 
def save_contacts(contacts):
  with open(CONTACTS_FILE, "wb") as f:
    pickle.dump(contacts, f)

def get_recent(s, num="all"):
  """Get recent text messages and display them to the console.  

  Args:
    s - String - session key
    num - int - number of recent messages to show.  If not specified, we'll 
      show them all.
    interactive - boolean - if True, we'll break the screen every so often
      for console reading.
  """
  cl = zwh.message_list(s)
  unread_ids = []
  msgs = []
  it = 30
  if num == 'all':
    num = 100000000
  c = get_contacts()
  while cl['total'] and it <= num:
    if debug:
      print("success: %s total: %s size: %s start: %d" % \
        (cl['success'], cl['total'], cl['size'], it))
    for k,v in cl.items():
      if k == 'total':
        total = v
      elif k == 'response':
        for i, d in enumerate(v):
          if num != "all" and i > num:
            break
          dt = parser.parse(d.get('dateCreated'))
          dt = dt.replace(tzinfo=pytz.timezone('US/Pacific'))
          now = datetime.now()
          now = now.replace(tzinfo=local_tz)
          ourTd = now - dt
          if ourTd.days:
            tstr = dt.astimezone(local_tz).strftime("%a %b %-d %Y %X")
            tstr = tstr[:-3]
          else:
            tstr = dt.astimezone(local_tz).strftime("%c")
            tstr = tstr[:-3]

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
          #print(dir(zwh))
          #print(help(zwh.message_read))
          #sys.exit(0)      
          if not d.get('isRead'):
            star = '*'
            unread_ids.append(d.get('id'))
          else:
            star = ' ' 
          lastMsg = d.get('body').replace('\n', ' ')
          firstname = d.get('firstName')
          lastname = d.get('lastName')
          name = firstname+" "+lastname
          if not d.get('fromName'):  # and not \
            # d.get('lastContactLastName'):
            contact = d.get('mobileNumber')
          else:
            contact = "%s" % \
              d.get('fromName') #, d.get('lastContactLastName'))
          multiline = False
          if name.strip():
            c[name] = contact

          #print("%4s | %10s | %14s | %s" % (star, tstr, contact, lines[line]))
          msgs.append([d.get('id'),star,tstr,contact,lastMsg, name])
    cl = zwh.message_list(s, start=it)
    it = it + total

  if debug:
    print("calling with start=%s total=%s" % (it, total))
    print("saving new contact list: %s" % c)
  save_contacts(c)
  print("returning from get_recent")
  return msgs

def show_recent(s, num="all", interactive=False, mark_read=False, gui=False):
  """Get recent text messages and display them to the console.  

  Args:
    s - String - session key
    num - int - number of recent messages to show.  If not specified, we'll 
      show them all.
    interactive - boolean - if True, we'll break the screen every so often
      for console reading.
  """
  cl = zwh.message_list(s)
  print("New? | %10s | %14s | Last Msg: " % ("Time:", "Conv With:"))
  unread_ids = []
  for k,v in cl.items():
    if k == 'response':
      for i, d in enumerate(v):
        if num != "all" and i > num:
          break
        dt = parser.parse(d.get('dateCreated'))
        dt = dt.replace(tzinfo=pytz.timezone('US/Pacific'))
        now = datetime.now()
        now = now.replace(tzinfo=local_tz)
        ourTd = now - dt
        if ourTd.days:
          tstr = dt.astimezone(local_tz).strftime("%a %X")
          tstr = tstr[:-3]
        else:
          tstr = dt.astimezone(local_tz).strftime("%X")
          tstr = tstr[:-3]

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
        #print(dir(zwh))
        #print(help(zwh.message_read))
        #sys.exit(0)        
        if not d.get('isRead'):
          star = '*'
          unread_ids.append(d.get('id'))
        else:
          star = ' ' 
        lastMsg = d.get('body').replace('\n', ' ')
        if not d.get('fromName'):  # and not \
          # d.get('lastContactLastName'):
          contact = d.get('mobileNumber')
        else:
          contact = "%s" % \
            d.get('fromName') #, d.get('lastContactLastName'))
        multiline = False
        if len(lastMsg) > 43:
          multiline = True
          words = lastMsg.split()
          num_lines = int((len(lastMsg)/43))+2
          lines = [" "]*num_lines
          line = 0
          for word in words:
            if len(lines[line]) + len(word) < 43:
              lines[line] += "%s " % word
            else:
              line = line+1
              lines[line] += "%s " % word
        if multiline:
          line = 0
          print("%4s | %10s | %14s | %s" % (star, tstr, contact, lines[line]))
          if gui:
            if star == '*':
              zw_notify.display_notification(d.get('id'), contact, "\n".join(lines))
          while line < len(lines)-1:
            line = line+1
            print("%4s | %10s | %14s | %s" % (" ", " ",  " ", lines[line]))
        else: 
          if gui:
            if star == '*':
              zw_notify.display_notification(d.get('id'), contact, lastMsg) 
          print("%4s | %10s | %14s | %s" % (star, tstr, contact, lastMsg)) 
       
        if interactive:
          if i > 1 and i % 19 == 0:
            yn = input("  <more> ")
  
  if mark_read:
    for msg in unread_ids:
      r = zwh.message_read(s,msg)
      if r.get("success"):
        if debug:
          print("Successfully marked msg %s as read." % msg)
      else:
        if debug:
          print(r,msg)



class message:
  def __init__(self, mid, mbody, mfromNum, mts, mfromName=None):
    self.mid = mid
    self.mbody = mbody
    self.mfromNum = mfromNum
    self.mts = mts
    self.mfromName = mfromNum

  def mark_read(self):
    s = authenticate()
    zwh.message_read(s, self.mid)
