from flask import Blueprint, request, render_template, jsonify
from urllib.parse import parse_qs
import requests

from options import Options

post_bp = Blueprint('post', __name__, url_prefix='/')

@post_bp.route("/posts", defaults={'page': 1}, methods=["GET"])
@post_bp.route("/posts/<int:page>", methods=["GET"])
def posts(page):
    qs = parse_qs(request.query_string.decode())
    
    if "text" in qs.keys():
        qs["text"] = qs["text"][0]

    if "category" in qs.keys():
        qs["category"] = qs["category"][0]

    body = {
        "sort_by" : "created_at",
        "sort_order" : "desc",
        "per_page" : 6,
        "page" : page,
        "show_all" : True,
        **qs
    }

    posts = requests.get(f"{Options.INTERNAL_BACKEND_URL}/post", json=body, cookies=request.cookies.to_dict())

    if posts.status_code != 200:
        return jsonify(success=False, message="Cannot fetch posts."), 400
    
    posts = posts.json()

    trending_posts = requests.get(f"{Options.INTERNAL_BACKEND_URL}/post", json={
        "sort_by" : "comments",
        "sort_order" : "desc",
        "per_page" : 4
    }, cookies=request.cookies.to_dict())

    if trending_posts.status_code == 200: 
        trending_posts = trending_posts.json()["result"]
    else: trending_posts = []

    categories = requests.get(f"{Options.INTERNAL_BACKEND_URL}/category", cookies=request.cookies.to_dict())
    if categories.status_code == 200: 
        categories = categories.json()["result"]
    else: categories = []

    tags = requests.get(f"{Options.INTERNAL_BACKEND_URL}/tag", json={
        "sort_by" : "posts"
    }, cookies=request.cookies.to_dict())
    if tags.status_code == 200: 
        tags = tags.json()["result"]
    else: tags = []

    params = {
        "posts": posts["result"], 
        "trending_posts": trending_posts, 
        "total_pages": posts["total_pages"], 
        "actual_page": page, 
        "categories": categories[:10],
        "tags" : tags[:20]
    }

    return render_template('user/articles.html', **params)

@post_bp.route("/post/<int:post_id>", methods=["GET"])
def post(post_id):
    resources = {
        "post" : {
            "url" : f"post/{post_id}"
        },
        "tag" : {
            "body" : {"sort_by" : "posts"},
            "url" : "tag"
        },
        "popular_tags" : {
            "body" : {"sort_by" : "posts"},
            "url" : "tag",
        }
    }

    data = {}
    
    for variable_name, req in resources.items():
        resp = requests.get("{}/{}".format(Options.INTERNAL_BACKEND_URL, req["url"]), json=req["body"] if "body" in req.keys() else {}, cookies=request.cookies.to_dict())
        response_json = resp.json()
        if resp.status_code != 200:
            return jsonify(success=False, error=response_json)
        data[variable_name] = response_json

    return render_template("user/article.user.html", **data)
