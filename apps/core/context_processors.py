def site_settings(request):
    """Inject global site context into every template."""
    return {
        "SITE_NAME": "TaskFlow AI",
        "SITE_VERSION": "1.0.0",
    }
