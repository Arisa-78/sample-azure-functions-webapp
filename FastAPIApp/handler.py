import os
import re
import httpx
import xmltodict
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    Message,
    TextMessage,
    ImageMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)

# LINE Botに関するインスタンス作成
configuration = Configuration(access_token=os.getenv("LINEOA_CHANNEL_ACCESS_TOKEN",""))
handler = WebhookHandler(os.getenv("LINEOA_CHANNEL_SECRET",""))

# 天気予報をリクエストしているメッセージの解析
def parseWeatherCommand(input: str):
    result = re.findall(r'^(.*)の天気', input)
    if len(result) > 0:
        return True, result[0]
    else:
        return False, ""

# 猫画像をリクエストしているメッセージの解析
def parseCatCommand(input: str):
    result = re.findall(r'^猫(\d{3})', input)
    if len(result) > 0:
        return True, result[0]
    else:
        return False, ""

# 都市名から都市IDを検索
def searchCityID(targetCity: str) -> (str, str):
    # エリア情報の取得
    areaResp = httpx.get("https://weather.tsukumijima.net/primary_area.xml")
    if areaResp.status_code != 200:
        raise HTTPException(status_code=500, detail="failed to get an area xml")
    try:
        # XMLを解析して、dictデータに変換
        area = xmltodict.parse(areaResp.text)
        # エリア情報から該当する都市IDを取得
        cityCode = ""
        for pref in area['rss']['channel']['ldWeather:source']['pref']:
            cityList = pref['city']
            if type(cityList) == list:
                for city in cityList:
                    if city['@title'] == targetCity:
                        return city['@id'], None
            else:
                if cityList['@title'] == targetCity:
                    return cityList['@id'], None
    except Exception as e:
        return "", "exception:{0}".format(str(e))
    # 見つからなかったら空文字を返す
    return "", "Not found"

# 天気予報の応答メッセージを作成
def createReplyForecastMessage(targetCity: str) -> Message:
    # 返信メッセージの作成
    replyText = ""
    ## 都市名から都市IDに変換
    ## 都市IDを使って天気予報情報を取得
    ##   - description > bodyText　から天気概況を取得して返信メッセージとする
    res_data = TextMessage(text=replyText)
    return res_data

# 猫画像が取得できるか確認
def validateStatusCodeForCat(status_code: str) -> bool:
    valid_status_codes = [
        100, 101, 102, 103,
        200, 201, 202, 203, 204, 206, 207,
        300, 301, 302, 303, 304, 305, 307, 308,
        400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418,
        420, 421, 422, 423, 424, 425, 426, 428, 429, 431, 444, 450, 451, 497, 498, 499,
        500, 501, 502, 503, 504, 506, 507, 508, 509, 510, 511, 521, 522, 523, 525, 530, 599,
    ]
    return int(status_code) in valid_status_codes

# 猫画像の応答メッセージを作成
def createReplyCatImageMessage(status_code: str) -> Message:
    # 猫画像が取得できるか確認(status_codeの確認)
    # 取得できるならURLの文字列を作成し、ImageMessageを作って返す
    # 取得できない場合はエラーの旨のTextMessageを作って返す
    pass

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        res_data = None
        # 天気予報
        if (result := parseWeatherCommand(event.message.text))[0]:
            # 天気予報の回答を生成
            res_data = createReplyForecastMessage(result[1])
        # 猫画像
        if (result := parseCatCommand(event.message.text))[0]:
            # 猫画像の回答を生成
            res_data = createReplyCatImageMessage(result[1])
        
        if res_data != None:
            # Replyメッセージの送信
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[res_data]
                )
            )