.. contents:: 
.. sectnum::

Introduction
============

This Django app is a *chat-like application* with some aspects from *IRC* but with a 
strong usage of message clocks.

**Message clocks** are always displayed and used in message to reference anwser or 
relation with other messages.

A sample part of Tribune messages will look like this in a plain-text version : ::
    
    16:15:27     <superman>            First
    16:16:13     Anonymous coward      16:15:27 oh no you don't !
    16:15:27     <superman>            16:16:13 lier !
    18:39:01     Mozilla/5.0           Hello world !
    18:39:05     <superman>            18:39:01 hello
    18:43:22     Anonymous coward      18:39:01 yo

Currently in alpha version, this include :

* An awesome project title;
* Data models;
* Queryset filtering API for "standard" tribune behavior and more with some options;
* All stuff for base remote views and remote views in various formats;
* Message posting views;
* ...
* Profit !

Installation
============

Actually Django-tribune doesn't require any dependancy, just register the app in your 
project settings like this : ::

    INSTALLED_APPS = (
        ...
        'djangotribune',
        ...
    )

Then after you should register the app urls in your project ``urls.py`` : ::

    url(r'^tribune/', include('djangotribune.urls')),

Of course you can use another mounting directory than the default ``tribune/`` or even 
use your own app urls, look at the provided ``djangotribune.urls`` to see what you have 
to map.

And finally don't forget to do the Django's *syncdb command* to synchronise models in your 
database.

Usage
=====

The tribune can either be used from the web interface or via remote client applications.

Message backends
****************

Backends are available under various formats, each format have his own specificity. 
Generally, *JSON* is for webapp usage, *XML* for remote clients and *Plain* for some 
nerdz.

Formats
-------

Plain-text
    Very light, use the raw message, ascendant ordered on default. Url path from the 
    tribune is ``remote/``.
XML
    Very fast, use the remote message render, descendant ordered on default. Url path from 
    the tribune is ``remote/xml/``.
CRAP XML
    The XML version *extended* to suit to old tribune application client. Actually the 
    only diff is the XML structure wich is indented. Url path from the tribune is 
    ``remote/xml/crap/``.
JSON
    Very *declarative*, use the web message render, descendant ordered on default. Url 
    path from the tribune is ``remote/json/``.

Url arguments
-------------

On backend URLs, you can set somes options in adding by adding URL arguments like : ::
    
    /remote/?channel=foo&limit=42&direction=asc&last_id=77

channel
    A string to specify the channel *slug* to use to limit the backend to fetch messages 
    only from the given channel. By default, when this argument is not specified, the 
    default channel is used. If the specified channel does not exist, the response return 
    a *Http404*.
limit
    An integer to specify how much message can be retrieved, this value cannot be higher 
    than the setting value ``TRIBUNE_MESSAGES_MAX_LIMIT``. Default value come from 
    setting ``TRIBUNE_MESSAGES_MAX_LIMIT`` if this option is not specified.
direction
    Message listing direction specify if the list should be ordered on ``id`` in 
    ascendant or descendant way. Value can be ``asc`` for ascendant or ``desc`` for 
    descendant. Each backend can have his own default direction.
last_id
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
    
    No matter what direction you specify in option, the results will stays identical.

Message post
************

From web interface
------------------

The actual web interface is really simple and don't implement yet a "rich interface" with 
Javascript, this is only a simple HTML form with the message list. The rich interface is 
planned to be implemented in last.

From remote client applications
-------------------------------

Remote clients can send a new message directly within a **POST** request and putting the 
content in a ``content`` argument. Validated messages return the last updated backend (from 
the *knowed* last id). Invalidated messages return an Http error (thus it's not 
implemented yet).

`Url arguments`_ options can be given for the POST request and they will be used for the returned 
backend in success case.

In fact, remote client applications should always give the 
``last_id`` option (taken from the last message they know just before sending the POST 
request) to receive only messages they didn't know (and not the whole backend).

Action commands
***************

Action commands can be passed in message content, generally this result in doing the 
action without saving a new message although some actions can push a message to save.

All action command must start with a ``/`` followed (without any separator) by the 
action name and then the action arguments if any. Unvalid action command will often 
result in saving the content as a new message.

Currently implemented actions
-----------------------------

Name
    This allow anonymous users to display a custom name instead of their *User-Agent* in 
    messages.
    
    Name saving is made by a special cookie, so if the user lost or delete his cookie, 
    he lost his custom name.
    
    Add new ua : ::
    
        /name My name is bond
    
    Remove the saved ua : ::
    
        /name
