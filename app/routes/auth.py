from flask import Blueprint, request, render_template, make_response, redirect
import requests

from options import Options
from utils.auth_decorators import login_required, unauthenticated_required

auth_bp = Blueprint('auth', __name__, url_prefix='/')

@auth_bp.route('/login')
@unauthenticated_required
def login():
    return render_template('user/login.html', backend_url=Options.BACKEND_URL)

@auth_bp.route('/logout')
@login_required
def logout():
    requests.delete(f"{Options.INTERNAL_BACKEND_URL}/token", cookies=request.cookies.to_dict())

    resp = make_response(redirect("/"))

    resp.set_cookie("access_token_cookie", "", expires=0)
    resp.set_cookie("refresh_token_cookie", "", expires=0)

    return resp
