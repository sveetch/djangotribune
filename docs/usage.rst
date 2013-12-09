.. _Django internationalization system: https://docs.djangoproject.com/en/dev/topics/i18n/
.. _LastFM API: http://www.lastfm.fr/api/intro
.. _texttable: http://pypi.python.org/pypi/texttable/0.8.1
.. _crispy-forms-foundation: https://github.com/sveetch/crispy-forms-foundation
.. _South: http://south.readthedocs.org/en/latest/
.. _Foundation3: http://foundation.zurb.com/docs/v/3.2.5/

.. _intro_usage:

*****
Usage
*****

.. _message-posting-label:

Message board
=============

The tribune can either be used from the web interface or via remote client applications.

Just enter in, and type your message in the input box at the bottom of the list of messages. You can use shortcut 
buttons to add html tags to surround your current text selection in the input (or just add it if 
you didn't select text).

Also in your message you can insert smileys (commonly called *totoz*) from the smiley host 
(by default http://totoz.eu/). Smileys syntax is to surround the smiley key word with 
``[:keyname]`` like ``[:totoz]`` that will be replaced to a link to the image 
``http://totoz.eu/totoz.gif``. This image will be displayed when the mouse cursor hovers the 
link.

The default interface performs a periodical request on the remote backend to display any new message, 
so you don't have to reload the page to see new message. When the the periodical refresh is on progress 
you will see a sign in the input, if the server return a response error you will see a sign that will be 
hidden at the next refresh success response.

If your posted message is not validated, the input field will be displayed with red borders, the borders will 
be hidden just after a new validated post.

In fact, the only option you can manage is the *Active refresh* that you can disable to avoid any 
periodical request on the remote backend. But if you disable it and you post a new message, there will 
still be a *POST* request that will refresh the message list.

.. _action-commands-label:

Action commands
===============

Action commands can be passed to message content, generally this results in doing the 
action without saving a new message although some actions can push a message to save.

All action command must start with a ``/`` followed (without any separator) by the 
action name and then the action arguments if any. Invalid action commands will often 
result in saving the content as a new message.

**name**
    This allows anonymous users to display a custom name instead of their *User-Agent* in 
    messages.
    
    Name saving is made by a special cookie, so if the user loses or deletes his cookie, 
    he loses his custom name.
    
    Add new ua : ::
    
        /name My name is bond
    
    Remove the saved ua : ::
    
        /name
    
    Note that this name will only be directly visible for anonymous user, because 
    registered users have their username displayed, but the name (or user-agent) is 
    visible on mouse over their username. This behavior is only on HTML board, remote 
    clients have their own behaviors.
**lastfm**
    This command use the `LastFM API`_ 
    to automatically post a *musical instant* for the current 
    track played. This works only the **current** track played, not the last recent 
    track played.
    
    You should specify an *username* in argument within the action, it will be used as 
    the username account on LastFM from where to search the current track.
    
    Generally, you will do like this : ::
    
        /lastfm instant myname
    
    But if you are authenticated on the tribune and your username is the same as on your 
    LastFM account, you can do like this : ::
    
        /lastfm instant
    
    This will result in a message like this :
        
        **====> Moment Artist - Title <====**
**bak**
    Intended for users to manage their message filters, see :ref:`messagefiltering-system-label` 
    for a complete explanation.

    If you want to avoid displaying message from the registered user ``BadBoy``, you will do : ::
        
            /bak add author Badboy

    You want to avoid displaying all message containing a reference to ``http://perdu.com`` you will do : ::
            
            /bak set message *= http://perdu.com

    You want to avoid displaying message from all user with an user-agent from ``Mozilla`` : ::
        
            /bak set ua *= Mozilla

.. _discovery-label:

Discovery
=========

Discovery files describes the needed configuration to use a tribune with third client 
applications.

They are simple XML files for describe configuration to access to the remote backend and 
to post new message, plus some other options and parameters.

You can access them at location ``/discovery.config`` under the path of the tribune, 
so for the default tribune this is usually : ::

    /tribune/discovery.config

And for a channel with the slug name "foo", it will be : ::

    /tribune/foo/discovery.config
