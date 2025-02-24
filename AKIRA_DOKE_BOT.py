from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import random

app = Flask(__name__)

# 🔹 你的 LINE Bot Token & Secret（請填入你的資訊）
LINE_BOT_API = "6KGfuSJHyZXkNeTL5Tm0gKcM815fZtCyHZ13uM17g6/cvgBXyEvlHP/k1tofXZO7CewhHS+LGp60MM3vrannCiqiqGWg1Q6tBvhNam3SgJOo5WcZeSnOppHXRUVYAxDI/RM4MVY5aB3h+HjZBQwRTwdB04t89/1O/w1cDnyilFU="
LINE_SECRET = "66c96646715bdc7efde71cad0e757bd0"

line_bot_api = LineBotApi(LINE_BOT_API)
handler = WebhookHandler(LINE_SECRET)

# 記錄玩家的身份（預設是知惠子）
user_roles = {}

# 🔹 標點符號
punctuations = ["。", "！", "……"]

# 🔹 真木秋的「滾！」回應（根據不同身份，並加上標點+表情or動作）
makki_replies = {
    "知惠子": [
        "（臉紅）", "（假裝沒聽見）", "（輕咳了一聲）",
        "（語氣有點遲疑）", "（翻過課本掩飾表情）",
        "（但眼神偷偷飄向你）", "（別過頭）",
        "（眼神空洞,覺得你這問題太煩了）", "（崩潰）", 
        "（微笑）",  "（露出意味深長的笑容）" 
    ],
    "石川": [
        "（揉了揉眉心）", "（明顯不耐煩）", "（冷冷地看著你）",
        "（語氣冷漠）", "（按了按太陽穴）", "（嘆了口氣）", 
        "（準備摔筆）", "（到底我為什麼會聽你在廢話）", 
        "（合上雙眼）", "（思考人生）" 
    ]
}

# 🔹 石川明的亂入回應（隨機選擇）
ishikawa_comments = [
    "秋，你不怕知惠子要哭嗎？",
    "秋，你真是的……",
    "秋，你這樣好嗎？",
    "哈哈，秋醬又在嘴硬了。",
    "啊啦，這畫面真是有趣呢。",
    "知惠子，快來拯救你的真木先生吧～",
    "真木，給點反應吧，這樣可不行哦～"
]

# 🔹「別滾」觸發的特殊回應（30% 機率）
special_replies = [
    "好啦，給我滾。",
    "愛滾就滾。",
    "那...我愛你，知惠子❤️",
    "喵。(貓耳模式)", 
    "那我就是愛叫你滾嘛...", 
]

# 🔹「作者 aka 你的吐槽」（30% 機率觸發）
author_trolls = [
    "（作者扶額）這場面怎麼又變成這樣了？",
    "（作者冷眼旁觀）我覺得你應該要習慣一下。",
    "（作者沉思）如果有一天真木不說滾，這 Bot 會不會壞掉？",
    "（作者翻白眼）這對話劇本是不是永遠不會變？",
    "（作者敲桌）我說真木...你能不能來點新的發展？！",
    "（作者無奈嘆氣）這都第幾次了，你還不習慣嗎？"
]

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_input = event.message.text.strip().lower()  # 轉成小寫，避免大小寫影響

    # 🆕 如果玩家輸入「切換身份: 知惠子」或「切換身份: 石川」
    if "切換身份: 知惠子" in user_input:
        user_roles[user_id] = "知惠子"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你現在是知惠子！"))
        return
    elif "切換身份: 石川" in user_input:
        user_roles[user_id] = "石川"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你現在是石川！"))
        return

    # 預設玩家身份為知惠子
    role = user_roles.get(user_id, "知惠子")

    # 🆕 如果訊息包含「別滾」「不要滾」，30% 機率觸發特殊回應
    if any(keyword in user_input for keyword in ["別滾", "不要滾", "不要再滾了"]):
        if random.random() < 0.3:  # 30% 機率
            reply_text = random.choice(special_replies)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            return  

    # 正常情況：根據身份選擇真木的「滾！」回應，包含標點 + 表情or動作
    reply_text = f"滾{random.choice(punctuations)} {random.choice(makki_replies[role])}"
    
    # 30% 機率讓石川亂入
    if random.random() < 0.3:  # 30% 機率觸發
        ishikawa_reply = f"\n石川：{random.choice(ishikawa_comments)}"
        reply_text += ishikawa_reply

    # 30% 機率讓「作者 aka 你」吐槽
    if random.random() < 0.3:  # 30% 機率觸發
        author_reply = f"\n作者：{random.choice(author_trolls)}"
        reply_text += author_reply

    # 發送回應
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run(port=5000)
