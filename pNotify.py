import dbus
import pickle
import imaplib
import ConfigParser

class Config:

  def __init__(self):
    ini_file = "config.ini"

    config = ConfigParser.ConfigParser()
    config.readfp(open(ini_file))
    self.imap_server = config.get("IMAP", "IMAP_SERVER")
    self.imap_port   = config.get("IMAP", "IMAP_PORT")
    self.user        = config.get("IMAP", "USER")
    self.password    = config.get("IMAP", "PASSWORD")
    self.db_path     = config.get("GENERAL", "DB_PATH")

class pNotify(Config):

  def __init__(self):
    """
      Reads previously notified mails.
      If no notifications have been issued before, an empty iterator is returned
    """
    Config.__init__(self)
    try:
      db_fp   =  open(self.db_path, 'rb')
      self.db = pickle.load(db_fp)
      db_fp.close()
    except:
      # The first time, this will fail
      self.db = [{'subject':None, 'body':None}]
      pass
  
  def saveNotifications(self, messages):
    """
      Implements persistency layer for the next run.
    """
    db_fp = open(self.db_path, 'wb')
    pickle.dump(messages, db_fp)
    db_fp.close()
  
  def getPreviousNotification(self, subject, body):
    """
      Check wheter a notification has already been issued for mail
    """
    for notification in self.db:
      if notification['subject'] == subject and\
          notification['body'] == body:
        return True
    return False
  
  def main(self):
    
    knotify = dbus.SessionBus().get_object("org.kde.knotify", "/Notify")
    
    server = imaplib.IMAP4(self.imap_server, self.imap_port)
    server.login(self.user, self.password)
    server.select()
    
    typ, data = server.search(None, '(UNSEEN)')
    
    messages = []
    # Don't notify for more than 2 mails
    mail_numbers = data[0].split()
  
    # Only notify for the first two mails with details
    wrote_notification = False
    for mail_number in mail_numbers[:2]:
      # Peek at the message, but don't mark it as '\\Seen' 
      # Details in rfc3501
      t_subject = server.fetch(mail_number, '(BODY.PEEK[header.fields (subject)])')
      subject = t_subject[1][0][1]
    
      t_from = server.fetch(mail_number, '(BODY.PEEK[header.fields (from)])')
      _from = t_from[1][0][1]
  
      t_body = server.fetch(mail_number, '(UID BODY.PEEK[TEXT])')
      body_line_end = t_body[1][0][1].find('\n')
      body = t_body[1][0][1][:body_line_end]
    
      # Check if notification has already been made
      if not self.getPreviousNotification(subject, body):
        # Write from and subject as title; body as body for notification
        knotify.event("warning", "kde", [], _from+subject, body, [], [], 0, 0,\
            dbus_interface="org.kde.KNotify")
        wrote_notification = True
    
      # Make notification persistent
      messages.append({'subject':subject, 'body':body})
  
    if wrote_notification and len(mail_numbers) > 2:
      msg = "%s more new messages" % (len(mail_numbers)-2)
      knotify.event("warning", "kde", [], "pnotify info", msg, [], [], 0, 0,\
          dbus_interface="org.kde.KNotify")
  
    
    self.saveNotifications(messages)

if __name__ == "__main__":
  pNotify().main()
