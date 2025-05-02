from flask import Blueprint, request, render_template
import requests

from options import Options

home_bp = Blueprint('home', __name__, url_prefix='/')


@home_bp.route('', methods=['GET'])
def home():
    latest_posts = requests.get(f"{Options.INTERNAL_BACKEND_URL}/post", json={
        "sort_by" : "created_at",
        "sort_order" : "desc",
        "per_page" : 4
    }, cookies=request.cookies.to_dict())

    if latest_posts.status_code == 200: 
        latest_posts = latest_posts.json()
    else: latest_posts = {"result" : []}

    trending_posts = requests.get(f"{Options.INTERNAL_BACKEND_URL}/post", json={
        "sort_by" : "comments",
        "sort_order" : "desc",
        "per_page" : 6
    }, cookies=request.cookies.to_dict())

    if trending_posts.status_code == 200: 
        trending_posts = trending_posts.json()
    else: trending_posts = {"result" : []}

    args = {
        "trending_posts" : trending_posts["result"], 
        "latest_posts" : latest_posts["result"],
        "logged" : False
    }
    
    return render_template('user/home.html', **args)
