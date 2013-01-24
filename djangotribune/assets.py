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
            "css/djangotribune/frontend.css",
            filters='yui_css',
            output='css/djangotribune.min.css'
        ),
        'djangotribune_js': Bundle(
            "js/jquery/jquery.querystring.js",
            "js/jquery/jquery.cookies.2.2.0.js",
            "js/djangotribune/timer.js",
            "js/djangotribune/csrf.js",
            "js/djangotribune/main.js",
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
