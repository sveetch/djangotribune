# -*- coding: utf-8 -*-
"""
Message parsers and renderer
"""
import re
from datetime import datetime

from six import StringIO

from django.template.defaultfilters import truncatechars

from djangotribune.settings_local import TRIBUNE_SMILEYS_URL, TRIBUNE_SHOW_TRUNCATED_URL


POST_CLEANER_TAG_RE = '<(?P<tag>/?(?:b|i|s|u|tt|m|code))>'
POST_CLEANER_SCHEME_RE = '(?P<scheme>(?:http|ftp|https|chrome|gopher|git|git+ssh|svn|svn+ssh)://)'
# TODO: think about to implement clock format with date aka "mm/jj#HH:MM:SS"
POST_CLEANER_CLOCK_RE = u'(?<![0-9])(?P<clock>(?P<h>2[0-3]|[01][0-9])(?P<c>(?=[0-5][0-9][:0-9])|:)(?P<m>[0-5][0-9])(?:(?P=c)(?P<s>[0-5][0-9])(?:(?P<sel>[¹²³⁴⁵⁶⁷⁸⁹][⁰¹²³⁴⁵⁶⁷⁸⁹]?|[\^:][1-9][0-9]?))?)?)(?![0-9:@])'
POST_CLEANER_TOTOZ_RE = '(?P<totoz>\[\:[A-Za-z0-9-_@ ]+(?:\:[0-9]+)?\])'
POST_CLEANER_RE = re.compile('(' + POST_CLEANER_TOTOZ_RE + '|(?P<sep>[\(\)\[\]"])|' + POST_CLEANER_TAG_RE + '|' + POST_CLEANER_SCHEME_RE + '|' + POST_CLEANER_CLOCK_RE + ')')
POST_CLEANER_SEP_END = { '(': ')', '[': ']', '"': '"' }


# TODO: move to settings "local" and use re.compile
URL_SUBSTITUTION = (
    (r".tar.gz", "tgz"),
    (r".tgz", "tgz"),
    (r".(zip|rpm|deb|tgz)$", r"\1"),
    (r".pdf", "pdf"),
    (r"http://localhost", "localhost"),
    (r"wikipedia.org/wiki/(.*)", r"\1@wikipedia"),
    (r"youtube.com", "youtube"),
    (r"dailymotion.com", "dailymotion"),
    (r"bashfr.org", "bashfr"),
    (r"imdb.com", "imdb"),
    (r"google.", "google"),
    (r"yahoo.", "yahoo"),
    (r"lemonde.fr", "lemonde"),
    (r"liberation.fr", "libe"),
    (r"lefigaro.fr", "lefigaro"),
    (r"journaldunet.", "jdn"),
    (r"01net.com", "01net"),
    (r"forum.hardware", "hfr"),
    (r"linuxfr.org", "Dlfp"),
    (r"goatse", "pas cliquer!"),
    (r"goat.cx", "pas cliquer!"),
    (r"glazman.org", "yerk pas cliquer!"),
    (r".ssz.fr", "pas cliquer non plus!"),
    (r"wiki", "wiki"),
    (r"wickedweasel", "WW"),
    (r"slashdot.org", "/."),
    (r"osnews.com", "osnews"),
    (r"zdnet.", "zdnet"),
    (r"ruby", "ruby"),
    (r"/goomi/unspeakable", "Fhtagn!"),
    (r"http://(.*).free.fr", r"\1@free"),
)


def XmlEntities(s):
    """
    Replace HTML entities to valid XML entities (with numeric character
    reference ``&#nnnn;``).
    """
    return s.replace('&', '&#38;').replace('<', '&#60;')\
            .replace('>', '&#62;').replace('"', '&#34;')


def PostMatchIterator(str):
    """
    Custom iterator to split string using message regex from
    ``POST_CLEANER_RE``.

    NOTE: No test coverage.
    """
    lastIndex = 0
    for match in re.finditer(POST_CLEANER_RE, str):
        if match.start() > lastIndex:
            yield ['txt', str[lastIndex:match.start()]]
        for category in ['sep', 'tag', 'scheme', 'clock', 'totoz']:
            if match.group(category):
                yield [category, match]
                break
        lastIndex = match.end()
    if len(str) > lastIndex:
        yield ['txt', str[lastIndex:]]


def ListPopIterator(list):
    """
    Custom iterator to consume every parts

    NOTE: No test coverage.
    """
    while True:
        try:
            yield list.pop()
        except: break


