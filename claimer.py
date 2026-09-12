import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# خادم وهمي لإبقاء الخدمة مجانية وشغالة على Render
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import UpdateUsernameRequest, CreateChannelRequest
from telethon.errors import UsernameInvalidError, UsernameOccupiedError, FloodWaitError

# بيانات API الخاصة بك من my.telegram.org
API_ID = 17555684  # استبدله برقم API ID الخاص بك
API_HASH = '5a7f2bfea72f4df4d0bd1e8291821148'  # استبدله بـ API Hash الخاص بك

# قائمة اليوزرات التي تريد مراقبتها (بدون @)
TARGET_USERNAMES = ['test_user_claimer_9988']

# زمن الانتظار بين كل محاولة بالثواني (مهم جداً لتجنب الحظر)
CHECK_INTERVAL = 3  

client = TelegramClient('session_claimer', API_ID, API_HASH)

async def check_and_claim(username):
    try:
        # المحاولة المباشرة لفحص وحجز اليوزر في قناة جديدة
        # أنشئ قناة مجانية مؤقتة ثم حاول تعيين اليوزر لها
        result = await client(CreateChannelRequest(title=f"Reserved {username}", about="Reserved Username", megagroup=False))
        channel = result.chats[0]
        
        await client(UpdateUsernameRequest(channel=channel, username=username))
        print(f"[+] مبروك! تم حجز اليوزر @{username} بنجاح على القناة!")
        return True
    except UsernameOccupiedError:
        # اليوزر ما زال مشغولاً
        return False
    except UsernameInvalidError:
        print(f"[-] اليوزر @{username} غير صالحة صيغته أو محظور نهائياً من تليجرام.")
        return False
    except FloodWaitError as e:
        print(f"[!] تحذير: قيود السرعة من تليجرام (FloodWait). يجب الانتظار {e.seconds} ثانية.")
        await asyncio.sleep(e.seconds)
        return False
    except Exception as e:
        # في حال وجود خطأ آخر (مثل أن الحساب صاحب اليوزر لا يزال حياً)
        return False

async def main():
    await client.start()
    print("[*] تم تشغيل السكربت وبدء مراقبة اليوزرات...")
    
    while TARGET_USERNAMES:
        for username in list(TARGET_USERNAMES):
            print(f"[*] جاري فحص @{username}...")
            claimed = await check_and_claim(username)
            if claimed:
                TARGET_USERNAMES.remove(username)
            await asyncio.sleep(CHECK_INTERVAL)

with client:
    client.loop.run_until_complete(main())
  
