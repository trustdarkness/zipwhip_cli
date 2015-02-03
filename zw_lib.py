import WebCalls
import pickle
import getpass
import os

zwh = WebCalls.WebCalls()
home = os.path.expanduser("~")
SETTINGS_DIR = os.path.join(home, ".zwcli")
SETTINGS_FILE = os.path.join(home, ".zwcli", "settings")

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
