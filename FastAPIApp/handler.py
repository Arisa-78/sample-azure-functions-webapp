import os
import re
import httpx
import xmltodict
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage

# LINE Botに関するインスタンス作成
line_bot_api = LineBotApi(os.getenv("LINEOA_CHANNEL_ACCESS_TOKEN",""))
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
def createReplyForecastMessage(targetCity: str) -> TextSendMessage:
    # 返信メッセージの作成
    replyText = ""
    cityCode, errorText = searchCityID(targetCity)
    if cityCode != "":
        # 取得した都市IDを使って、天気予報を取得
        resp = httpx.get("https://weather.tsukumijima.net/api/forecast/city/{0}".format(cityCode))
        if resp.status_code == 200:
            result = resp.json()
            try:
                replyText = result["description"]["bodyText"]   # TextMessageは改行はそのまま表示に反映されるので変換せずに渡す
            except KeyError:    # description > bodyTextが見つからなかった場合
                replyText = "天気予報を取得に失敗しました(データ構造エラー)"
        else:   # description > bodyTextが見つからなかった場合
            replyText = "天気予報を取得に失敗しました(通信エラー)"
    else:   # エリア情報から都市名が見つからなかった場合
        replyText = "指定した都市名({0})が見つかりませんでした - error:{1}".format(targetCity, errorText)
    res_data = TextSendMessage(text=replyText)
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
def createReplyCatImageMessage(status_code: str) -> MessageEvent:
    # 猫画像が取得できるか確認
    if validateStatusCodeForCat(status_code):
        # URLを作成
        catImageURL = "https://http.cat/{0}.jpg".format(status_code)
        # イメージメッセージを返す
        return ImageSendMessage(original_content_url=catImageURL, preview_image_url=catImageURL)
    else:
        # 猫画像が見つからないので、エラーのメッセージを返す
        return TextSendMessage(text="猫画像が見つかりませんでした-code:{0}".format(status_code))

@handler.add(MessageEvent)
def handle_message(event):
    # Message typeが"text"のとき
    if event.message.type == "text":
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
            line_bot_api.reply_message(event.reply_token, res_data)