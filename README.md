zipwhip_cli
===========

This is a command line interface to the ZipWhip cloud texting service.

A short backstory:  I hate typing on my phone.  Thus, when Google Voice
came out, I was happy to have an alternative to text via my computer.
Later, I became a privacy nut and pulled my data out of Google's services
but I found I really missed the functionality of Google Voice for texting.

ZipWhip doesn't have all of that functionality, but it has some of it, and
though there is no privacy inherint in ZipWhip's service, I don't need 
to lock into a whole ecosystem to use it like I do Google Voice. 

Though I give kudos to ZipWhip for making a linux client, they 
unfortunately made it only for Ubuntu and did not release the source.
I used the web interface on Fedora for some time, but grew tired of having
to use up an extra tab just for that.  Thankfully, the folks at ZipWhip
have a great API.

So, I threw together this very basic command line interface.  It currently
has ZERO bells and whistles.  It will allow you to view the last message
in every conversation in your texting "inbox" and it will allow you to send
text messages via a phone number.

Usage is pretty simple:

    usage: zwcli.py [-h] [-c] [-r READ] [-s] [-t TO] [-m MSG] [-u USER]
                [-p PASSWORD]

    optional arguments:
      -h, --help            show this help message and exit
      -c, --cron            Run in 'cron' mode, or non-interactively... meant for   
                            cron jobs or watch processes. Defaults to 'read' mode,
                            reading recent texts to standard out. Can be combined
                            with -s for send or -r for read,
      -r READ, --read READ  Read the last X text messages to std out. Can be run
                            like ./zwcli.py -r20 to read only the last 20
                            messages, defaults to 10
      -s, --send            Run in send mode. Must be combined with -t and -m (but
                            may be also be combined with -u and -p to specify a
                            user and password, for use with cron, etc.
      -t TO, --to TO        Number to send a message to, must be combined with -s
                            and -t Currently must be a phone number, a named
                            contacts will not work.
      -m MSG, --msg MSG     Message to send. Must be combined with -s and -t.
                            Length is limited by either zipwhip or your carrier.
                            Nothing is guaranteed. enclose your message in quotes
                            for best results, like: ./zwcli.py -s -t5555555555
                            -m'LOL ROFLMAOBBQ!!!'
      -u USER, --user USER  Username / Phonenumber to send from. Currently must be
                            a 10 digit phone number that is already setup on
                            zipwhip in the form 5555555555. If you don't supply a
                            username, we will try to use a previously saved one or
                            prompt you on the console.
      -p PASSWORD, --password PASSWORD
                            Password for zipwhip account to send from. Beware bash
                            history! If you don't supply a password, we will try
                            to use a previously saved one or prompt you on the
                            console.    


Examples:
=========

    $ ./zwcli.py
    Enter zipwhip number: 3125555555
    Enter password: 
    Would you like to save this info? 
    THIS IS NOT SECURE and will allow anyone with access to this
    account on your computer the ability to send and recieve 
    messages via your ZipWhip account
    Save? y/n y
    Select one of the following options:
        1. See recent conversations
        2. Send a text
 
    selection: 1
    New? | From:      | Msg: 
         | 651XXXXXXX | Not 4 hours big dude! Maybe 20 min with a real connection.
         | 312XXXXXXX | testing 
         | 773XXXXXXX | again.
         | 312XXXXXXX | Sure
         | 630XXXXXXX | no problem... we'll talk soon.
         | 773XXXXXXX | -=call=-  Outgoing Phone Call Duration: 60 seconds
         | 630XXXXXXX | -=call=-  Outgoing Phone Call Duration: 14 seconds
         | 805XXXXXXX | -=call=-  Outgoing Phone Call Duration: 20 seconds
         | 630XXXXXXX | -=call=-  Missed Phone Call
         | 630XXXXXXX | Thanks
         | 773XXXXXXX |  sorry for the delayed response... didn't see your message 
         |            |  right away
         |            |  
         |            |  
         |      20000 |  .signup verify 9309 Zipwhip installation complete! To 
         |            |  send, receive, and view all your texts complete 
         |            |  registration from your computer at zipwhip.com 
         |            |  
         |        456 |  Free T-Mobile Msg: $60.00 has been added to your account. 
         |            |  Your new balance is $61.00. Thanks for refilling! 
         |            |  
         | 952XXXXXXX |  i think we'll have a better idea about january
         | 708XXXXXXX | Nooo
         | 773XXXXXXX | Another test
         | 7084850010 | -=call=-  Incoming Phone Call Duration: 29 seconds
      <more> 



+++ snip +++

    $ ./zwcli.py
    You've successfully logged in.
    Select one of the following options:
        1. See recent conversations
        2. Send a text
 
    selection: 2
    Phone Number to Text: 773XXXXXXX
    Message to send: I hate white rabbits!
 
    Getting ready to send
 
         I hate white rabbits!
 
      to: 773XXXXXXX
    Confirm? y/n y
    Message sent successfully!


TODOS:
======

I'm open to feature requests, but the next things *I* would at least like to
work on implementing:

- ncurses ui (similar to mcabber)
- encryption using socialist millionaire

If you've stumbled across this and use it, please let me know!
