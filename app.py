from dotenv import load_dotenv

load_dotenv()
# line_bot_api = LineBotApi(os.getenv("LINEBOT_ChannelAccessToken"))
# line_bot_userid = os.getenv("LINEBOT_UserID")
# line_bot_api.push_message(line_bot_userid, TextSendMessage(text="Hello World!!!"))
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_smorest import Api
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import models
from blocklist import BLOCKLIST
from db import db
from resources.accessment import GetAccessment
from resources.accessment import blp as Accessmentprint
from resources.item import blp as ItemBlueprint
from resources.linebots import blp as LinebotBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

# apscheduler先用local不要用docker測試
# wait to do...apscheduler, it seams work, maybe docker is too slow
# selenium.common.exceptions.WebDriverException: Message: Service /root/.cache/selenium/chromedriver/linux64/128.0.6613.137/chromedriver unexpectedly exited. Status code was: 127
# https://www.youtube.com/watch?v=b49Y3NGJX68


def create_app(db_url=None):
    app = Flask(__name__)
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    scheduler = BlockingScheduler()

    def job():
        GetAccessment()

    scheduler.add_job(job, "interval", seconds=60)

    @app.teardown_appcontext
    def stop_scheduler(exception=None):
        scheduler.shutdown()

    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)
    app.config["JWT_SECRET_KEY"] = "770A8A65DA156D24EE2A093277530142"
    jwt = JWTManager(app)

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # TODO: Read from a config file instead of hard-coding
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    with app.app_context():
        #     db.create_all() # replaced by Flask_Migrate, or using it when use SQLAlchemy
        scheduler.start()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(LinebotBlueprint)
    api.register_blueprint(Accessmentprint)

    return app


create_app()
