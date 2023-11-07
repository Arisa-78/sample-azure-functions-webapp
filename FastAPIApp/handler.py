import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage

# LINE Botに関するインスタンス作成
line_bot_api = LineBotApi(os.getenv("LINEOA_CHANNEL_ACCESS_TOKEN",""))
handler = WebhookHandler(os.getenv("LINEOA_CHANNEL_SECRET",""))

@handler.add(MessageEvent)
def handle_message(event):
    # Message typeが"text"のとき
    if event.message.type == "text":
        # おうむ返しをするので、入力されたテキスト(event.message.text)を返す
        res_data = TextMessage(text=event.message.text)
        line_bot_api.reply_message(event.reply_token, res_data)