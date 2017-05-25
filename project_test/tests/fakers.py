from faker import Faker

# first, import a similar Provider or use the default one
from faker.providers import BaseProvider

# create new provider class
class TribuneProvider(BaseProvider):
    KINDS = (
        'answer',
        'moment',
        'markup',
        'totoz',
        #'url',
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
        """14:15:23 Yep 14:15:23 Nope""",
        """00:00:00 Refused""",
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

    MOMENT_MESSAGES = (
        """<m>The West Montgomery Trio - Whisper Not</m>""",
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

if __name__ == "__main__":
    # add new provider to faker instance
    fake = Faker()
    fake.add_provider(TribuneProvider)

    for i in range(0, 9):
        print(fake.tribune_message())
    print()