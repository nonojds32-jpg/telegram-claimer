import asyncio
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, UpdateUsernameRequest
from telethon.errors import UsernameInvalidError, UsernameOccupiedError, FloodWaitError

# خادم وهمي للمنصات السحابية
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Claimer Bot is Running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# إعدادات الحساب
API_ID = 17555684
API_HASH = '5a7f2bfea72f4df4d0bd1e8291821148'

# قائمة اليوزرات المطلوبة (بدون @)
TARGET_USERNAMES = ['EFE_E']

# زمن الانتظار بين المحاولات (بالثواني)
CHECK_INTERVAL = 10

client = TelegramClient('session_claimer', API_ID, API_HASH)

# متغير لحفظ القناة المجهزة للحجز
target_channel = None

async def prepare_channel():
    global target_channel
    if not target_channel:
        print("[*] جاري إنشاء قناة واحدة جاهزة لاستقبال اليوزر...")
        result = await client(CreateChannelRequest(
            title="Reserved Username",
            about="Reserved via Claimer Bot",
            megagroup=False
        ))
        target_channel = result.chats[0]
        print(f"[✓] تم إنشاء القناة المجهزة بنجاح ID: {target_channel.id}")

async def check_and_claim(username):
    global target_channel
    try:
        # المحاولة المباشرة لربط اليوزر بالقناة المجهزة سابقاً
        await client(UpdateUsernameRequest(channel=target_channel, username=username))
        print(f"\n[🎉] مبروك! تم حجز اليوزر @{username} بنجاح!")
        return True
    except UsernameOccupiedError:
        # اليوزر ما زال مشغولاً (طبيعي)
        return False
    except UsernameInvalidError:
        print(f"\n[❌] اليوزر @{username} غير صالح أو محظور نهائياً.")
        return False
    except FloodWaitError as e:
        print(f"\n[⚠️] تم فرض حظر مؤقت (FloodWait). يجب الانتظار {e.seconds} ثانية.")
        await asyncio.sleep(e.seconds)
        return False
    except Exception as e:
        print(f"\n[❌] حدث خطأ أخير: {e}")
        return False

async def main():
    await client.start()
    print("[✓] تم تسجيل الدخول بنجاح إلى تليجرام.")
    
    # إنشاء قناة واحدة فقط لاستخدامها لكل المحاولات
    await prepare_channel()
    
    print("\n[*] بدأ المراقبة وفحص اليوزرات...")
    
    while True:
        for username in TARGET_USERNAMES:
            print(f"\r[*] جاري فحص اليوزر: @{username}...", end="", flush=True)
            success = await check_and_claim(username)
            if success:
                print(f"[✓] تم إيقاف السكربت للحفاظ على اليوزر المحجوز.")
                return
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    client.loop.run_until_complete(main())
    
