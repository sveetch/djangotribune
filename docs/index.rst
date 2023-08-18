.. djangotribune documentation master file, created by
   sphinx-quickstart on Sun Dec  1 22:21:02 2013.
.. _South: http://south.readthedocs.org/en/latest/

*************
djangotribune
*************

**Project is no longer maintained and has been archived**

Django-tribune is a *chat-like application* with some aspects of *IRC* but with a
strong usage of message clocks.

**Message clocks** are always displayed and used in messages to reference answers or
relation with other messages.

A sample part of Tribune messages will look like this in a plain-text version : ::

    16:15:27     <superman>            First
    16:16:13     Anonymous coward      16:15:27 oh no you don't !
    16:15:27     <superman>            16:16:13 liar !
    18:39:01     Mozilla/5.0           Hello world !
    18:39:05     <superman>            18:39:01 hello
    18:43:22     Anonymous coward      18:39:01 yo

The application has a rich interface but is also accessible from third client
application (via a XML backend) and even in plain text.

Features
========

* Easy embedding in your Django webapp;
* Various backends :ref:`formats-label`;
* :ref:`action-commands-label`;
* :ref:`messagefiltering-system-label` usually called a *BaK*;
* A rich interface (currently in development);
* Full localization for french and english language;
* :ref:`discovery-label` XML configuration file for third client applications (aka remote client or *coincoins*);
* Channel support;
* `South`_ support;

Links
=====

* Download his `PyPi package <http://pypi.python.org/pypi/djangotribune>`_;
* Clone it on his `Github repository <https://github.com/sveetch/djangotribune>`_;

Contents
--------

.. toctree::
   :maxdepth: 3

   install.rst
   basics.rst
   usage.rst
   changelog.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

