import WebCalls
import pickle
import getpass
import subprocess
import os
import zw_notify
from datetime import datetime
from dateutil import parser

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
SETTINGS_DIR = os.path.join(home, ".zwhli")
SETTINGS_FILE = os.path.join(home, ".zwhli", "settings")

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
  r = zwh.user_login(u,p)
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

def mark_read(msg_id):
  s = authenticate()
  zwh.message_read(s,msg_id)

def send_message(to, body):
  s = authenticate()
  r = zwh.message_send(s, to, body)
  if r.get("success"):
    return "Message sent successfully!"
  else:
    return "Sending failed."

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
        print("Successfully marked msg %s as read." % msg)
      else:
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
