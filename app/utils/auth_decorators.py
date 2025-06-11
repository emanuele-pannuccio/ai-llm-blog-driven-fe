from functools import wraps
from flask import request
from flask import  request, redirect, url_for
import requests

from options import Options

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = requests.get(f"{Options.INTERNAL_BACKEND_URL}/user/me", cookies=request.cookies.to_dict())
        if user.status_code != 200:
            return redirect("/") 
        return f(*args, **kwargs)
    return decorated_function

def unauthenticated_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = requests.get(f"{Options.INTERNAL_BACKEND_URL}/user/me", cookies=request.cookies.to_dict())
        if user.status_code == 200:
            return redirect("/") 
        return f(*args, **kwargs)
    return decorated_function