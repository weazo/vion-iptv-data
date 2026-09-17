import json
import requests
import re
import os
from collections import defaultdict

# ==================== الإعدادات ====================
OUTPUT_DIR = "data"
USER_AGENT = "VionIPTVBuilder/1.0"
IPTV_ORG_API = "https://iptv-org.github.io/api"

# مصادر M3U الإضافية
M3U_SOURCES = [
    {"name": "Free-TV", "url": "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8"},
    {"name": "YueChan-Live", "url": "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u"},
    {"name": "joevess-IPTV", "url": "https://raw.githubusercontent.com/joevess/IPTV/main/m3u/iptv.m3u"},
]

# ==================== قوائم الحظر ====================
ADULT_KEYWORDS = [
    "xxx", "porn", "sex", "adult", "erotic", "brazzers", "playboy", "hustler",
    "penthouse", "onlyfans", "livejasmin", "chaturbate", "stripchat", "cam4",
    "bongacams", "myfreecams", "adult swim", "red light", "blue movie",
    "milf", "gilf", "18+", "porno", "pornography", "nude", "naked",
    "strip", "striptease", "escort", "massage", "bdsm", "fetish",
    "bondage", "hentai", "ecchi", "sexy", "playmate", "centerfold",
    "bangbros", "reality kings", "naughty america", "mofos", "twistys",
    "digital playground", "vivid", "wicked", "evil angel", "jules jordan",
    "tushy", "vixen", "blacked", "brazzers",
]

GAMBLING_KEYWORDS = [
    "gambling", "casino", "bet", "poker", "slot", "roulette", "blackjack",
    "lottery", "lotto", "jackpot", "betting", "sportsbook", "vegas",
    "bingo", "keno", "craps", "baccarat", "pachinko",
    "1xbet", "bet365", "betway", "william hill", "pokerstars", "bwin",
    "draftkings", "fanduel", "betfair", "unibet", "ladbrokes", "coral",
    "gamble", "bookmaker", "odds", "wager",
]

RACISM_HATE_KEYWORDS = [
    "racist", "racism", "white power", "white pride", "neo nazi", "neo-nazi",
    "nazi", "hitler", "adolf", "third reich", "aryan", "kkk", "ku klux klan",
    "supremacy", "supremacist", "hate", "bigot", "fascist", "fascism",
    "islamophob", "antisemit", "anti-semitic", "homophob", "xenophob",
    "ethnic cleansing", "genocide", "holocaust denial",
    "nigger", "nigga", "faggot", "retard", "chink", "spic", "kike", "wetback",
]

DRUGS_KEYWORDS = [
    "cocaine", "heroin", "marijuana", "cannabis", "meth", "methamphetamine",
    "ecstasy", "mdma", "lsd", "shrooms", "opium", "opioid", "fentanyl",
    "morphine", "codeine", "xanax", "valium", "narcotics", "cartel",
    "drug lord", "drug trafficking",
]

VIOLENCE_TERRORISM_KEYWORDS = [
    "terror", "terrorism", "terrorist", "isis", "isil", "al-qaeda",
    "taliban", "boko haram", "hamas", "hezbollah", "jihad", "jihadi",
    "extremist", "extremism", "insurgent", "militant", "militia",
    "massacre", "genocide", "torture", "atrocity",
]

OTHER_KEYWORDS = [
    "sorcery", "witchcraft", "occult", "satan", "satanism", "devil",
    "demon", "exorcism", "blasphemy", "heresy", "pagan", "voodoo",
]

ALL_BLOCKED_KEYWORDS = list(set(
    ADULT_KEYWORDS + GAMBLING_KEYWORDS + RACISM_HATE_KEYWORDS +
    DRUGS_KEYWORDS + VIOLENCE_TERRORISM_KEYWORDS + OTHER_KEYWORDS
))

# ==================== دوال مساعدة ====================
def is_blocked(text):
    """فحص إذا كان النص يحتوي على كلمات محظورة"""
    if not text:
        return False
    text_lower = text.lower()
    return any(kw in text_lower for kw in ALL_BLOCKED_KEYWORDS)