class GenericPostCleaner(list):
    """
    Basic message parser.

    Basic parser is only about to split a string into message parts where each
    part can be a text, a clock, a totoz, an url or a recognized tag. It is an
    inheritor from ``list`` object.

    Available part kinds are:

    * A message text part until another element kind is
      encountered, if so it will close its part before to potentially continue
      in another following part;
    * A *Totoz* that is a smiley name surrounded with bracket and colon like
      this ``[:name]``;
    * Any url starting with recognized protocol from
      ``POST_CLEANER_SCHEME_RE``;
    * A time clock with hour, minute and second like ``12:00:15``;
    * A recognized HTML tag from ``POST_CLEANER_TAG_RE``, this is not
      necessarily a valid HTML tag;

    Recognized tags are corrected when not
    correctly written like missing closing tag, attributes, etc.. Other tags
    are just escaped (or at least pretended to be so for this basic parser).

    Processing and formatting methods (named like ``append_xxxx``) in this
    parser only append given content as a message, excepting for clock and tag
    methods.

    Original credits to Mike Hommey :
    mh AT glandium DOT org
    """
    def __init__(self):
        self._tags = []
        super(GenericPostCleaner, self).__init__()

    def __str__(self):
        return ''.join(self)

    def __iter__(self):
        for t in ListPopIterator(self._tags):
            self.pop_or_append('<%s>' % t, '</%s>' % t)
        return super(GenericPostCleaner, self).__iter__()

    def pop_or_append(self, pop, append):
        if len(self) > 0 and self[len(self) - 1] == pop:
             self.pop()
        else:
             self.append(append)

    def format_clock(self, weight_format, h, m, s):
        """
        Format given time args to a clock display depending from given clock
        weight format.

        Args:
            weight_format (string): Clock weight format like ``%H:%M:%S``. In
                fact, method only worries about presence of ``:`` in the third
                position of format so it will be added in formatted clock or
                not.
            h (integer): Hours.
            m (integer): Minutes
            s (integer): Seconds.

        Returns:
            string: Allways return a clock with seconds even if equal to zero.
            Clock parts will separeted with ``:`` or not depending from
            ``weight_format``.
        """
        clock = ('%02d:%02d' if weight_format[2] == ':' else '%02d%02d') % (h, m)
        if s != None:
            clock += (':%02d' if weight_format[2] == ':' else '%02d') % s

        return clock

    def append_tag(self, tag):
        """tag is given without <>"""
        if tag[0] == '/':
            if tag[1:] in self._tags:
                for t in ListPopIterator(self._tags):
                    self.pop_or_append('<%s>' % t, '</%s>' % t)
                    if t == tag[1:]:
                        break
        else:
            self._tags.append(tag)
            self.pop_or_append('</%s>' % tag, '<%s>' % tag)

    def append_escape(self, string):
        """
        Escape string from HTML entities and append it to message parts.
        """
        self.append(string)

    def append_url(self, scheme, url):
        """
        Process url string and append it to message parts.
        """
        self.append(url)

    def append_totoz(self, totoz):
        """
        Process totoz string and append it to message parts.
        """
        self.append(totoz)

    def append_clock(self, weight_format, h, m, s, sel):
        """
        Process clock string and append it to message parts.
        """
        if not sel:
            sel = ''
        self.append(self.format_clock(weight_format, h, m, s) + sel)

    def append_batch(self, str):
        """
        Parse and split given string into message parts.
        """
        lastSep = ''
        code = 0
        iterator = iter(PostMatchIterator(str))
        for type, match in iterator:
            if type == 'txt':
                self.append_escape(match)
            elif code:
                if type == 'tag' and match.group('tag') == '/code':
                     self.append_tag(match.group('tag'))
                     code = 0
                else:
                    self.append_escape(match.group(0))
            elif type == 'sep':
                sep = match.group('sep')
                if sep in ['(', '[', '"']:
                    lastSep = sep
                self.append(sep)
            elif type == 'tag':
                if match.group('tag') == 'code':
                    code = 1
                self.append_tag(match.group('tag'))
            elif type == 'scheme':
                scheme = match.group('scheme')
                url = ''
                i = -1
                if lastSep:
                    end = POST_CLEANER_SEP_END[lastSep]
                else:
                    end = ' '
                url += scheme
                for type, match in iterator:
                    if type == 'tag' or (type == 'sep' and match.group('sep') == end):
                        break
                    if type == 'txt':
                        try:
                            i = match.index(' ')
                            url += match[:i]
                            break
                        except:
                            url += match
                    else:
                        url += match.group(0)
                self.append_url(scheme, url)
                if i != -1:
                    self.append_escape(match[i:])
                #if type == 'sep':
                if type == 'sep' and match.group('sep') == end:
                    self.append(match.group('sep'))
                elif type == 'tag':
                    self.append_tag(match.group('tag'))
            elif type == 'clock':
                if not match.group('s'):
                    format = '%H:%M'
                elif match.group('c'):
                    format = '%H:%M:%S'
                else:
                    format = '%H%M%S'
                self.append_clock(format, int(match.group('h')), int(match.group('m')),
                                                 int(match.group('s')) if match.group('s') else None, match.group('sel'))
            elif type == 'totoz':
                self.append_totoz(match.group('totoz'))


