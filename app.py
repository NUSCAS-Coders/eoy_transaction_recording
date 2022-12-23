from datetime import datetime, timedelta, timezone
from flask import Flask, send_from_directory, render_template
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
import os
from flask_cors import CORS

from flask_jwt_extended import JWTManager, get_jwt
from api.auth.controller import auth_api
from api.user.controller import user_api
from api.user.service import update_artists_info
from api.post.controller import post_api
from api.account.controller import account_api

from api.auth import service as auth_service
from config.db import config_db


if __name__ == "__main__":

    load_dotenv()
    app = Flask(
        __name__,
    )
    cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }})

    app.config['CORS_HEADERS'] = 'Content-Type'
    # config_db(app)
    # jwt = JWTManager(app)

    # app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    # app.config["JWT_TOKEN_LOCATION"] = ["headers"]

    # @app.after_request
    # def refresh_expiring_jwts(response):
        # print("hii")
        # return auth_service.refresh_jwt_token(response)

    # Registering controllers
    app.register_blueprint(auth_api, url_prefix="/auth")
    app.register_blueprint(user_api, url_prefix="/user")
    app.register_blueprint(post_api, url_prefix="/post")
    app.register_blueprint(account_api, url_prefix="/account")

    @app.route("/", methods=["GET"])
    def serve_home_page():
        return render_template('index.html')

    update_artists_info('W')

    app.run(port=int(os.getenv("PORT")), host=os.getenv("HOST"), debug=True)
