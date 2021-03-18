from pyramid.settings import asbool


def admin_only_debugtoolbar(request):
    """
    Enable toolbar for authorized users only.
    Returns True when it should be enabled.
    """
    return request.is_authenticated


def includeme(config):
    if not asbool(config.get_settings().get("admin_debugtoolbar")):
        return
    print("Yep")
    config.add_settings(
        {
            "debugtoolbar.hosts": ["0.0.0.0/0", "::/0"],
            "debugtoolbar.intercept_exc": "display",
        }
    )
    config.include("pyramid_debugtoolbar", route_prefix="/admin")
    config.set_debugtoolbar_request_authorization(admin_only_debugtoolbar)
