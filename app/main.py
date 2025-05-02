from flask import Flask, render_template, request, session, make_response, jsonify
from uuid import uuid4
from flask_jwt_extended import jwt_required
from http.cookies import SimpleCookie

from options import Options

import requests, os
#
from functools import wraps
from flask import  request, redirect, url_for

from werkzeug.utils import secure_filename
from urllib.parse import parse_qs, parse_qsl


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_logged = request.cookies.get("access_token_cookie") is not None

        if not is_logged:
            return redirect(url_for("home")) 
        return f(*args, **kwargs)
    return decorated_function

def unauthenticated_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_logged = request.cookies.get("access_token_cookie") is not None

        if is_logged:
            return redirect(url_for("home")) 
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = Options.SECRET_KEY

def clone_cookies_from_response(user):
    resp = make_response(redirect("/"))

    set_cookie_headers = user.headers.get('Set-Cookie')
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

@app.before_request
def update_token():
    access_token = request.cookies.get("access_token_cookie")
    refresh_token = request.cookies.get("refresh_token_cookie")

    # Se non c'è il refresh token, non possiamo fare nulla
    if not refresh_token:
        return

    # Se non c'è access token, oppure si vuole forzare il refresh ogni volta
    if not access_token:
        refresh_req = requests.post(
            f"{Options.INTERNAL_BACKEND_URL}/token/refresh",
            cookies=request.cookies.to_dict()
        )

        if refresh_req.status_code == 200 and refresh_req.cookies.get("access_token_cookie"):
            return clone_cookies_from_response(refresh_req)

        # Se il refresh fallisce
        if refresh_req.status_code == 401 and "revoked" in refresh_req.json().get("msg", "").lower():
            resp = make_response(redirect("/"))
            resp.set_cookie("access_token_cookie", "", expires=0)
            resp.set_cookie("refresh_token_cookie", "", expires=0)
            return resp

@app.route('/')
def home():
    latest_posts = requests.get(f"{Options.INTERNAL_BACKEND_URL}/post/", json={
        "sort_by" : "created_at",
        "sort_order" : "desc",
        "per_page" : 4
    })

    if latest_posts.status_code == 200: 
        latest_posts = latest_posts.json()
    else: latest_posts = {"result" : []}

    trending_posts = requests.get(f"{Options.INTERNAL_BACKEND_URL}/post/", json={
        "sort_by" : "comments",
        "sort_order" : "desc",
        "per_page" : 6
    })

    if trending_posts.status_code == 200: 
        trending_posts = trending_posts.json()
    else: trending_posts = {"result" : []}

    args = {
        "trending_posts" : trending_posts["result"], 
        "latest_posts" : latest_posts["result"],
        "logged" : False
    }
    
    user = requests.get(f"{Options.INTERNAL_BACKEND_URL}/user/me", cookies=request.cookies.to_dict())
    if user.status_code == 200:
        args["logged"] = True
        user=user.json()
        args["user"] = user

    return render_template('home.html', **args)

@app.route('/login')
@unauthenticated_required
def login():
    return render_template('login.html', backend_url=Options.BACKEND_URL)

@app.route('/logout')
@login_required
def logout():
    requests.delete(f"{Options.INTERNAL_BACKEND_URL}/token/", cookies=request.cookies.to_dict())

    resp = make_response(redirect("/"))

    resp.set_cookie("access_token_cookie", "", expires=0)
    resp.set_cookie("refresh_token_cookie", "", expires=0)

    return resp

@app.route("/posts", defaults={'page': 1}, methods=["GET"])
@app.route("/posts/<int:page>", methods=["GET"])
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
        **qs
    }

    posts = requests.get(f"{Options.INTERNAL_BACKEND_URL}/post/", json=body)

    if posts.status_code != 200:
        return jsonify(success=False, message="Cannot fetch posts."), 400
    
    posts = posts.json()

    trending_posts = requests.get(f"{Options.INTERNAL_BACKEND_URL}/post/", json={
        "sort_by" : "comments",
        "sort_order" : "desc",
        "per_page" : 4
    })

    if trending_posts.status_code == 200: 
        trending_posts = trending_posts.json()["result"]
    else: trending_posts = []

    categories = requests.get(f"{Options.INTERNAL_BACKEND_URL}/category")
    if categories.status_code == 200: 
        categories = categories.json()["result"]
    else: categories = []

    tags = requests.get(f"{Options.INTERNAL_BACKEND_URL}/tag", json={
        "sort_by" : "posts"
    })
    if tags.status_code == 200: 
        tags = tags.json()["result"]
    else: tags = []

    params = {
        "posts": posts["result"], 
        "trending_posts": trending_posts, 
        "total_pages": posts["total_pages"], 
        "actual_page": page, 
        "backend_url": Options.BACKEND_URL, 
        "categories": categories[:10],
        "tags" : tags[:20]
    }

    user = requests.get(f"{Options.INTERNAL_BACKEND_URL}/user/me", cookies=request.cookies.to_dict())
    if user.status_code == 200:
        params["logged"] = True
        user=user.json()
        params["user"] = user

    return render_template('articles.html', **params)

