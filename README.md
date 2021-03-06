# soldat-pystats

Statistics script which displays kill and player/country stats for multiple
[Soldat](http://soldat.pl/) game servers. Powered by Python + [Redis](http://redis.io/) + [Flask](http://flask.pocoo.org/) and styled with [Bootswatch](http://bootswatch.com/).

# Screenshots

 - [Home Page](http://jrgp.us/screenshots/soldat-pystats1.png)
 - [Players list](http://jrgp.us/screenshots/soldat-pystats2.png)
 - [Player profile](http://jrgp.us/screenshots/soldat-pystats3.png)

# Features

 - ip2country for all players. Country stats + flags next to each player
 - Supports multiple Soldat servers
 - Configurable data retention. Don't show kill stats more than X days old.
 - Ability to connect to Soldat server's admin port and provide current status
 - Player search
 - Pretty graphs
 - Clean comfortable layout provided by Bootswatch
 - Uses Redis key value database instead of SQL so pages are fast even with
   hundreds of thousands of recorded kills.

# Requirements

- Python 2.7, with virtualenv/pip tools
- Redis DB installed/running
- Tested on Ubuntu/Debian. Will work on CentOS if you get at least Python 2.7

# Instructions

First, have an install of Redis database runnning. The following will do.

    sudo apt-get install redis-server

Install python virtualenv tool

    sudo apt-get install python-virtualenv

Create & activate venv (run this before next commands):

    virtualenv env
    source env/bin/activate

To install to your venv but point to your code so you can edit and dev and run:

    python setup.py develop

Copy config.yml.samp to config.yml after editing it to fit your setup

Run update script. Probably add this to cron.

    runupdate -c config.yml

Start website. (Bind to all NICs on port 5000)

    runsite -c config.yml

It is also possible to run this under apache/nginx with uwsgi. I'll include a
guide for that maybe later.

# Contact
 - Joe Gillotti - <joe@u13.net>
 - [GitHub](https://github.com/jrgp/soldat-pystats)
