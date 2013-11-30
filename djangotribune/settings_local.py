# -*- coding: utf-8 -*-
"""
App default settings
"""
from django.conf import settings

# If ``True`` only logged user can read and write to the tribune, Anonymous user will be 
# rejected either from backend or post requests
TRIBUNE_LOCKED = getattr(settings, 'TRIBUNE_LOCKED', False)

# Default message limit to display in backend
TRIBUNE_MESSAGES_DEFAULT_LIMIT = getattr(settings, 'TRIBUNE_MESSAGES_DEFAULT_LIMIT', 50)
# Maximum value allowed for the message limit option
TRIBUNE_MESSAGES_MAX_LIMIT = getattr(settings, 'TRIBUNE_MESSAGES_MAX_LIMIT', 100)
# Maximum length (in characters) for the content message
TRIBUNE_MESSAGES_POST_MAX_LENGTH = getattr(settings, 'TRIBUNE_MESSAGES_POST_MAX_LENGTH', 500)

# Default time refresh shifting to use on the board interface, time is in milli-seconds
TRIBUNE_INTERFACE_REFRESH_SHIFTING = getattr(settings, 'TRIBUNE_INTERFACE_REFRESH_SHIFTING', 10000)

# Name for the cookie which carry on the customized user agent
TRIBUNE_MESSAGES_UA_COOKIE_NAME = getattr(settings, 'TRIBUNE_MESSAGES_UA_COOKIE_NAME', 'djangotribune_user-agent')
# Maximum age time for the UserAgent cookie
TRIBUNE_MESSAGES_UA_COOKIE_MAXAGE = getattr(settings, 'SESSION_COOKIE_AGE', (60 * 60 * 24 * 7 * 8))
# Minimum length (in characters) for an user-agent value, this is used to validate 
# *custom name* and for the browser user-agent (if it's under limit, will be replaced 
# by *coward*).
TRIBUNE_MESSAGES_UA_LENGTH_MIN = getattr(settings, 'TRIBUNE_MESSAGES_UA_LENGTH_MIN', 3)

# Template string for smileys URL, this is where you can set the wanted smiley host
TRIBUNE_SMILEYS_URL = getattr(settings, 'TRIBUNE_SMILEYS_URL', 'http://sfw.totoz.eu/{0}.gif')

# Name for session part containing the BaK
TRIBUNE_BAK_SESSION_NAME = getattr(settings, 'TRIBUNE_BAK_SESSION_NAME', 'djangotribune_bak')

# Maximum number of user message id saved in session
TRIBUNE_SESSION_MAX_OWNED_IDS = getattr(settings, 'TRIBUNE_SESSION_MAX_OWNED_IDS', 50)

# How many urls maximum will be saved in a message
TRIBUNE_SAVE_URLS_BY_POST = getattr(settings, 'TRIBUNE_SAVE_URLS_BY_POST', 5)

# Titles randomly displayed on tribune board (html and plain/text versions)
TRIBUNE_TITLES = getattr(settings, 'TRIBUNE_TITLES_AVAILABLE', (
    u'Avengers Mansion', # Marvel Comics
    u'Gotham City', # DC Comics
    u'Morrison Hotel', # Album des Doors
    u'Maysaf', # Assassin's Creed
    u'Cheyenn Mountain', # Stargate
    u'Mines of Moria', # LOTRO
    # Red Dead Redemption
    u'Armadillo',
    u'Chuparosa',
    u'Tumbleweed',
    # Babylon 5
    u'Secteur Gris, niveau 6',
    u'Zahadum',
    # Fallout3
    u'Abri 101',
    u'Rockopolis',
    u'Megaton',
    # GTA
    u'Vice City',
    u'San Andreas',
    u'Liberty City',
    # Hercule Poirot
    u'Whitehaven Mansions',
    # Zorel
    u'La trouée des Trolls',
    u'Twilight Zone',
    u'Mon curé chez les musselidés',
    u'One mussel on the moon',
    u"Nan c'est à côté",
    u'Here be dragons',
    # Profitroll
    u'Le petit bonhomme en mousse',
    # Fab&lhg
    u'Au royaume des lusers, les geeks sont rois',
    # Eddy
    u'Parle à ma main',
    # Sensei
    u"Place de l'inquisition",
    # Nostromo
    u"On n'est pas à C dans l'air ici",
    # Divers
    u"Tom Petty Fan club",
    u"L'île aux pirates",
    u'Environnement Confiné',
    u'Hôtel Palace',
    u'La Tour de Gay',
    u'1 rue Sésame',
    u'Zone 42',
    u'Dance Floor',
    u'Poire Mécanique',
    u'Tibet Libre',
    u'PaTribune PaLibre',
    u'Hello World',
    u'Hello Kitty Land',
    u'La Tour Sombre',
    u'[:uxam]',
    u'Grrrrrr',
    u'I can haz shiny post too',
    u'Institut de la connaissance universelle',
    u'Please, insert coin',
    u'alt.tribune.dax',
    u'/b/',
    u"Only Classic Rock n' Roll",
    u"Dollarmussels",
))

# URL to the LastFM API to use the lastfm command action
TRIBUNE_LASTFM_API_URL = getattr(settings, 'TRIBUNE_LASTFM_API_URL', 'http://ws.audioscrobbler.com/2.0/')
# API Key used by djangotribune with the LastFM API
TRIBUNE_LASTFM_API_KEY = getattr(settings, 'TRIBUNE_LASTFM_API_KEY', '07f44b8af0c8fbf981b064ff04b3bce5')

TRIBUNE_SHOW_TRUNCATED_URL = getattr(settings, 'TRIBUNE_SHOW_TRUNCATED_URL', False)
