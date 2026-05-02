import http.server
import socketserver
import threading
import os

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()


import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json
import time
import threading
import os
import uuid
import html
import re
from datetime import datetime

try:
    from telebot.types import CopyTextButton
    HAS_COPY_BTN = True
except ImportError:
    HAS_COPY_BTN = False

TOKEN="8629605075:AAHhuS6Nch-ZKkMJEXRgJ2c8WqvyvZC64w4"
ADMIN_ID = 7041397843
BASE_URL = "http://185.190.142.81"
NEXA_API_KEY="nxa_f691b5e9c1f4757f9c65536b98135381321af18c"

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "dxa_bot_premium_data_v4.json"

active_polls = {}
user_states = {}
traffic_cooldowns = {}
data_lock = threading.RLock()
COUNTRY_FLAGS = {
    "afghanistan": "🇦🇫", "albania": "🇦🇱", "algeria": "🇩🇿", "andorra": "🇦🇩",
    "angola": "🇦🇴", "argentina": "🇦🇷", "armenia": "🇦🇲", "australia": "🇦🇺",
    "austria": "🇦🇹", "azerbaijan": "🇦🇿", "bahamas": "🇧🇸", "bahrain": "🇧🇭",
    "bangladesh": "🇧🇩", "barbados": "🇧🇧", "belarus": "🇧🇾", "belgium": "🇧🇪",
    "belize": "🇧🇿", "benin": "🇧🇯", "bhutan": "🇧🇹", "bolivia": "🇧🇴",
    "bosnia": "🇧🇦", "botswana": "🇧🇼", "brazil": "🇧🇷", "brunei": "🇧🇳",
    "bulgaria": "🇧🇬", "burkina faso": "🇧🇫", "burundi": "🇧🇮", "cambodia": "🇰🇭",
    "cameroon": "🇨🇲", "canada": "🇨🇦", "chile": "🇨🇱", "china": "🇨🇳",
    "colombia": "🇨🇴", "congo": "🇨🇬", "costa rica": "🇨🇷", "croatia": "🇭🇷",
    "cuba": "🇨🇺", "cyprus": "🇨🇾", "czech republic": "🇨🇿", "denmark": "🇩🇰",
    "djibouti": "🇩🇯", "dominican republic": "🇩🇴", "ecuador": "🇪🇨", "egypt": "🇪🇬",
    "el salvador": "🇸🇻", "estonia": "🇪🇪", "ethiopia": "🇪🇹", "fiji": "🇫🇯",
    "finland": "🇫🇮", "france": "🇫🇷", "gabon": "🇬🇦", "gambia": "🇬🇲",
    "georgia": "🇬🇪", "germany": "🇩🇪", "ghana": "🇬🇭", "greece": "🇬🇷",
    "guatemala": "🇬🇹", "guinea": "🇬🇳", "haiti": "🇭🇹", "honduras": "🇭🇳",
    "hungary": "🇭🇺", "iceland": "🇮🇸", "india": "🇮🇳", "indonesia": "🇮🇩",
    "iran": "🇮🇷", "iraq": "🇮🇶", "ireland": "🇮🇪", "israel": "🇮🇱",
    "italy": "🇮🇹", "jamaica": "🇯🇲", "japan": "🇯🇵", "jordan": "🇯🇴",
    "kazakhstan": "🇰🇿", "kenya": "🇰🇪", "kuwait": "🇰🇼", "kyrgyzstan": "🇰🇬",
    "laos": "🇱🇦", "latvia": "🇱🇻", "lebanon": "🇱🇧", "libya": "🇱🇾",
    "lithuania": "🇱🇹", "luxembourg": "🇱🇺", "madagascar": "🇲🇬", "malawi": "🇲🇼",
    "malaysia": "🇲🇾", "maldives": "🇲🇻", "mali": "🇲🇱", "malta": "🇲🇹",
    "mauritius": "🇲🇺", "mexico": "🇲🇽", "moldova": "🇲🇩", "mongolia": "🇲🇳",
    "morocco": "🇲🇦", "mozambique": "🇲🇿", "myanmar": "🇲🇲", "namibia": "🇳🇦",
    "nepal": "🇳🇵", "netherlands": "🇳🇱", "new zealand": "🇳🇿", "nicaragua": "🇳🇮",
    "niger": "🇳🇪", "nigeria": "🇳🇬", "norway": "🇳🇴", "oman": "🇴🇲",
    "pakistan": "🇵🇰", "palestine": "🇵🇸", "panama": "🇵🇦", "paraguay": "🇵🇾",
    "peru": "🇵🇪", "philippines": "🇵🇭", "poland": "🇵🇱", "portugal": "🇵🇹",
    "qatar": "🇶🇦", "romania": "🇷🇴", "russia": "🇷🇺", "rwanda": "🇷🇼",
    "saudi arabia": "🇸🇦", "senegal": "🇸🇳", "serbia": "🇷🇸", "singapore": "🇸🇬",
    "slovakia": "🇸🇰", "slovenia": "🇸🇮", "somalia": "🇸🇴", "south africa": "🇿🇦",
    "south korea": "🇰🇷", "spain": "🇪🇸", "sri lanka": "🇱🇰", "sudan": "🇸🇩",
    "sweden": "🇸🇪", "switzerland": "🇨🇭", "syria": "🇸🇾", "taiwan": "🇹🇼",
    "tajikistan": "🇹🇯", "tanzania": "🇹🇿", "thailand": "🇹🇭", "togo": "🇹🇬",
    "tunisia": "🇹🇳", "turkey": "🇹🇷", "uganda": "🇺🇬", "ukraine": "🇺🇦",
    "united arab emirates": "🇦🇪", "united kingdom": "🇬🇧", "united states": "🇺🇸",
    "uruguay": "🇺🇾", "uzbekistan": "🇺🇿", "venezuela": "🇻🇪", "vietnam": "🇻🇳",
    "yemen": "🇾🇪", "zambia": "🇿🇲", "zimbabwe": "🇿🇼",
    "usa": "🇺🇸", "uk": "🇬🇧", "uae": "🇦🇪", "hong kong": "🇭🇰"
}

