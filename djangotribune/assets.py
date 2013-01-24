"""
Asset bundles to use with django-assets
"""
try:
    from django_assets import Bundle, register
except ImportError:
    DJANGO_ASSETS_INSTALLED = False
else:
    DJANGO_ASSETS_INSTALLED = True

    AVALAIBLE_BUNDLES = {
        'djangotribune_css': Bundle(
            "djangotribune/djangotribune.css",
            filters='yui_css',
            output='css/djangotribune.min.css'
        ),
        'djangotribune_js': Bundle(
            "jquery/plugins/jquery.querystring.js",
            "jquery/plugins/jquery.cookies.2.2.0.min.js",
            "djangotribune/timer.js",
            "djangotribune/csrf.js",
            "djangotribune/djangotribune.js",
            filters='yui_js',
            output='js/djangotribune.min.js'
        ),
    }

    ENABLED_BUNDLES = (
        'djangotribune_css',
        'djangotribune_js',
    )

    for item in ENABLED_BUNDLES:
        register(item, AVALAIBLE_BUNDLES[item])
