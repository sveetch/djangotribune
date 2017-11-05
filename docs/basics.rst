.. _Django internationalization system: https://docs.djangoproject.com/en/dev/topics/i18n/
.. _LastFM API: http://www.lastfm.fr/api/intro
.. _texttable: http://pypi.python.org/pypi/texttable/0.8.1
.. _crispy-forms-foundation: https://github.com/sveetch/crispy-forms-foundation
.. _South: http://south.readthedocs.org/en/latest/
.. _Foundation3: http://foundation.zurb.com/docs/v/3.2.5/

.. _intro_basics:

******
Basics
******

.. _message-backends-label:

Message backends
================

Backends are available in various formats, each format has its own special features.
Usually, *JSON* is for webapp usage, *XML* for remote clients and *Plain* for some
nerdz.

.. _formats-label:

Formats
-------

Every paths below are relative to djangotribune URL.

**Plain-text**
    Very light, use the raw message, ascendant ordered by default. Url path from the
    tribune is ``remote/`` for backend and ``post/`` for post view.
**XML**
    Very fast, use the remote message render, descendant ordered by default. Url path from
    the tribune is ``remote/xml/`` for backend and ``post/xml/`` for post view.
**CRAP XML**
    The *extended* XML version to go well with old tribune application clients. Currently the
    only diff is the XML structure wich is indented. Url path from the tribune is
    ``crap/remote.xml`` for backend and ``crap/post.xml`` for post view.
**JSON**
    Very *declarative*, use the web message render, descendant ordered by default. Url
    path from the tribune is ``remote/json/`` for backend and ``post/json/`` for post
    view.
**Tabulation Separated Values**
    A lightweight backend format intended for some recent third application
    clients. It works like Plain-text format excepting each message parts
    (id, clock, message, user, etc..) are separated with tabulation character.
    Url path for backend is ``remote/tsv/`` and ``post/tsv/``
    for post view.

.. NOTE:: For channel backend and post urls you must prepend the path with the channel
          slug, by example with a channel slug ``foo`` for the XML backend you will need
          to do ``foo/remote/xml/``.


.. _url-arguments-label:

Url arguments
-------------

On backend URLs, you can set some options by adding URL arguments like this : ::

    /remote/?limit=42&direction=asc&last_id=77

**limit**
    An integer to specify how many messages can be retrieved. This value cannot be greater
    than the setting value ``TRIBUNE_MESSAGES_MAX_LIMIT``. Default value comes from
    setting ``TRIBUNE_MESSAGES_MAX_LIMIT`` if this option is not specified.
**direction**
    Message listing direction specify whether the list should be ordered by ``id`` in
    ascendant or descendant way. Value can be ``asc`` for ascendant or ``desc`` for
    descendant. Each backend can have its own default direction.
**last_id**
    The last ``id`` from wich to retrieve the messages in the interval of the ``limit``
    option.

    For example, with a *tribune* with 42 messages numbered (on their ``id``) from 1
    to 42, and with default limit to 30 :

    * Requesting a backend without any option will return messages from ``id`` 13 to 42;
    * Requesting a backend with option ``limit`` to 10, will return messages from ``id``
      33 to 42;
    * Requesting a backend with option ``last_id`` to 15 will return messages from ``id``
      16 to 42;
    * Requesting a backend with option ``limit`` to 5 and option ``last_id`` to 15 will
      return messages from ``id`` 38 to 42;

    No matter what direction you specify in option, the results will stay identical.

.. _message-posting-system-label:

Message posting system
======================

The tribune can either be used from the web interface or via remote client applications.

.. _message-posting-system-remote-label:

Remote client applications
--------------------------

Remote clients can send a new message directly within a **POST** request and by putting the
content in a ``content`` argument.

* Validated messages from a request without ``last_id`` defined return an empty Http200 response
  in plain-text;
* Validated messages from a request with ``last_id`` defined return the last updated backend (from
  the *known* last id);
* Unvalid message return an Http error.

If ``last_id`` is given in the **POST** request it will be used instead of **GET** argument.

All POST response for validated message return a **X-Post-Id** header that contain the ID of the
new message.

