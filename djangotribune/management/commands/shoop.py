# -*- coding: utf-8 -*-
"""
Tribune command line

TEMPORARY
"""
import datetime, json, random, string

from optparse import OptionValueError, make_option

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import CommandError, BaseCommand
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail

announce = """Bonjour,

Le site "dax.sveetch.net" a migré sur http://sveetch.net avec un nouveau moteur.

Votre compte utilisateur '{username}' y a été importé avec un nouveau mot de passe :

{new_password}

Vous pourrez le modifier en vous connectant.

"""

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--users", dest="user_dump_filepath", default=None, help="Dump file to user to import users, use it only on a clean install, there is no check for uniqueness of users"),
    )
    help = "Command for importing data from shoop's dump files"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        self.user_dump_filepath = options.get('user_dump_filepath')
        
        if self.user_dump_filepath:
            self.import_users()

    def import_users(self):
        messages = []
        
        dump_fp = open(self.user_dump_filepath, "r")
        dump = json.load(dump_fp)
        dump_fp.close()
        
        for item in dump:
            print "* Importing:", item['username']
            try:
                existing = User.objects.get(username=item['username'])
            except User.DoesNotExist:
                #id,username,first_name,last_name,email,last_login,date_joined
                date_joined = datetime.datetime(*item['date_joined'])
                last_login = datetime.datetime(*item['last_login'])
                new_password = self.id_generator()
                # Save the new user
                new_user = User(
                    username=item['username'],
                    first_name=item['first_name'],
                    last_name=item['last_name'],
                    email=item['email'],
                    last_login=last_login,
                    date_joined=date_joined,
                    password="",
                    is_active=True,
                )
                new_user.set_password(new_password)
                new_user.save()
                # Make his email
                msg = announce.format(username=new_user.username, new_password=new_password)
                messages.append(['dax.sveetch.net has moved to sveetch', msg, 'sveetch@gmail.com', [new_user.email]])
            else:
                print "Allready exists, passed"

        # Sending all email
        if len(messages)>0:
            send_mass_mail(messages, fail_silently=False)
        
    def id_generator(self, size=8, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))
