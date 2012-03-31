==============
Django-tribune
==============

Introduction
============

This Django app is a *chat-like application* with some aspects from *IRC* but with a 
strong usage of message clocks.

**Message clocks** are always displayed and used in message to reference anwser or 
relation with other messages.

Currently in alpha version, this include :

* An awesome project title;
* Data models;
* Queryset filtering API for "standard" tribune behavior;
* All stuff for base remote views and remote views for plain-text, JSON and XML;
* ...
* Profit !

Usage
=====

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
    
    /remote/?limit=42&direction=asc&last_id=77

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
    