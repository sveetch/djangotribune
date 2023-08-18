.. _Django internationalization system: https://docs.djangoproject.com/en/dev/topics/i18n/
.. _texttable: http://pypi.python.org/pypi/texttable/0.8.1
.. _crispy-forms-foundation: https://github.com/sveetch/crispy-forms-foundation
.. _South: http://south.readthedocs.org/en/latest/

**Project is no longer maintained and has been archived**

Introduction
============

This Django app is a *chat-like application* with some aspects of *IRC* but with a 
strong usage of message clocks.

**Message clocks** are always displayed and used in message to reference answer or 
relation with other messages.

A sample part of Tribune messages will look like this in a plain-text version : ::
    
    16:15:27     <superman>            First
    16:16:13     Anonymous coward      16:15:27 oh no you don't !
    16:15:27     <superman>            16:16:13 lier !
    18:39:01     Mozilla/5.0           Hello world !
    18:39:05     <superman>            18:39:01 hello
    18:43:22     Anonymous coward      18:39:01 yo

The application has a rich interface but is also accessible from third client 
application (via a XML backend) and even in plain text.

Features
********

* Easy embedding in your Django webapp;
* Various backends `Formats`_;
* `Action commands`_;
* `Message filtering`_ usually called a *BaK*;
* A rich interface (currently in development);
* Full localization for french and english language;
* `Discovery`_ XML configuration file for third client applications (aka remote client or *coincoins*);
* Channel support;
* `South`_ support;

Links
*****

* Download his `PyPi package <http://pypi.python.org/pypi/djangotribune>`_;
* Clone it on his `Github repository <https://github.com/sveetch/djangotribune>`_;
* Documentation on `Read the Docs <http://djangotribune.readthedocs.org/>`_;
