import os

class Options:
    SECURED_ROUTES = ["/admin", "/user"]
    BACKEND_URL = f"{os.environ.get("HTTP_HOST","http://localhost:8081")}/api"
    INTERNAL_BACKEND_URL = f"{os.environ.get("INTERNAL_BACKEND_URL", "http://localhost:8081")}/api"
    UPLOAD_FOLDER = os.path.join('static', 'images/uploads')
    SECRET_KEY = os.environ.get("SECRET_KEY", "super secret key")