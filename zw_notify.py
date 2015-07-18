import notify2
import zw_lib

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


def display_notification(msg_id, msg_from, msg_body):
  notify2.init("ZipWhip")
  m = zw_lib.message(msg_id, msg_body, msg_from, msg_from, "qt")
  n = notify2.Notification("New Text from: %s" % msg_from,
                           msg_body,
                           "notification-message-im"   # Icon name)
  )
  #n.add_action("mark_read", "Mark As Read", m.mark_read)
  n.add_action("reply", "Reply", passs)
  n.show()

def passs(buf):
  pass
