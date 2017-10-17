from urllib.parse import urlparse, urljoin

from flask import redirect, request, url_for


def redirect_back(endpoint, **values):
    """Helper function to redirect to 'next' URL if it exists.
    Otherwise, redirect to an endpoint."""
    target = request.args.get('next', 0, type=str)
    if not target or not is_safe(target):
        target = url_for(endpoint, **values)
    return redirect(target)


def is_safe(url):
    """Is the URL safe to redirect to?"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, url))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def str2bool(string):
    if type(string) == bool:
        return string
    return string.lower() == 'true'
