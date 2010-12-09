About
-----

pNotify is a small Python script to monitor your IMAP inbox.

When new mail arrives, it will notify you via the KDE notification daemon
[KNotify](http://api.kde.org/4.x-api/kdebase-runtime-apidocs/knotify/html/index.html)
with the authors, the subjects and the first message body lines. If there are
more than two new messages in your inbox, pNotify will tell you how many more
have arrived.

Screenshot: http://dispatched.ch/pic/pnotify_screenshot.png

Usage
-----
 * Configure config.ini - this will be straight forward. Put your IMAP credentials inside.
 * You are good to go. Run with "python pNotify.py"
 * Prefereably set up a cronjob for regular monitoring

Example conjob configuration to run pNotify every five minutes:

    $ crontab -e
    */5 * * * * python [path]/pNotify.py

Dependencies
------------

 * KNotify

Licence
-------
BSD - for more info see LICENCE
