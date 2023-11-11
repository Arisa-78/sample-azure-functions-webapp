import os
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)

# LINE Botに関するインスタンス作成
configuration = Configuration(access_token=os.getenv("LINEOA_CHANNEL_ACCESS_TOKEN",""))
handler = WebhookHandler(os.getenv("LINEOA_CHANNEL_SECRET",""))

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # おうむ返しをするので、入力されたテキスト(event.message.text)を返す
        res_data = TextMessage(text=event.message.text)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[res_data]
            )
        )