def get_country_flag(country_name):
    if not country_name:
        return "🌍"
    name = str(country_name).lower().strip()
    if name in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[name]
    for country, flag in COUNTRY_FLAGS.items():
        if len(country) >= 4 and (country in name or name in country):
            return flag
    return "🌍"
    COUNTRY_ISO = {
    "bangladesh": "BD", "india": "IN", "pakistan": "PK", "cameroon": "CM",
    "vietnam": "VN", "indonesia": "ID", "united states": "US", "usa": "US",
    "united kingdom": "GB", "uk": "GB", "russia": "RU", "brazil": "BR",
    "nigeria": "NG", "philippines": "PH", "egypt": "EG", "turkey": "TR",
    "thailand": "TH", "myanmar": "MM", "south africa": "ZA", "colombia": "CO"
}

SERVICE_SHORTS = {
    "facebook": "FB", "whatsapp": "WA", "telegram": "TG",
    "instagram": "IG", "twitter": "TW", "google": "GO",
    "gmail": "GM", "youtube": "YT", "tiktok": "TT"
}

EMOJI_COLLECTION = {
    "done": "✅", "cross": "❌", "warning": "⚠️", "time": "⏰",
    "waiting": "🔄", "message": "📩", "otp": "🔐", "number": "📞",
    "world": "🌐", "user": "👤", "bot": "🤖", "live": "🟢",
    "off": "🔴", "traffic": "📊", "chart": "📈", "star": "⭐",
    "crown": "👑", "fire": "🔥", "sparkles": "✨"
}

def get_iso_code(country_name):
    name = str(country_name).lower().strip()
    return COUNTRY_ISO.get(name, name[:2].upper())

def emo(keyword, default="✨"):
    if not keyword:
        return default
    kw = str(keyword).lower().strip()
    return EMOJI_COLLECTION.get(kw, default)

def get_short_service(service_name):
    name = str(service_name).lower().strip()
    return SERVICE_SHORTS.get(name, name[:2].upper())
    def format_url(url):
    url = url.strip()
    if url and not url.startswith(('http://', 'https://', 'tg://')):
        return 'https://' + url
    return url

def extract_channel_username(url):
    if "t.me/" in url:
        parts = url.split("t.me/")
        if len(parts) > 1:
            username = parts[1].split("/")[0].split("?")[0]
            if not username.startswith("@"):
                username = "@" + username
            return username
    return ""