def fetch_url(url):
    """جلب محتوى URL"""
    print(f"  جلب {url}...")
    try:
        headers = {'User-Agent': USER_AGENT}
        r = requests.get(url, timeout=60, headers=headers)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  خطأ: {e}")
        return None

def fetch_json(url):
    """جلب JSON من URL"""
    content = fetch_url(url)
    if not content:
        return None
    try:
        return json.loads(content)
    except Exception as e:
        print(f"  خطأ في تحليل JSON: {e}")
        return None

def parse_m3u(content):
    """تحليل ملف M3U"""
    channels = []
    current = {}
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('#EXTINF:'):
            info = line[8:]
            attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', info))
            name = info.split(',', 1)[-1].strip() if ',' in info else attrs.get('tvg-name', 'Unknown')
            current = {
                'name': name,
                'tvg_id': attrs.get('tvg-id'),
                'tvg_name': attrs.get('tvg-name'),
                'tvg_logo': attrs.get('tvg-logo'),
                'group_title': attrs.get('group-title', 'general'),
                'url': None
            }
        elif line.startswith('http') and current:
            current['url'] = line
            channels.append(current)
            current = {}
    return channels

def normalize_name(name):
    """توحيد الأسماء لإزالة التكرار"""
    if not name:
        return ""
    name = name.lower()
    for word in ['hd', 'fhd', '4k', 'sd', 'tv', 'channel', 'live', 'uhd']:
        name = name.replace(word, '')
    return re.sub(r'[^a-z0-9\u0600-\u06FF]', '', name)

def generate_code(name, country, existing):
    """توليد كود فريد"""
    prefix = re.sub(r'[^A-Z]', '', name.upper())[:3].ljust(3, 'X')
    counter = 1
    while True:
        code = f"{prefix}-{country}-{counter:03d}"
        if code not in existing:
            return code
        counter += 1

