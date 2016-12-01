import os
import commands

_current_dir = os.path.split(__file__)[0]
DB_DIR = os.path.expanduser('~/edb2') #XXX windows incompatible
DEBUG = True
LOGFILE_DIR = os.path.expanduser('~/edb_log') #XXX windows incompatible

# #ifndef VERSION_SPIDER
#_hostname = commands.getoutput('hostname') #XXX windows incompatible
#if _hostname == 'diesel':
#    DB_DIR = '/home/uzak/backup/earnings/home/uzak/edb' #XXX???
# #endif

COOKIE_FILE = os.path.join(_current_dir, 'cookies.txt')
