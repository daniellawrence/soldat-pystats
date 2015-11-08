import os
import glob
import re
import string
from dateutil import parser
from datetime import datetime
import time

try:
  import cPickle as pickle
except ImportError:
  import pickle

from piestats.kill import KillObj
from piestats.player import PlayerObj


def get_kills(r, soldat_dir):
  root = os.path.join(soldat_dir, 'logs', 'kills')

  # Make sure we go by filename sorted in ascending order, as we can't sort
  # our global kill log after items are inserted.
  files = sorted(map(os.path.basename, glob.glob(os.path.join(root, '*.txt'))))

  skipped_files = 0

  for filename in files:
    key = 'pystats:logs:{filename}'.format(filename=filename)
    path = os.path.join(root, filename)
    size = os.path.getsize(path)
    prev = r.get(key)
    if prev is None:
      pos = 0
    else:
      pos = int(prev)
    if size > pos:
      print 'reading {filename} from offset {pos}'.format(filename=filename, pos=pos)
      with open(path, 'r') as h:
        h.seek(pos)
        for kill in parse_kills(h.read()):
          yield kill
      r.set(key, size)
    else:
      skipped_files += 1

  print 'skipped {count} unchanged kill logs'.format(count=skipped_files)


def update_kills(r, soldat_dir):
  for kill in get_kills(r, soldat_dir):

    # Add kill to global kill log
    r.lpush('pystats:latestkills', pickle.dumps(kill))

    # Update last seen time for this player instance
    r.zadd('pystats:playerslastseen', kill.killer.name, kill.timestamp)

    # Stuff that only makes sense for non suicides
    if not kill.suicide:
      r.zadd('pystats:playerslastseen', kill.victim.name, kill.timestamp)
      r.zincrby('pystats:playerstopkills', kill.killer.name)
      r.zincrby('pystats:playerstopdeaths', kill.victim.name)
      r.hincrby(kill.killer.data_key, 'kills', 1)

    # Increment number of deaths for victim
    r.hincrby(kill.victim.data_key, 'deaths', 1)

    # Update first/last time we saw player
    r.hsetnx(kill.killer.data_key, 'firstseen', kill.timestamp)
    r.hset(kill.killer.data_key, 'lastseen', kill.timestamp)

    # Update first/last time we saw victim, if they're not the same..
    if not kill.suicide:
      r.hsetnx(kill.victim.data_key, 'firstseen', kill.timestamp)
      r.hset(kill.victim.data_key, 'lastseen', kill.timestamp)

    # Update weapon stats..
    if kill.suicide:
      if kill.weapon != 'Selfkill':
        r.zincrby('pystats:weaponsuicides', kill.weapon)
    else:
      r.zincrby('pystats:weaponkills', kill.weapon)
      r.hincrby(kill.killer.data_key, 'kills:' + kill.weapon, 1)
      r.hincrby(kill.victim.data_key, 'deaths:' + kill.weapon, 1)

    # If we're not a suicide, update top enemy kills for player..
    if not kill.suicide:
      # Top people the killer has killed
      r.zincrby(kill.killer.top_victims_key, kill.victim.name)

      # Top people the victim has died by
      r.zincrby(kill.victim.top_enemies_key, kill.killer.name)

    # If we're not a sucide, add this legit kill to the number of kills for this
    # day
    if not kill.suicide:
      text_today = str(datetime.utcfromtimestamp(kill.timestamp).date())
      r.incr('pystats:killsperday:{day}'.format(day=text_today))


def parse_kills(contents):
    m = re.findall('\-\-\- (\d\d\-\d\d\-\d\d \d\d:\d\d:\d\d)\\n(.+)\\n(.+)\\n(Ak-74|Barrett M82A1|'
                   'Chainsaw|Cluster Grenades|Combat Knife|Desert Eagles|FN Minimi|Grenade|Hands|HK MP5|LAW|M79|Ruger '
                   '77|Selfkill|Spas-12|Stationary gun|Steyr AUG|USSOCOM|XM214 Minigun)\n', contents)
    for kill in m:
      timestamp, killer, victim, weapon = map(string.strip, kill)
      suicide = killer == victim

      unixtime = int(time.mktime(parser.parse(timestamp, parser.parserinfo(yearfirst=True)).timetuple()))
      yield KillObj(
          PlayerObj(killer),
          PlayerObj(victim),
          weapon,
          unixtime,
          suicide
      )
