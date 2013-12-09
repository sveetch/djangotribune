.. _Django internationalization system: https://docs.djangoproject.com/en/dev/topics/i18n/
.. _LastFM API: http://www.lastfm.fr/api/intro
.. _texttable: http://pypi.python.org/pypi/texttable/0.8.1
.. _crispy-forms-foundation: https://github.com/sveetch/crispy-forms-foundation
.. _South: http://south.readthedocs.org/en/latest/
.. _Foundation3: http://foundation.zurb.com/docs/v/3.2.5/

.. _intro_install:

*******
Install
*******

First, register the app in your project settings like this : ::

    INSTALLED_APPS = (
        ...
        'djangotribune',
        ...
    )

Then after you should register the app urls in your project ``urls.py`` : ::

    url(r'^tribune/', include('djangotribune.urls')),

Of course, you can use another mounting directory than the default ``tribune/`` or even 
use your own app urls, look at the provided ``djangotribune.urls`` to see what you have 
to map.

And finally don't forget to do the Django's *syncdb command* to synchronize models in your 
database.

If needed, you can change some `Application settings`_ in your settings file.

.. NOTE:: The recommended database engine is **PostgreSQL**. With SQLite you could have 
          problems because the application makes usage of case-insensitive matching 
          notably in :ref:`messagefiltering-system-label`.

Project templates
=================

A simple note about templates, djangotribune templates use a base template ``djangotribune/base.html`` to include some common HTML to add contents to your layout, and all other templates extend it to insert theirs.

This base template is made to extend a ``skeleton.html`` template that should be the root base of your project layout. Therefore, if you don't use a base template or use it with another name, just override ``djangotribune/base.html`` in project templates to fit it right within your project.

Also, note that templates have been written for `Foundation3`_ so if you don't use it, it should not really matter to you as this is only HTML, you can style it yourself or at least change the templates to accomodate to your needed HTML structure. And if you want to use `Foundation3`_, just add its required assets to your project, but for the url archives form you will have to patch some Javascript because of an added feature to use input checkbox inside button dropdown.

Here is a patch file for the Javascript file for buttons : ::

    diff --git a/project/webapp_statics/js/foundation/jquery.foundation.buttons.js b/project/webapp_statics/js/foundation/jquery.foundation.buttons.js
    --- a/project/webapp_statics/js/foundation/jquery.foundation.buttons.js
    +++ b/project/webapp_statics/js/foundation/jquery.foundation.buttons.js
    @@ -33,6 +33,12 @@
            button = $el.closest('.button.dropdown'),
            dropdown = $('> ul', button);
            
    +        // let ".no-reset-click" elements to act by default to prevent dropdown closing
    +        if($(e.target).hasClass('no-reset-click')){
    +          e.stopPropagation();
    +          return true;
    +        }
    + 

And another patch file for your ``app.js`` : ::

    diff --git a/project/webapp_statics/js/foundation/app.js b/project/webapp_statics/js/foundation/app.js
    --- a/project/webapp_statics/js/foundation/app.js
    +++ b/project/webapp_statics/js/foundation/app.js
    @@ -11,6 +11,15 @@ function column_equalizer(){
    }
    
    $(document).ready(function() {
    +    // Automatically add "no-reset-click" class on direct input parent label to 
    +    // follow their natural behavior (to propagate the click to their input child, 
    +    // usually only for radio or checkbox)
    +    $("form .button.dropdown .no-reset-click").each(function(index) {
    +        if($(this).parent().prop('nodeName')=='LABEL'){
    +            $(this).parent().addClass('no-reset-click');
    +        }
    +    });
    +    
        //$.fn.foundationAlerts           ? $doc.foundationAlerts() : null;
        $.fn.foundationButtons          ? $doc.foundationButtons() : null;
        //$.fn.foundationAccordion        ? $doc.foundationAccordion() : null;

Updates
=======

Since 0.6.6 version, `South`_ support is implemented, so for future updates you will have to use something like : ::

    ./manage.py migrate djangotribune

And model changes will be automatically applied to your database.

.. _application-settings-label:

Application settings
====================

All default app settings are located in the ``settings_local.py`` file of ``djangotribune``, you can modify them in your 
project settings.

.. NOTE:: All app settings are overwritten if present in your project settings with the exception of 
          dict variables. This is to be remembered when you want to add a new entry in a list variable, you will have to 
          copy the default version in your settings with the new entry otherwise default variable will be lost.

**TRIBUNE_LOCKED**
    When set to ``True`` all anonymous users will be rejected from any request on remote 
    views, post views and board views, only registred users will continue to access to 
    these views. 
    
    By default this is set to ``False`` so anonymous and registred users have full access 
    to any *public views*.
**TRIBUNE_MESSAGES_DEFAULT_LIMIT**
    Default message limit to display in backend. 
    
    Requires an integer, by default this is set to 50.
**TRIBUNE_MESSAGES_MAX_LIMIT**
    The maximum value allowed for the message limit option. Limit option used beyond this 
    will be set to this maximum value. 
    
    Requires an integer, by default this is set to 100.
**TRIBUNE_MESSAGES_POST_MAX_LENGTH**
    Maximum length (in characters) for the content message. 
    
    Requires an integer, by default this is set to 500. You have no real limit on this 
    value because this is stored in full text field without limit.
**TRIBUNE_SMILEYS_URL**
    `Template string <http://docs.python.org/library/string.html#formatstrings>`_ for 
    smileys URL, this is where you can set the wanted smiley host. By default this is set to : ::
        
        http://totoz.eu/{0}.gif
        
    So the host will be *totoz.eu* that is the *safe for work* version, if you prefer the *non safe for work* use ``nsfw.totoz.eu`` instead.
**TRIBUNE_TITLES**
    List of titles randomly displayed on tribune boards. 
    
    The default one allready contains many titles.
**TRIBUNE_LASTFM_API_URL**
    The URL to use to request the `LastFM API`_ used within ``lastfm`` action command.
**TRIBUNE_LASTFM_API_KEY**
    The Application key to use for on requests made to `LastFM API`_.
**TRIBUNE_INTERFACE_REFRESH_SHIFTING**
    The default time in milli-seconds between each backend refresh request on the interface.
**TRIBUNE_SHOW_TRUNCATED_URL**
    A boolean to define (if ``True``) if URLs should be displayed as a truncated url of 100 characters maximum. Default behavior (when ``False`` or not in your settings) is to display them like ``[url]`` if it does not match any regex in the dictionnary ``parser.URL_SUBSTITUTION``.

Internationalization and localization
=====================================

This application make usage of the `Django internationalization system`_, see the Django documentation about this if 
you want to add a new language translation.
