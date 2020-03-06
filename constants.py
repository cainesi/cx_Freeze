import datetime, os

DEBUG = True

##
#
# Version information, to be updated for each release.
#
##

#version number must be of the form #.#.#.#
#XX version = u"%1%.%2%.%3%" & 0 & 16 & 0
version = u"0.16.0"

#XX revision = %1% & 128
revision = 128

upgrade_code = "{ac3218cf-6351-4f4a-b686-5866e5de74c2}"  # upgrade code to uniquely identify msi installers for this program

#XX release_date = datetime.date(year=%y%, month=%m%, day = %d%)
release_date = datetime.date(year=2020, month=1, day = 17)

#key_date = release_date + datetime.timedelta(days=365)  # date at which this version will expire (regardless of keys)

release_date_string = release_date.strftime(u"%B") + " " + str(release_date.day) + ", " + str(release_date.year)

##
#
# System information constants / file locations
#
##

HOME_DIR = os.path.expanduser(u"~")
SETTINGS_FILE = os.path.join(HOME_DIR,"bline.settings")
HISTORY_DB_FILE = os.path.join(HOME_DIR, "bline.historyDB")

##
#
# Program setting behaviours
#
##

DEFAULT_COPY_PT_SIZE = 10
AUTHOR_EMAIL = "ian.caines@gmail.com"
DROP_DUMMY = "anti_self_drop_dummy_data"  # dummy data used to detect self-drops
MAX_DATABASE_SIZE = 10000

##
#
# Operational controls
#
##

ADVANCED_HELP = True  # whether to use the advanced help interface in window_help

##
#
# Debug output control constants
#
##

VERBOSE_STARTUP = False  # whether to print information during program startup in blineapp.py
VERBOSE_INTERFACE = False  # whether main interface is verbose
VERBOSE_HTML = False  # determines whether HTMLFixer module is verbose
VERBOSE_BLACKLINE_ENGINE = False  # is blacklineEngine.py verbose
VERBOSE_COORDINATOR = False  # is the pasteCoordinator verbose
VERBOSE_TEXTLINKER = False  # is textLinker verbose
VERBOSE_DROPWIDGET = False  # is DropWidget verbose (also stops cursor flash, and generates additional output whenever re-paint called)
VERBOSE_BLINETEXTEDIT = False  # is BLineTextEdit verbose
VERBOSE_TEXT_CHANGE = False  # if a report should be generate on each text change.
VERBOSE_HELP = False  # if help display should show verbose help
VERBOSE_FORMAT = False  # if verbose information should be printed about text formats
VERBOSE_PRINT = False  # if verbose information should be printed by printing module (in particular, when printing out text format properties)
VERBOSE_TEXT_UTIL = False  # should the util_text module output verbose information
VERBOSE_DB = False  # verbose information about history database access
VERBOSE_DB_DRAW = False  # verbose information about drawing history-database related widgets


##
#
# Graphics constants
#
##

# CORNER_ROUNDING_LENGTH = 80.0 # this variable is no longer used by the new droppable widget code.

##
#
# Build related constants
#
##

# auto-generated files that are permitted to have non-committed changes when building project for distribution.

GENERATED_FILES = { "interfaces/interface_about.py",
"interfaces/interface_help.py",
"interfaces/interface_keyErrorBox.py",
"interfaces/interface_main.py",
"interfaces/interface_mainWidget.py",
"interfaces/interface_settingDialog.py",
"interfaces/interface_textDisplay.py",
"interfaces/interface_textrequestwidget.py",
"mainresources_rc.py"
}

GIT_PATH_OSX = "/opt/local/bin/git"
GIT_PATH_WIN = "c:\\Program Files\\Git\\bin\\git.exe"  # need to escape backslashes