class PostCleaner(GenericPostCleaner):
    """
    Functional message parser.

    Opposed to the basic message parser, this one process every part to apply
    some formatting. Also it escapes string and makes some indexes about finded
    totoz, clock and urls.
    """
    def __init__(self, link_rel_escape):
        super(PostCleaner, self).__init__()
        self.matched_totozs = []
        self.matched_clocks = []
        self.matched_urls = []
        self.link_rel_escape = link_rel_escape

    def append_escape(self, s):
        self.append(XmlEntities(s))

    def append_url(self, scheme, url):
        # scheme includes ://
        self.append('<a href="')
        self.append_escape(url)
        self.append('"%s>' % self.link_rel_escape)
        self.append( self.link_formatter(scheme[0:-3], url) )
        self.append('</a>')
        self.matched_urls.append(url)

    def append_totoz(self, totoz):
        # totoz contains enclosing [: ]
        self.append('<totoz name="%s"/>' % totoz[2:])
        self.matched_totozs.append(totoz[2:])

    def append_clock(self, weight_format, h, m, s, sel):
        time = self.format_clock(weight_format, h, m, s)
        if not sel:
            sel = ''
        self.append('<clock time="%s">' % (time.replace(':','')))
        self.append(time + sel)
        self.append('</clock>')
        self.matched_clocks.append(time + sel)

    def truncate_link(self, scheme, url):
        return truncatechars(url.replace(scheme + '://', ''), 100)

    def link_formatter(self, scheme, url):
        """
        Format link according to url, determine name from ``URL_SUBSTITUTION``
        label patterns.
        """
        if TRIBUNE_SHOW_TRUNCATED_URL:
            return self.truncate_link(scheme, url)

        # Label par défaut des urls
        title = scheme
        if title == 'http':
            title = 'url'

        # Renommage du label du lien selon son url
        for k,v in URL_SUBSTITUTION:
            matched = re.search(k, url)
            # On a trouvé un motif de label
            if matched:
                # Motif avec substitution dynamique
                if len(matched.groups(0))>0:
                    title = matched.expand(v)
                # Motif avec substitution simple
                else:
                    title = v
                break

        return "[%s]" % title


class MessageParser(object):
    """
    Message renderer.

    Using functional parser, it render a message to a HTML and a XML versions.
    """
    def __init__(self, smileys_url=TRIBUNE_SMILEYS_URL, min_width=2):
        self.smileys_url = smileys_url
        self.min_width = min_width
        self.link_rel_escape = "$LinkRelEscape{0}$".format(datetime.now().strftime('%s'))

    def render(self, source):
        """
        Render given string to HTML and XML.
        """
        lastIndex = 0
        slipped_web = StringIO()
        slipped_remote = StringIO()
        # Procède au scan et nettoyage de la source
        parserObject = PostCleaner(link_rel_escape=self.link_rel_escape)
        parserObject.append_batch( source )
        cleaned_source = unicode( parserObject )

        # Itération sur les résultats de la Regex de formattage
        for chunk in parserObject:
            if chunk[0] == '<':
                # Moment
                if chunk == '<m>':
                    slipped_web.write('====&#62; <b>Moment ')
                    slipped_remote.write('====&#62; <b>Moment ')
                elif chunk == '</m>':
                    slipped_web.write('</b> &#60;====')
                    slipped_remote.write('</b> &#60;====')
                # Horloge
                elif chunk[0:7] == '<clock ':
                    slipped_web.write('<span class="pointer">')
                    #slipped_remote.write(chunk)
                elif chunk == '</clock>':
                    slipped_web.write('</span>')
                    #slipped_remote.write(chunk)
                # Smileys
                elif chunk[0:7] == '<totoz ':
                    totoz = chunk[13:-4]
                    totoz_url = self.smileys_url.format(totoz)
                    slipped_web.write('<a class="smiley" href="%s" rel="nofollow">[:%s]</a>' % (totoz_url, totoz))
                    slipped_remote.write('[:%s]'%totoz)
                else:
                    slipped_web.write(chunk)
                    slipped_remote.write(chunk)
            else:
                slipped_web.write(chunk)
                slipped_remote.write(chunk)

        return {
            'web_render': slipped_web.getvalue().replace(self.link_rel_escape, ' class="external" rel="nofollow"'),
            'remote_render': slipped_remote.getvalue().replace(self.link_rel_escape, ''),
            'urls': parserObject.matched_urls,
            'smileys': parserObject.matched_totozs,
            'clocks': parserObject.matched_clocks,
        }

    def validate(self, source):
        ## TODO: invalidate for words with a crazy length
        #if len(source.strip()) < self.min_width:
            #return False
        return True