@app.route("/post/<int:post_id>", methods=["GET"])
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

    data = {**data, **check_authentication()}

    return render_template("article.user.html", **data)

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    data = {}

    for resource in ["post", "tag", "user", "category"]:
        resp = requests.get(f"{Options.INTERNAL_BACKEND_URL}/{resource}/", cookies=request.cookies.to_dict())
        if resp.status_code != 200: 
            data[resource] = {"result" : [], "total_pages" : 1, "page" : 1, "total_count" : 0}
            continue

        data[resource] = resp.json()["result"]
    
    data = {**data, **check_authentication()}

    return render_template("admin/dashboard.admin.html", **data)

def check_authentication():
    _dict = {}

    user = requests.get(f"{Options.INTERNAL_BACKEND_URL}/user/me", cookies=request.cookies.to_dict())
    if user.status_code == 200:
        _dict["logged"] = True
        user=user.json()
        _dict["user"] = user
    
    return _dict

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Nessun file fornito'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'Nome file mancante'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(Options.UPLOAD_FOLDER, str(uuid4())+"_"+filename)
    file.save(filepath)
    return jsonify({'message': 'Immagine salvata con successo', 'path': "/"+filepath}), 200

@app.route("/admin/categories", defaults={'page': 1}, methods=["GET"])
@app.route("/admin/categories/<int:page>", methods=["GET"])
@login_required
def admin_categories(page):
    qs = parse_qs(request.query_string.decode())
    print(qs)
    data = {}
    reqs = {
        "post" : {
            "per_page" : 10,
            "page" : page,
            "include_delete" : True,
            "show_all" : True
        }, 
        "user" : {}, 
        "category" : {**qs}
    }

    for key, val in reqs["category"].items():
        if key in ["name"]:
            reqs["category"][key] = val[0]
        
    
    for resource, json in reqs.items():
        resp = requests.get(f"{Options.INTERNAL_BACKEND_URL}/{resource}/", cookies=request.cookies.to_dict(), json=json)
        if resp.status_code != 200: 
            data[resource] = {"result" : [], "total_pages" : 1, "page" : 1, "total_count" : 0}
            continue

        data[resource] = resp.json()

    if page > data["category"]["total_pages"] and page > 1:
        return redirect("/admin/categories")
    
    data["active_cat"] = len(list(filter(lambda x: len(x["posts"])>0, data["category"]["result"])))
    data["inactive_cat"] = len(list(filter(lambda x: len(x["posts"])==0, data["category"]["result"])))

    data = {**data, **check_authentication(), "backend_url" : Options.BACKEND_URL}

    return render_template("admin/category.admin.html", **data)


@app.route("/admin/posts", defaults={'page': 1}, methods=["GET"])
@app.route("/admin/posts/<int:page>", methods=["GET"])
@login_required
def admin_post(page):
    qs = parse_qs(request.query_string.decode())
    print(qs)

    data = {}
    reqs = {"post" : {
        "per_page" : 10,
        "page" : page,
        "include_deleted" : True,
        **qs
    }, "tag" : {}, "user" : {}, "category" : {}}

    for key, val in reqs["post"].items():
        if key in ["category", "status", "text"]:
            reqs["post"][key] = val[0]

    for resource, json in reqs.items():
        resp = requests.get(f"{Options.INTERNAL_BACKEND_URL}/{resource}/", cookies=request.cookies.to_dict(), json=json)
        if resp.status_code != 200: 
            data[resource] = {"result" : [], "total_pages" : 1, "page" : 1, "total_count" : 0}
            continue

        data[resource] = resp.json()
    
    print(data)

    data = {**data, **check_authentication(), "status" : ["review", "public", "archived"], "backend_url":Options.BACKEND_URL}

    if "post" in data.keys() and page > data["post"]["total_pages"] and page > 1:
        return redirect("/admin/posts")

    return render_template("admin/articles.admin.html", **data)

if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")