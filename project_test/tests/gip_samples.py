from __future__ import unicode_literals

SAMPLES = (
    (
        u'''Un lien correct http://perdu.com et un autre http://coin.org/foo.bar?po=1&foo=lop aussi''',
        u'''Un lien correct <a href="http://perdu.com">[url]</a> et un autre <a href="http://coin.org/foo.bar?po=1&amp;foo=lop">[url]</a> aussi''',
    ),
    (
        u'''Une url free pour la reconnaissance de motifs d'urls http://prout.free.fr et une autre http://prout.free.fr/flop/quiz voila''',
        u'''Une url free pour la reconnaissance de motifs d'urls <a href="http://prout.free.fr">[url]</a> et une autre <a href="http://prout.free.fr/flop/quiz">[url]</a> voila''',
    ),
    (
        u'''Une url entourée de quelque chose (http://machin.info)''',
        u'''Une url entourée de quelque chose (<a href="http://machin.info">[url]</a>)''',
    ),
    (
        u'''Un lien foireux http://<b>''',
        u'''Un lien foireux <a href="http://">[url]</a>''',
    ),
    (
        u'''Un url avec des accents http://fr.wikipedia.org/wiki/Téléphone voila<b>''',
        u'''Un url avec des accents <a href="http://fr.wikipedia.org/wiki/Téléphone">[url]</a> voila''',
    ),
    (
        u'''Url contenant des caractères pas frais http://fr.finance.yahoo.com/q/bc?s=^FCHI&t=1y&l=on&z=m&q=l&c=''',
        u'''Url contenant des caractères pas frais <a href="http://fr.finance.yahoo.com/q/bc?s=^FCHI&amp;t=1y&amp;l=on&amp;z=m&amp;q=l&amp;c=">[url]</a>''',
    ),
    (
        u'''gopher://gopher.floodgap.com/0/fun/figletgw?kupo!|font=isometric3 gopher y'a quand meme des truc qui dechirent /o\\''',
        u'''<a href="gopher://gopher.floodgap.com/0/fun/figletgw?kupo!|font=isometric3">[gopher]</a> gopher y'a quand meme des truc qui dechirent /o\\''',
    ),
    (
        u'''http://eur.news1.yimg.com/eur.yimg.com/xp/afpji/20060224/060224171152.46ftcfa50_un-lien-kil-est-long.jpg''',
        u'''<a href="http://eur.news1.yimg.com/eur.yimg.com/xp/afpji/20060224/060224171152.46ftcfa50_un-lien-kil-est-long.jpg">[url]</a>''',
    ),
    (
        u'''Une url avec [Ip:port] : http://192.168.0.101:8888/about/''',
        u'''Une url avec [Ip:port] : <a href="http://192.168.0.101:8888/about/">[url]</a>''',
    ),
    (
        u'''http://192.168.0.101:8888/about?foo=tu a le look coco&bar=ok''',
        u'''<a href="http://192.168.0.101:8888/about?foo=tu">[url]</a> a le look coco&amp;bar=ok''',
    ),
    (
        u'Un url de près de 360caractères http://www.marktplaats.nl/index.php?url=http%3A//kopen.marktplaats.nl/woningen-koop/buitenland/c1041.html%3Fxl%3D1%26ds%3Dto%253A1%253Bpu%253A0%253Bl1%253A1032%253Bl2%253A1041%253Bpa%253A150000%253Bdi%253A%253Blt%253Azip%253Bsfds%253A%253Bpt%253A0%253Bmp%253Anumeric%253Bosi%253A2%26ppu%3D0%26aw%255B68%255D%255B0%255D%3D448%26p%3D1%26av%5B-1%5D%5B0%5D%3D0',
        u'''Un url de près de 360caractères <a href="http://www.marktplaats.nl/index.php?url=http%3A//kopen.marktplaats.nl/woningen-koop/buitenland/c1041.html%3Fxl%3D1%26ds%3Dto%253A1%253Bpu%253A0%253Bl1%253A1032%253Bl2%253A1041%253Bpa%253A150000%253Bdi%253A%253Blt%253Azip%253Bsfds%253A%253Bpt%253A0%253Bmp%253Anumeric%253Bosi%253A2%26ppu%3D0%26aw%255B68%255D%255B0%255D%3D448%26p%3D1%26av%5B-1%5D%5B0%5D%3D0">[url]</a>''',
    ),
    (
        u'''Un totoz normal [:rofl] et correct [:excellent]''',
        u'''Un totoz normal <totoz name="rofl"/> et correct <totoz name="excellent"/>''',
    ),
    (
        u'''Un totoz en gras <b>[:rofl]</b> mais correct''',
        u'''Un totoz en gras <b><totoz name="rofl"/></b> mais correct''',
    ),
    (
        u'''Un totoz [:avec plein d'espace made in elly<] c'est fou''',
        u'''Un totoz [:avec plein d'espace made in elly&lt;] c'est fou''',
    ),
    (
        u'''<b>====> Moment Test - À la main en html <====</b>''',
        u'''<b>====&gt; Moment Test - À la main en html &lt;====</b>''',
    ),
    (
        u'''<m>Automatique</m>''',
        u'''<m>Automatique</m>''',
    ),
    (
        u'''<m>Foireux 1<m>''',
        u'''<m>Foireux 1</m>''',
    ),
    (
        u'''<m>Automatique 1</m> vs <m> Automatique 2 </m>''',
        u'''<m>Automatique 1</m> vs <m> Automatique 2 </m>''',
    ),
    (
        u'''<b>Avec un - http://www.none.fr/search?hl=fr&btnG=Recherche+Google&meta=&q=azedaed-</b>''',
        u'''<b>Avec un - <a href="http://www.none.fr/search?hl=fr&amp;btnG=Recherche+Google&amp;meta=&amp;q=azedaed-">[url]</a></b>''',
    ),
    (
        u'''<m>Avec un - http://www.none.fr/search?hl=fr&btnG=Recherche+Google&meta=&q=azedaed-</m>''',
        u'''<m>Avec un - <a href="http://www.none.fr/search?hl=fr&amp;btnG=Recherche+Google&amp;meta=&amp;q=azedaed-">[url]</a></m>''',
    ),
    (
        u'''2008/28/03#21:42:42 Horloge avec une date complète''',
        u'''2008/28/03#<clock time="1253220162" format="%H:%M:%S"/> Horloge avec une date complète''',
    ),
    (
        u'''20082803#02:42:11 Horloge avec une date complète mais incorrecte''',
        u'''20082803#<clock time="1253238131" format="%H:%M:%S"/> Horloge avec une date complète mais incorrecte''',
    ),
    (
        u'''12:00 Horloges en séries 1:00:11 13:59:07 21:21:21² 22:34:48 22:34:48⁶''',
        u'''<clock time="1253271600" format="%H:%M"/> Horloges en séries 1:<clock time="1253229060" format="%H:%M"/> <clock time="1253278747" format="%H:%M:%S"/> <clock time="1253218881" sel="²" format="%H:%M:%S"/> <clock time="1253223288" format="%H:%M:%S"/> <clock time="1253223288" format="%H:%M:%S"/>⁶''',
    ),
    (
        u'''21:42:42 horloge simple et correcte avec un smiley [:alf]''',
        u'''<clock time="1253220162" format="%H:%M:%S"/> horloge simple et correcte avec un smiley <totoz name="alf"/>''',
    ),
    (
        u'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
        u'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
    ),
    (
        u'''Un message <b>totalement</b> <u>correct</u>''',
        u'''Un message <b>totalement</b> <u>correct</u>''',
    ),
    (
        u'''Un message <b>totalement </u>incorrect</u>''',
        u'''Un message <b>totalement incorrect</b>''',
    ),
    (
        u'''Un message <b>partiellement</b> <u>correct''',
        u'''Un message <b>partiellement</b> <u>correct</u>''',
    ),
    (
        u'''Test <de faux attributs/> <et attributs =""/> xml''',
        u'''Test &lt;de faux attributs/&gt; &lt;et attributs =""/&gt; xml''',
    ),
    (
        u''''"''"#\\'"'foirade'''"&"'totale''',
        u''''"''"#\\'"'foirade&amp;totale''',
    ),
    (
        u'''Un bout de code <code><?php echo <b>phpinfo();</b> ?></code> en php kipu''',
        u'''Un bout de code <code>&lt;?php echo phpinfo(); ?&gt;</code> en php kipu''',
    ),
    (
        u'''13:42:12² Un post http://perdu.com <b>complet</b> [:lol] et <u>correct</u> 12:12 tu l'a dit bouffi : http://yahoo.fr/actus [:rofl]''',
        u'''<clock time="1253277732" sel="²" format="%H:%M:%S"/> Un post <a href="http://perdu.com">[url]</a> <b>complet</b> <totoz name="lol"/> et <u>correct</u> <clock time="1253272320" format="%H:%M"/> tu l'a dit bouffi : <a href="http://yahoo.fr/actus">[url]</a> <totoz name="rofl"/>''',
    ),
)