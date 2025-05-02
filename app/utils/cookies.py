from flask import make_response, redirect
from http.cookies import SimpleCookie

def clone_cookies_from_response(url, request):
    resp = make_response(redirect(url))

    set_cookie_headers = request.headers.get('Set-Cookie')
    cookie = SimpleCookie()
    cookie.load(set_cookie_headers)

    for key, morsel in cookie.items():
        kwargs = {}
        if morsel['path']:
            kwargs['path'] = morsel['path']
        if morsel['domain']:
            kwargs['domain'] = morsel['domain']
        if morsel['secure']:
            kwargs['secure'] = True
        if morsel['httponly']:
            kwargs['httponly'] = True
        if morsel['expires']:
            kwargs['expires'] = morsel['expires']
        if morsel['samesite']:
            kwargs['samesite'] = morsel['samesite']

        resp.set_cookie(key, morsel.value, **kwargs)

    return resp
