import requests, os

from flask import Flask, request, jsonify
from uuid import uuid4
from werkzeug.utils import secure_filename

from options import Options
from utils.cookies import clone_cookies_from_response

from routes.admin import admin_bp
from routes.post  import post_bp
from routes.home  import home_bp
from routes.auth  import auth_bp


app = Flask(__name__)
app.secret_key = Options.SECRET_KEY

app.register_blueprint(admin_bp)
app.register_blueprint(post_bp)
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)

@app.before_request
def before_request():
    if "static" in request.url: return

    app.jinja_env.globals["backend_url"] = Options.BACKEND_URL
    user = requests.get(f"{Options.INTERNAL_BACKEND_URL}/user/me", cookies=request.cookies.to_dict())
    print(user.text)
    if user.status_code == 200:
        user=user.json()
        app.jinja_env.globals["user"] = user
    else:
        refresh_token = request.cookies.get("refresh_token_cookie")
        if refresh_token:
            # Aggiornamento access token
            new_access_token = requests.post(f"{Options.INTERNAL_BACKEND_URL}/token/refresh", cookies=request.cookies.to_dict())
            if new_access_token.status_code == 201:
                return clone_cookies_from_response(request.url, new_access_token)
        
        # caso in cui l'access token avesse avuto problemi
        
        app.jinja_env.globals["user"] = None

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

if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0", debug=True)