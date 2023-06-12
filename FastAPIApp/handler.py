import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage

# LINE Botに関するインスタンス作成
line_bot_api = LineBotApi(os.environ["LINEOA_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINEOA_CHANNEL_SECRET"])

@handler.add(MessageEvent)
def handle_message(event):
    res_data = TextMessage(text="メッセージを受け取りました")
    line_bot_api.reply_message(event.reply_token, res_data)