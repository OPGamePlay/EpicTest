import json
import requests
from datetime import datetime
from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def trigger_function():
    freeGames = getFreeGames()
    sent_webhook(freeGames)

    return 'Function triggered successfully!'


def sent_webhook(freeGames):
    embeds = []
    for freeGame in freeGames:
        dt = datetime.strptime(freeGame['expiryDate'], "%Y-%m-%dT%H:%M:%S.%fZ")

        embed = {
            "title": f"{freeGame['title']} 限時免費中 | Epic Games",
            "description": f"限時免費至{dt.date().year}年{dt.date().month}月{dt.date().day}日{dt.time().hour}:{str(dt.time().minute).zfill(2)} \n {freeGame['url']}",
            "color": 0xFFFFFF,  # Embed 的顏色（十進制 RGB 值）
            "image" : {
                "url": freeGame['thumbnail']
            }
        }
        embeds.append(embed)
    # Discord Webhook URL
    webhook_url = "https://discord.com/api/webhooks/1184844587181801522/5IVP1-VXOxNh7hV1upmxNqk7GPlpUU662pBCKBBg47mLWwVDU0q1OOaPddM3Omjov8qJ"

    # 構建要發送的消息內容
    message = {
        "username": "Epic Free Games",
        "avatar_url": "https://cdn2.unrealengine.com/Epic+Games+Node%2Fxlarge_whitetext_blackback_epiclogo_504x512_1529964470588-503x512-ac795e81c54b27aaa2e196456dd307bfe4ca3ca4.jpg",
        "embeds": embeds
    }

    # 將消息內容轉換為 JSON 格式
    payload = json.dumps(message)

    # 發送 HTTP POST 請求到 Webhook URL
    response = requests.post(webhook_url, data=payload, headers={"Content-Type": "application/json"})

    # 檢查請求是否成功
    if response.status_code == 204:
        print("Webhook message sent successfully!")
    else:
        print(f"Failed to send webhook message. Status code: {response.status_code}")

def getFreeGames():
    # 指定網頁的URL
    url = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-Hant&country=HK&allowCountries=HK"  # 替換為你要請求的網頁URL

    # 發送GET請求
    response = requests.get(url)

    # 檢查請求是否成功
    if response.status_code == 200:
        web_data = response.json()
        querys = web_data['data']['Catalog']['searchStore']['elements']
        freeGames = []
        for game in querys:
            try:
                promotions_s = game['promotions']['promotionalOffers']
                for promotions in promotions_s:
                    for promotion in promotions['promotionalOffers']:
                        if promotion['discountSetting']['discountPercentage'] == 0:
                            # thumbnail = (image['url'] for image in game['keyImages'] if image['type'] == "DieselStoreFrontWide")

                            for image in game['keyImages']:
                                if image['type'] == "DieselStoreFrontWide":
                                    thumbnail = image['url']
                            freeGame = {
                                "title": game['title'],
                                "description" : game['description'],
                                "startDate" : game['effectiveDate'],
                                "expiryDate" : game['expiryDate'],
                                "thumbnail" : thumbnail,
                                "url": "https://store.epicgames.com/zh-Hant/p/" + game['productSlug']
                            }
                            freeGames.append(freeGame)
                            
            except TypeError:
                continue
            except Exception as err:
                print(err)
        return freeGames

    else:
        print("請求失敗，狀態碼：" + str(response.status_code))




if __name__ == "__main__":
    app.run()
