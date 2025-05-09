from flask import Blueprint, request, render_template, make_response, redirect
from urllib.parse import parse_qs
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from options import Options
from utils.auth_decorators import login_required, unauthenticated_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route("/dashboard")
@login_required
def admin_dashboard():
    data = {}
    reqs = {"post" : {
        "per_page" : 10,
        "include_deleted" : True,
        "show_all" : True
    }, "tag" : {}, "user" : {}, "category" : {}}

    for resource, json in reqs.items():
        resp = requests.get(f"{Options.INTERNAL_BACKEND_URL}/{resource}", cookies=request.cookies.to_dict(), json=json)
        if resp.status_code != 200: 
            data[resource] = {"result" : [], "total_pages" : 1, "page" : 1, "total_count" : 0}
            continue

        data[resource] = resp.json()
    
    for post in data["post"]["result"]:
        post["created_at_dt"] = datetime.strptime(post["created_at"], "%d/%m/%Y %H:%M").timestamp() if post["created_at"] else None

    data = {**data, "status" : ["review", "public", "archived"], "now": datetime.now(ZoneInfo("Europe/Rome")).timestamp()}
    
    return render_template("admin/dashboard.admin.html", **data)

@admin_bp.route("/categories", defaults={'page': 1}, methods=["GET"])
@admin_bp.route("/categories/<int:page>", methods=["GET"])
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
        resp = requests.get(f"{Options.INTERNAL_BACKEND_URL}/{resource}", cookies=request.cookies.to_dict(), json=json)
        if resp.status_code != 200: 
            data[resource] = {"result" : [], "total_pages" : 1, "page" : 1, "total_count" : 0}
            continue

        data[resource] = resp.json()

    if page > data["category"]["total_pages"] and page > 1:
        return redirect("/admin/categories")
    
    data["active_cat"] = len(list(filter(lambda x: len(x["posts"])>0, data["category"]["result"])))
    data["inactive_cat"] = len(list(filter(lambda x: len(x["posts"])==0, data["category"]["result"])))

    return render_template("admin/category.admin.html", **data)


@admin_bp.route("/posts", defaults={'page': 1}, methods=["GET"])
@admin_bp.route("/posts/<int:page>", methods=["GET"])
@login_required
def admin_post(page):
    qs = parse_qs(request.query_string.decode())
    print(qs)

    data = {}
    reqs = {"post" : {
        "per_page" : 10,
        "page" : page,
        "show_all" : True,
        **qs
    }, "tag" : {}, "user" : {}, "category" : {}}

    for key, val in reqs["post"].items():
        if key in ["category", "status", "text"]:
            reqs["post"][key] = val[0]

    for resource, json in reqs.items():
        resp = requests.get(f"{Options.INTERNAL_BACKEND_URL}/{resource}", cookies=request.cookies.to_dict(), json=json)
        if resp.status_code != 200: 
            data[resource] = {"result" : [], "total_pages" : 1, "page" : 1, "total_count" : 0}
            continue

        data[resource] = resp.json()
    
    data = {**data, "status" : ["review", "public", "archived"], "now": datetime.now(ZoneInfo("Europe/Rome")).timestamp()}

    for post in data["post"]["result"]:
        post["created_at_dt"] = datetime.strptime(post["created_at"], "%d/%m/%Y %H:%M").timestamp() if post["created_at"] else None

    if "post" in data.keys() and page > data["post"]["total_pages"] and page > 1:
        return redirect("/admin/posts")

    return render_template("admin/articles.admin.html", **data)