# first, import a similar Provider or use the default one
from faker.providers import BaseProvider


# create new provider class
class TribuneProvider(BaseProvider):
    KINDS = (
        'answer',
        'moment',
        'markup',
        'totoz',
        'url',
    )

    MARKUP_MESSAGES = (
        """That's a <b>nice</b> <i>thing>/i> you got here""",
        """I'm <b>ok</b> with that!""",
        """You may add a new <code><div/></code> in your element""",
        """<tt>disco</tt> disco DISCO <b>DISCO</b>""",
        """<s>john</s>, paul, <s>george</s> and ringo""",
    )

    ANSWER_MESSAGES = (
        """12:12:12 No you don't""",
        """22:30:30""",
        """14:15:23 Yep 14:15:23 Nope""",
        """00:00:00 Refused""",
        """I ain't going nowhere until 16:45:00""",
    )

    TOTOZ_MESSAGES = (
        """[:totoz]""",
        """[:fail]""",
        """[:flu12]""",
        """[:klemton]""",
        """[:kzmir]""",
        """[:julm3]""",
        """[:fascinant]""",
    )

    URL_MESSAGES = (
        """http://perdu.com""",
        """https://linuxfr.org/news""",
        """https://google.fr""",
        """https://en.wikipedia.org/wiki/Western_conifer_seed_bug""",
        """http://minecraft.gamepedia.com/Crafting""",
        """http://internet-map.net/""",
        """https://www.smashingmagazine.com/tag/web-design/""",
        """http://heeeeeeeey.com/""",
    )

    MOMENT_MESSAGES = (
        """<m>The West Montgomery Trio - Whisper Not</m>""",
        """<m>AC/DC - Hells Bells</m>""",
        """<m>Laurent Coulondre - Vamos Tio</m>""",
        """<m>Bobby Timmons - This Here</m>""",
        """<m>Nazareth - Hair of the Dog</m>""",
        """<m>Willie Nelson - Night Life</m>""",
        """<m>Os Tres Morais - Freio Aerodinämico</m>""",
    )

    def tribune_message(self):
        method_name = """tribune_{}""".format(self.random_element(self.KINDS))
        return getattr(self, method_name)()

    def tribune_answer(self):
        return self.random_element(self.ANSWER_MESSAGES)

    def tribune_totoz(self):
        return self.random_element(self.TOTOZ_MESSAGES)

    def tribune_markup(self):
        return self.random_element(self.MARKUP_MESSAGES)

    def tribune_moment(self):
        return self.random_element(self.MOMENT_MESSAGES)

    def tribune_url(self):
        return self.random_element(self.URL_MESSAGES)


if __name__ == "__main__":
    from faker import Faker

    # add new provider to faker instance
    fake = Faker()
    fake.add_provider(TribuneProvider)

    # Dummy tests
    for i in range(0, 9):
        print(fake.tribune_message())
    print()