:ref:`url-arguments-label` options can be given for the POST request and they will be used for the returned
backend in case of success.

In fact, remote client applications should always give the
``last_id`` option (taken from the last message they know just before sending the POST
request) to receive only messages they didn't know (and not the whole backend).

.. _message-posting-system-errors-label:

Dealing with errors
...................

* This is not really an error, but remote backend returns a **Http304** (*NotModified*) when
  you try to fetch a backend with no new message;
* If the *POST* request is invalidated (with the form), the returned response will be a
  **Http400** (*Bad Request*) with an explanation in Ascii;
* A **Http404** is returned when you try to use a channel remote backend that
  doesn't exists;
* You could receive a **Http500** (*Internal Server Error*) in case of bugs or bad
  configured server;
* Sometimes you can receive a **Http403** if you try to use a restricted command but
  there are not implemented yet.

.. _messagefiltering-system-label:

Message filtering system
========================

All users (registred and anonymous) can manage their own entries for filtering messages
on various pattern. These filters are stored in the user session in an object called BaK
as *Boîte à Kons* (eg: *Idiots box*) which is persistent in your session.

That being so, a user can lose its session (after a very long inactivity or when logged out)
so there are option to **save** the filters of your BaK in your profile in a database. So
you can **load** them in your session when needed.

There is two ways to manage filters from your bak :

* You can use **the easy way** which always assumes you use an exact pattern, this is the
  purpose of options **add** and **del** than expects only two arguments, a target and
  the pattern;
* Or you can use **the verbose way** which expects three arguments respectively the target,
  the kind and the pattern, this is the purpose of options **set** and **remove**;

Available arguments
-------------------

**target**
    The part of the message which will be used to apply the filter, available targets are :

    * ``ua`` for the user-agent;
    * ``author`` for the author username only effective for messages from registered users;
    * ``message`` for the message in his raw version (as it was posted).
**kind**
    The kind of matching filter that will be used. Only used in the *verbose way*
    options, for the *easy way* this is always forced to an exact matching.

    Kinds are written like *operators*, the available kinds are :

    * ``*=`` for Case-sensitive containment test;
    * ``|=`` for Case-insensitive containment test;
    * ``==`` for Case-sensitive exact match;
    * ``~=`` for Case-insensitive exact match;
    * ``^=`` for Case-sensitive starts-with;
    * ``$=`` for Case-sensitive ends-with.
**pattern**
    The pattern to match by the filter. This is a simple string and not a regex pattern.
    You can use space in your pattern without quoting it.

Options details
---------------

**add**
    The *easy way* to add a new filter. This requires two arguments, the target and the
    pattern like that : ::

        /bak add author Badboy
**del**
    The *easy way* to drop a filter. This requires two arguments, the target and the
    pattern that you did have used, like that : ::

        /bak del author Badboy
**set**
    The *verbose way* to add a new filter. This requires three arguments, the target, the
    kind operator and the pattern like that : ::

        /bak set author == Badboy
**remove**
    The *verbose way* to drop a filter. This requires three arguments, the target, the
    kind operator and the pattern like that : ::

        /bak remove author == Badboy
**save**
    To save your current filters in your session to your profile in database, this works only
    for registered users.

    Saving your filters will overwrite all your previously saved filters, so if you just
    want to add new filters, load the previously saved filters before.

    This is option does not require any argument : ::

        /bak save
**load**
    To load your previously saved filters in your current session. If you already have
    filters in your current session this will overwrite them.

    This is option does not requires any argument : ::

        /bak load
**on**
    To enable message filtering using your filters in current session. A new session have
    message filtering enabled by default.

    This is option does not requires any argument : ::

        /bak on
**off**
    To disable message filtering using your filters in current session. The filters will
    not be dropped out of your session so you can enable them after if needed.

    This is option does not requires any argument : ::

        /bak off
**reset**
    To clear all your filters in current session. You can use this option followed after
    by a save action to clear your saved filters too.

    This is option does not requires any argument : ::

        /bak reset

.. NOTE:: Messages filters will not be retroactive on displays on remote clients, only
          for new message to come after your command actions. So generally you will have
          to reload your client to see applied filters on messages posted before your
          command actions.

