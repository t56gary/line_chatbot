# step1 引用套件
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import json
from linebot.models import RichMenu
import requests

# step2 伺服器準備
app = Flask(__name__)

'''
讀取安全檔案內的字串，以供後續程式碼調用
'''
secretFileContentJson=json.load(open("material/line_secret_key",'r',encoding="utf-8"))
server_url=secretFileContentJson.get("server_url")
#透過line_secret_key設定檔內的chanel_acess_token創建linebotapi客戶端,line_bot_api
line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))
handler = WebhookHandler(secretFileContentJson.get("secret_key"))



# 讀取設定檔
'''
菜單設定檔

    設定圖面大小、按鍵名與功能

'''
menuRawData='''
{
  "size": {
    "width": 2500,
    "height": 1686
  },
  "selected": true,
  "name": "圖文選單",
  "chatBarText": "查看更多資訊",
  "areas": [
    {
      "bounds": {
        "x": 0,
        "y": 0,
        "width": 2500,
        "height": 847
      },
      "action": {
        "type": "message",
        "text": "我想訂餐"
      }
    },
    {
      "bounds": {
        "x": 5,
        "y": 848,
        "width": 821,
        "height": 838
      },
      "action": {
        "type": "message",
        "text": "我想看菜單"
      }
    },
    {
      "bounds": {
        "x": 826,
        "y": 847,
        "width": 835,
        "height": 839
      },
      "action": {
        "type": "message",
        "text": "店鋪資訊"
      }
    },
    {
      "bounds": {
        "x": 1661,
        "y": 852,
        "width": 831,
        "height": 834
      },
      "action": {
        "type": "message",
        "text": "我想連絡你們"
      }
    }
  ]
}
'''
'''

載入前面的圖文選單設定，

並要求line_bot_api將圖文選單上傳至Line


'''

menuJson = json.loads(menuRawData)

# 轉line_bot_api 用menuJson創造圖文選單(crete_rich_menu),並將結果存回,且打印出來
lineRichMenuId = line_bot_api.create_rich_menu(rich_menu=RichMenu.new_from_json_dict(menuJson))
'''

將先前準備的菜單照片，以Post消息寄發給Line

    載入照片
    要求line_bot_api，將圖片傳到先前的圖文選單id


'''
#讀取圖片
uploadImageFile=open("material/images/圖文選單(正).png",'rb')

#請line_bot_api將圖片(uploadimagefile)上傳給line(set_rich_menu_image),必須指定id
setImageResponse = line_bot_api.set_rich_menu_image(lineRichMenuId,'image/png',uploadImageFile)


'''

將選單綁定到特定用戶身上
    取出上面得到的菜單Id及用戶id
    要求line_bot_api告知Line，將用戶與圖文選單做綁定

'''
#請line_bot_api,將某用戶跟指定的圖文選單做關聯
linkResult=line_bot_api.link_rich_menu_to_user(secretFileContentJson["self_user_id"], lineRichMenuId)

'''

檢視用戶目前所綁定的菜單
    取出用戶id，並告知line_bot_api，
    line_bot_api傳回用戶所綁定的菜單
    印出

'''
#影line_bot_api去查指定用戶的圖文選單
rich_menu_id = line_bot_api.get_rich_menu_id_of_user(secretFileContentJson["self_user_id"])


@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

'''
用戶發話,我們會依據他的內容去material資料夾內

找出 以用戶說的話為名字的資料夾

找出 裡面reply.json檔
把json檔轉成消息物件
發回給用戶
'''
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 回復用戶,他所打內容
    # stock_info=twstock.realtime.get(event.message.text)

    # 取數據回來,分析程式碼

    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text))

    # 用戶說的話，作為資料夾名字
    folder_name = event.message.text

    # 去material資料夾內找出來該reply.json
    with open('material/' + folder_name + '/reply.json', encoding='utf8') as fd:
        jsonObject = json.load(fd)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage.new_from_json_dict(jsonObject)
        )

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])
    # app.run()