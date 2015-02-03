import notify2
import zw_lib

notify2.init("ZipWhip")

def display_notification(msg_id, msg_from, msg_body):
  m = zw_lib.message(msg_id, msg_body, msg_from, msg_from)
  n = notify2.Notification("New Text from: %s" % msg_from,
                           msg_body,
                           "notification-message-im"   # Icon name)
  )
  #n.add_action("mark_read", "Mark As Read", m.mark_read)
  n.show()
