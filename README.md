# imapsync API


[imapsync](https://imapsync.lamiral.info/) is a tool for syncing mailboxes. It syncs all the emails from email1 to email2. 


## What?

This is a restAPI wrapper for imapsync. As always, it is very simple. 

## Why?

We didn't want to use imapsync as a command-line tool, so I ended up putting this API together. First you add a configuration, giving the SMTP, email, password etc then you run the sync jobs calling a specific config, multiple configs or all of them together. 

## How to start

Staring the application is simple:

    docker compose up -d

And once everything is up and running you can access the application as

    http://YOUR_DOCKER_HOST_IP/applications/web


## How to use:

You will need to add the configs using the "Add Label" menu. I should have called them configs but initially they were just labels containing configuration... 

Once you have a label you can then go to Run Labels and select whatever way you want to run them. There aren't many options anyway. You'll figure it out. 

## TODO 
* Tidy up the naming
* Drop tooljet if I can figure out how to deal with FE. 