# ==================== الدالة الرئيسية ====================
def build_channels():
    print("=" * 60)
    print("بناء قائمة Vion IPTV")
    print("=" * 60)

    all_channels_dict = {}
    blocked_count = 0

    # ---------- 1. جلب iptv-org ----------
    print("\n[1/4] جلب بيانات iptv-org...")
    channels_data = fetch_json(f"{IPTV_ORG_API}/channels.json") or []
    streams_data = fetch_json(f"{IPTV_ORG_API}/streams.json") or []
    print(f"  تم جلب {len(channels_data)} قناة، {len(streams_data)} رابط")

    streams_by_channel = defaultdict(list)
    for s in streams_data:
        ch_id = s.get('channel')
        if ch_id:
            streams_by_channel[ch_id].append(s)

    for ch in channels_data:
        ch_id = ch.get('id')
        if not ch_id or ch.get('closed') or ch.get('is_nsfw'):
            blocked_count += 1
            continue

        name = ch.get('name', '')
        category = (ch.get('categories') or ['general'])[0]

        if is_blocked(name) or is_blocked(category):
            blocked_count += 1
            continue

        streams = streams_by_channel.get(ch_id, [])
        if not streams:
            continue

        streams_list = []
        for s in streams:
            url = s.get('url', '')
            if not url:
                continue
            protocol = 'hls' if '.m3u8' in url else ('rtmp' if 'rtmp' in url else 'unknown')
            streams_list.append({
                "url": url,
                "quality": s.get('quality', 'unknown'),
                "protocol": protocol,
                "priority": 1 if s.get('quality') == '1080p' else (2 if s.get('quality') == '720p' else 3),
                "last_checked": None,
                "is_working": None
            })
        streams_list.sort(key=lambda x: x['priority'])

        key = normalize_name(name)
        if not key or key in all_channels_dict:
            continue

        all_channels_dict[key] = {
            'id': ch_id,
            'name': name,
            'country': ch.get('country', 'XX'),
            'language': (ch.get('languages') or ['unknown'])[0],
            'category': category,
            'logo': None,
            'streams': streams_list
        }

    print(f"  ✅ {len(all_channels_dict)} قناة صالحة من iptv-org")

    # ---------- 2. جلب مصادر M3U ----------
    print("\n[2/4] جلب مصادر M3U الإضافية...")
    for source in M3U_SOURCES:
        content = fetch_url(source['url'])
        if not content:
            continue

        parsed = parse_m3u(content)
        added = 0
        for ch in parsed:
            name = ch.get('name', '')
            category = ch.get('group_title', 'general')

            if is_blocked(name) or is_blocked(category):
                blocked_count += 1
                continue

            if not ch.get('url'):
                continue

            key = normalize_name(ch.get('tvg_name') or name)
            if not key:
                continue

            if key in all_channels_dict:
                # أضف رابط بديل
                url = ch['url']
                existing_urls = [s['url'] for s in all_channels_dict[key]['streams']]
                if url not in existing_urls:
                    protocol = 'hls' if '.m3u8' in url else 'unknown'
                    all_channels_dict[key]['streams'].append({
                        "url": url,
                        "quality": "unknown",
                        "protocol": protocol,
                        "priority": 5,
                        "last_checked": None,
                        "is_working": None
                    })
            else:
                country = 'XX'
                if ch.get('tvg_id') and '.' in ch['tvg_id']:
                    country = ch['tvg_id'].split('.')[-1].upper()

                all_channels_dict[key] = {
                    'id': key,
                    'name': name,
                    'country': country,
                    'language': 'unknown',
                    'category': category,
                    'logo': ch.get('tvg_logo'),
                    'streams': [{
                        "url": ch['url'],
                        "quality": "unknown",
                        "protocol": 'hls' if '.m3u8' in ch['url'] else 'unknown',
                        "priority": 5,
                        "last_checked": None,
                        "is_working": None
                    }]
                }
                added += 1
        print(f"  ✅ {source['name']}: {added} قناة جديدة")

    print(f"  إجمالي: {len(all_channels_dict)} قناة فريدة")

    # ---------- 3. بناء القنوات النهائية ----------
    print("\n[3/4] بناء القنوات النهائية...")
    all_channels = []
    existing_codes = set()
    index = 1

    for key, ch_data in all_channels_dict.items():
        name = ch_data['name']
        if is_blocked(name):
            blocked_count += 1
            continue

        country = ch_data.get('country', 'XX')
        code = generate_code(name, country, existing_codes)
        existing_codes.add(code)

        all_channels.append({
            "id": ch_data.get('id', key),
            "code": code,
            "index": index,
            "tvg_id": None,
            "tvg_chno": 100 + index,
            "name_ar": name,
            "name_en": name,
            "country": country,
            "language": ch_data.get('language', 'unknown'),
            "category": ch_data.get('category', 'general'),
            "logo": ch_data.get('logo'),
            "website": None,
            "priority": 1,
            "last_checked": None,
            "is_working": None,
            "streams": ch_data['streams']
        })
        index += 1

    # ---------- 4. حفظ الملفات ----------
    print("\n[4/4] حفظ الملفات...")
    channels_by_country = defaultdict(list)
    for ch in all_channels:
        channels_by_country[ch.get('country', 'XX')].append(ch)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ملف الفهرس
    index_data = {
        "version": "1.0.0",
        "total_channels": len(all_channels),
        "sources_used": ["iptv-org"] + [s['name'] for s in M3U_SOURCES],
        "filtering": {
            "total_blocked_keywords": len(ALL_BLOCKED_KEYWORDS),
            "blocked_channels_count": blocked_count
        },
        "countries": [
            {"code": code, "channel_count": len(chs)}
            for code, chs in sorted(channels_by_country.items())
        ]
    }
    with open(f"{OUTPUT_DIR}/index.json", 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ index.json")

    # ملف لكل دولة
    for country, chs in channels_by_country.items():
        data = {
            "version": "1.0.0",
            "country": country,
            "total_channels": len(chs),
            "channels": chs
        }
        filepath = f"{OUTPUT_DIR}/channels_{country.lower()}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ {filepath} ({len(chs)})")

    print("\n" + "=" * 60)
    print(f"✅ اكتمل! إجمالي: {len(all_channels)} قناة")
    print(f"🚫 تم استبعاد: {blocked_count} قناة")
    print("=" * 60)

if __name__ == '__main__':
    build_channels()