def mask_number(phone):
    phone_str = str(phone).replace('+', '')
    if len(phone_str) > 7:
        return f"{phone_str[:3]}VIP{phone_str[-4:]}"
    return phone_str

def safe_send(chat_id, text, reply_markup=None, message_id=None):
    try:
        clean_text = re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text)
        if message_id:
            return bot.edit_message_text(
                clean_text,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        else:
            return bot.send_message(
                chat_id,
                clean_text,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
    except Exception:
        return None
        
   def load_data():
    with data_lock:
        if not os.path.exists(DATA_FILE):
            default_data = {
                "users": [],
                "services_data": {},
                "forward_groups": [],
                "main_otp_link": "https://t.me/",
                "watermark": "VIP NUMBER CLUB",
                "force_join_enabled": False,
                "force_join_channels": []
            }
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(default_data, f, indent=4)
            return default_data

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "force_join_enabled" not in data:
                data["force_join_enabled"] = False
            if "force_join_channels" not in data:
                data["force_join_channels"] = []

            return data
        except Exception:
            return {
                "users": [],
                "services_data": {},
                "forward_groups": [],
                "main_otp_link": "https://t.me/",
                "watermark": "VIP NUMBER CLUB",
                "force_join_enabled": False,
                "force_join_channels": []
            }


def save_data(data):
    with data_lock:
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass


def add_user(user_id):
    data = load_data()
    if user_id not in data.get("users", []):
        data["users"].append(user_id)
        save_data(data)
        def get_total_ranges():
    data = load_data()
    count = 0
    for srv in data.get("services_data", {}).values():
        for cnt in srv.get("countries", {}).values():
            count += len(cnt.get("ranges", {}))
    return count


def check_force_join(user_id):
    if user_id == ADMIN_ID:
        return True

    data = load_data()

    if not data.get("force_join_enabled"):
        return True

    channels = data.get("force_join_channels", [])

    if not channels:
        return True

    for link in channels:
        chat_username = extract_channel_username(link)
        if not chat_username:
            continue
        try:
            member = bot.get_chat_member(chat_username, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception:
            pass

    return True


def show_force_join_message(chat_id, message_id=None):
    data = load_data()
    channels = data.get("force_join_channels", [])

    text = (
        f"{emo('warning')} <b>ACCESS DENIED</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📢 Join our channels to use this bot\n\n"
        f"Click <b>JOINED</b> after joining"
    )

    markup = InlineKeyboardMarkup()

    for link in channels:
        markup.add(InlineKeyboardButton("📢 Join Channel", url=link))

    markup.add(InlineKeyboardButton("✅ JOINED ✅", callback_data="check_join"))

    safe_send(chat_id, text, markup, message_id)
    def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📱 GET NUMBER"),
        KeyboardButton("📊 TRAFFIC")
    )
    if user_id == ADMIN_ID:
        markup.add(KeyboardButton("⚙️ ADMIN PANEL"))
    return markup


def show_main_menu(chat_id, first_name=None, message_id=None):
    if not first_name:
        try:
            first_name = bot.get_chat(chat_id).first_name
        except Exception:
            first_name = "VIP User"

    data = load_data()
    watermark = data.get("watermark", "VIP NUMBER CLUB")

    text = (
        f"{emo('crown')} <b>VIP NUMBER CLUB</b> {emo('crown')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emo('user')} Welcome, <a href='tg://user?id={chat_id}'>{html.escape(first_name)}</a>!\n\n"
        f"{emo('star')} Premium OTP Service {emo('star')}\n\n"
        f"📱 Tap GET NUMBER to start\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emo('fire')} {html.escape(watermark)} {emo('fire')}"
    )

    safe_send(chat_id, text, get_main_menu(chat_id), message_id)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    bot.clear_step_handler_by_chat_id(message.chat.id)
    add_user(user_id)

    if not check_force_join(user_id):
        show_force_join_message(message.chat.id)
        return

    show_main_menu(message.chat.id, message.from_user.first_name)
    @bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text

    bot.clear_step_handler_by_chat_id(message.chat.id)
    add_user(user_id)

    if "GET NUMBER" in text:
        if not check_force_join(user_id):
            show_force_join_message(message.chat.id)
            return
        show_user_services(message.chat.id)

    elif "TRAFFIC" in text:
        if not check_force_join(user_id):
            show_force_join_message(message.chat.id)
            return
        show_traffic_search(message.chat.id)

    elif "ADMIN PANEL" in text:
        if user_id == ADMIN_ID:
            show_admin_panel(message.chat.id)
        else:
            bot.send_message(
                message.chat.id,
                f"{emo('warning')} <b>Access Denied!</b>",
                parse_mode="HTML"
            )


def show_user_services(chat_id, message_id=None):
    data = load_data()
    markup = InlineKeyboardMarkup(row_width=2)

    buttons = []
    for srv_id, srv in data.get("services_data", {}).items():
        has_ranges = any(
            len(cnt.get("ranges", {})) > 0
            for cnt in srv.get("countries", {}).values()
        )
        if has_ranges:
            buttons.append(
                InlineKeyboardButton(
                    text=f"{emo(srv['name'])} {srv['name']}",
                    callback_data=f"usr_s|{srv_id}"
                )
            )

    if buttons:
        markup.add(*buttons)

    markup.add(
        InlineKeyboardButton("🔍 Custom Search", callback_data="find_number")
    )

    text = (
        f"{emo('star')} <b>AVAILABLE SERVICES</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔍 Choose your service\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    safe_send(chat_id, text, markup, message_id)
    def show_user_countries(chat_id, srv_id, message_id=None):
    data = load_data()
    srv_data = data.get("services_data", {}).get(srv_id)

    if not srv_data:
        return

    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []

    for cnt_id, cnt in srv_data.get("countries", {}).items():
        if len(cnt.get("ranges", {})) > 0:
            flag = get_country_flag(cnt["name"])
            buttons.append(
                InlineKeyboardButton(
                    text=f"{flag} {cnt['name']}",
                    callback_data=f"usr_c|{srv_id}|{cnt_id}"
                )
            )

    if buttons:
        markup.add(*buttons)

    markup.add(
        InlineKeyboardButton("🔙 Back", callback_data="back_to_user_services")
    )

    text = (
        f"{emo('world')} <b>SELECT COUNTRY</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📱 Service: <code>{html.escape(srv_data['name'])}</code>\n\n"
        f"Choose your country"
    )

    safe_send(chat_id, text, markup, message_id)


def show_user_ranges(chat_id, srv_id, cnt_id, message_id=None):
    data = load_data()
    srv_data = data.get("services_data", {}).get(srv_id)

    if not srv_data:
        return

    cnt_data = srv_data.get("countries", {}).get(cnt_id)
    if not cnt_data:
        return

    markup = InlineKeyboardMarkup(row_width=2)
    flag = get_country_flag(cnt_data["name"])

    buttons = [
        InlineKeyboardButton(
            text=f"📱 {rng_val}",
            callback_data=f"usr_r|{srv_id}|{cnt_id}|{rng_id}"
        )
        for rng_id, rng_val in cnt_data.get("ranges", {}).items()
    ]

    if buttons:
        markup.add(*buttons)

    markup.add(
        InlineKeyboardButton(
            "🔙 Back",
            callback_data=f"usr_s|{srv_id}"
        )
    )

    text = (
        f"{emo('number')} <b>SELECT RANGE</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emo(srv_data['name'])} Service: <code>{html.escape(srv_data['name'])}</code>\n"
        f"{flag} Country: <code>{html.escape(cnt_data['name'])}</code>\n\n"
        f"Choose your range"
    )

    safe_send(chat_id, text, markup, message_id)
    def fetch_number(chat_id, service_info, api_key, msg_id, is_custom=False):
    headers = {'X-API-Key': api_key}
    payload = {"range": service_info['range'], "format": "normal"}

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/numbers/get",
            json=payload,
            headers=headers,
            timeout=15
        )
        res_data = response.json()

        if res_data.get("success"):
            number = res_data.get("number")
            number_id = res_data.get("number_id")

            data = load_data()
            watermark = data.get("watermark", "VIP NUMBER CLUB")

            c_name = service_info.get('country_name', '').lower().strip()
            s_name = service_info.get('service_name', '').lower().strip()

            c_code = COUNTRY_ISO.get(c_name, 'UN')
            flag = get_country_flag(c_name)
            srv_emoji = emo(s_name)

            text = (
                f"{emo('crown')} <b>NUMBER ALLOCATED</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{srv_emoji} Service: <b>{html.escape(service_info['service_name'])}</b>\n"
                f"{flag} Country: <b>{html.escape(service_info['country_name'])}</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📱 <code>{number}</code>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{emo('fire')} {html.escape(watermark)} {emo('fire')}"
            )

            main_link = format_url(data.get("main_otp_link", "https://t.me/"))

            markup = InlineKeyboardMarkup(row_width=2)

            if is_custom:
                markup.add(
                    InlineKeyboardButton("🔄 Change", callback_data=f"chgc|{service_info['range']}"),
                    InlineKeyboardButton("📨 OTP Group", url=main_link)
                )
                markup.add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
            else:
                markup.add(
                    InlineKeyboardButton(
                        "🔄 Change",
                        callback_data=f"chg_r|{service_info['srv_id']}|{service_info['cnt_id']}|{service_info['id']}"
                    ),
                    InlineKeyboardButton("📨 OTP Group", url=main_link)
                )
                markup.add(
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data=f"usr_c|{service_info['srv_id']}|{service_info['cnt_id']}"
                    )
                )

            safe_send(chat_id, text, markup, msg_id)

            active_polls[str(chat_id)] = True

            threading.Thread(
                target=poll_otp,
                args=(chat_id, number_id, number, service_info, api_key, msg_id, is_custom)
            ).start()

        else:
            safe_send(chat_id, f"{emo('cross')} <b>Number out of stock.</b>", None, msg_id)

    except Exception:
        safe_send(chat_id, f"{emo('warning')} <b>Connection Error.</b>", None, msg_id)
        def poll_otp(chat_id, number_id, phone_number, service_info, api_key, msg_id, is_custom):
    headers = {'X-API-Key': api_key}
    timeout = 600
    start_time = time.time()

    while time.time() - start_time < timeout:

        if not active_polls.get(str(chat_id), True):
            return

        try:
            res = requests.get(
                f"{BASE_URL}/api/v1/numbers/{number_id}/sms",
                headers=headers,
                timeout=15
            )
            s_data = res.json()

            if s_data.get("success") and s_data.get("otp"):

                otp_code = s_data.get("otp")

                c_name = service_info.get('country_name', '').lower().strip()
                s_name = service_info.get('service_name', '').lower().strip()

                flag = get_country_flag(c_name)
                srv_emoji = emo(s_name)

                disp_num = f"+{str(phone_number).replace('+', '')}"

                # Main message update
                success_text = (
                    f"{emo('done')} <b>COMPLETED</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{srv_emoji} Service: <b>{html.escape(service_info['service_name'])}</b>\n"
                    f"{flag} Country: <b>{html.escape(service_info['country_name'])}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📱 <code>{disp_num}</code>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🟢 OTP received!"
                )

                markup = InlineKeyboardMarkup()

                if is_custom:
                    markup.add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
                else:
                    markup.add(
                        InlineKeyboardButton(
                            "🔙 Back",
                            callback_data=f"usr_c|{service_info['srv_id']}|{service_info['cnt_id']}"
                        )
                    )

                safe_send(chat_id, success_text, markup, msg_id)

                # Inbox message
                inbox_msg = (
                    f"{emo('message')} <b>NEW OTP RECEIVED</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{srv_emoji} Service: {html.escape(service_info['service_name'])}\n"
                    f"{flag} Country: {html.escape(service_info['country_name'])}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📱 <code>{disp_num}</code>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🔐 OTP: <code>{otp_code}</code>"
                )

                safe_send(chat_id, inbox_msg)

                active_polls[str(chat_id)] = False
                return

        except Exception:
            pass

        time.sleep(3)

    if active_polls.get(str(chat_id), False):
        safe_send(
            chat_id,
            f"{emo('time')} <b>Timeout! No OTP received.</b>",
            None,
            msg_id
        )
        active_polls[str(chat_id)] = False
        def show_admin_panel(chat_id, message_id=None):
    data = load_data()

    text = (
        f"{emo('crown')} <b>ADMIN PANEL</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 Users: {len(data.get('users', []))}\n"
        f"📱 Ranges: {get_total_ranges()}\n"
        f"🔗 Groups: {len(data.get('forward_groups', []))}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="back_to_user_services"))

    safe_send(chat_id, text, markup, message_id)


# ================================
# 🚀 BOT START
# ================================
if __name__ == "__main__":
    print("👑 VIP NUMBER CLUB BOT RUNNING... 👑")
    bot.infinity_polling()