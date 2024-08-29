import os

from flask import Flask, abort, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint, abort
from jwt import InvalidSignatureError
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from sqlalchemy.exc import SQLAlchemyError

from db import db

blp = Blueprint("Linebots", __name__, description="Operations on linebots")

line_bot_userid = LineBotApi(os.getenv("LINEBOT_UserID"))
# Channel Access Token
line_bot_api = LineBotApi(os.getenv("LINEBOT_ChannelAccessToken"))
# Channel Secret
handler = WebhookHandler(os.getenv("LINEBOT_ChannelSecret"))


@blp.route("/linebot/send")
class LinebotSend(MethodView):
    def post(self):
        try:
            line_bot_api.push_message(
                line_bot_userid, TextSendMessage(text="Hello World!!!")
            )
            return "OK"
        except:
            print("error")


# 監聽所有來自 /callback 的 Post Request
@blp.route("/linebot/callback")
class LinebotCallback(MethodView):
    def post(self):
        # get X-Line-Signature header value
        signature = request.headers["X-Line-Signature"]
        # get request body as text
        body = request.get_data(as_text=True)
        # app.logger.info("Request body: " + body)
        # handle webhook body
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)
        return "OK"


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)
