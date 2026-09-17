import json
import requests
import re
import os
from collections import defaultdict

# --- الإعدادات ---
OUTPUT_DIR = "data"
CHANNEL_LIMIT = 0  # 0 = بلا حد
USER_AGENT = "VionIPTVBuilder/1.0"

# --- قوائم الحظر (Blocklists) ---
# قائمة كلمات البالغين والمقامرة
ADULT_GAMBLING_KEYWORDS = [
    # Adult
    "xxx", "porn", "sex", "adult", "erotic", "brazzers", "playboy", "hustler",
    "penthouse", "onlyfans", "livejasmin", "chaturbate", "stripchat", "cam4",
    "bongacams", "myfreecams", "adult swim", "red light", "blue movie",
    "hot", "passion", "desire", "pleasure", "sensual", "intimate",
    # Gambling
    "gambling", "casino", "bet", "poker", "slot", "roulette", "blackjack",
    "lottery", "lotto", "jackpot", "betting", "sportsbook", "vegas",
    "bingo", "keno", "craps", "baccarat", "pachinko", "toto",
    "1xbet", "bet365", "betway", "william hill", "pokerstars", "bwin",
    "draftkings", "fanduel", "betfair", "unibet", "ladbrokes", "coral",
]

# قائمة كلمات العنصرية وخطاب الكراهية
RACISM_HATE_KEYWORDS = [
    "racist", "racism", "white power", "white pride", "neo nazi", "neo-nazi",
    "nazi", "hitler", "adolf", "third reich", "aryan", "kkk", "ku klux klan",
    "supremacy", "supremacist", "hate", "bigot", "fascist", "fascism",
    "islamophob", "antisemit", "anti-semitic", "homophob", "xenophob",
    "ethnic cleansing", "genocide", "holocaust denial", "slur",
    "nigger", "nigga", "faggot", "retard", "chink", "spic", "kike", "wetback",
]

def is_blocked(name, source_type="generic"):
    """
    فحص ما إذا كان اسم القناة يحتوي على كلمات محظورة.
    source_type: نوع المصدر (iptv_org_api، m3u، generic)
    """
    if not name:
        return False
    
    name_lower = name.lower()
    
    # فحص قوائم الكلمات
    for keyword in ADULT_GAMBLING_KEYWORDS + RACISM_HATE_KEYWORDS:
        if keyword in name_lower:
            return True
    
    return False

def fetch_url(url):
    """جلب المحتوى من URL (JSON أو نص M3U)"""
    print(f"  جاري جلب {url}...")
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, timeout=60, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  خطأ في جلب {url}: {e}")
        return None

def parse_m3u(content):
    """محلل بسيط لملفات M3U لاستخراج القنوات"""
    channels = []
    lines = content.splitlines()
    current_channel = {}
    
    for line in lines:
        line = line.strip()
        if line.startswith('#EXTINF:'):
            info = line[8:]
            attrs = {}
            for match in re.finditer(r'([\w-]+)="([^"]*)"', info):
                attrs[match.group(1)] = match.group(2)
            name = info.split(',', 1)[-1].strip() if ',' in info else attrs.get('tvg-name', 'Unknown')
            
            current_channel = {
                'name': name,
                'tvg_id': attrs.get('tvg-id'),
                'tvg_name': attrs.get('tvg-name'),
                'tvg_logo': attrs.get('tvg-logo'),
                'group_title': attrs.get('group-title'),
                'url': None
            }
        elif line.startswith('http') and current_channel:
            current_channel['url'] = line
            channels.append(current_channel)
            current_channel = {}
    return channels

def parse_iptv_org(content):
    """محلل خاص لبيانات iptv-org API (streams.json)"""
    try:
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"  خطأ في تحليل JSON: {e}")
        return []

def normalize_name(name):
    """توحيد الأسماء لإزالة التكرارات"""
    if not name:
        return ""
    name = name.lower()
    for word in ['hd', 'fhd', '4k', 'sd', 'tv', 'channel', 'live', 'ar', 'en', 'uhd']:
        name = name.replace(word, '')
    name = re.sub(r'[^a-z0-9\u0600-\u06FF]', '', name)
    return name

def build_channels():
    print("=" * 60)
    print("بدء بناء قائمة Vion IPTV (متعدد المصادر + تصفية)")
    print("=" * 60)

    # 1. جلب البيانات
    print("\n[1/5] جلب البيانات من المصادر...")
    
    # جلب بيانات iptv-org
    iptv_org_channels_raw = fetch_url("https://iptv-org.github.io/api/channels.json")
    iptv_org_streams_raw = fetch_url("https://iptv-org.github.io/api/streams.json")
    
    iptv_org_channels = {}
    iptv_org_streams = defaultdict(list)
    iptv_org_blocklist = set()
    
    if iptv_org_channels_raw:
        try:
            channels_list = json.loads(iptv_org_channels_raw)
            for ch in channels_list:
                if not ch.get('id'):
                    continue
                # استبعاد القنوات المغلقة أو غير الأخلاقية
                if ch.get('closed') or ch.get('is_nsfw'):
                    iptv_org_blocklist.add(ch['id'])
                    continue
                iptv_org_channels[ch['id']] = ch
            print(f"  ✅ iptv-org: {len(iptv_org_channels)} قناة صالحة")
        except Exception as e:
            print(f"  خطأ في معالجة قنوات iptv-org: {e}")
    
    if iptv_org_streams_raw:
        try:
            streams_list = json.loads(iptv_org_streams_raw)
            for s in streams_list:
                ch_id = s.get('channel')
                if ch_id and ch_id not in iptv_org_blocklist:
                    iptv_org_streams[ch_id].append(s)
        except Exception as e:
            print(f"  خطأ في معالجة روابط iptv-org: {e}")

    # جلب قوائم M3U الإضافية
    m3u_sources = [
        {"name": "Free-TV", "url": "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8"},
        {"name": "YueChan-Live", "url": "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u"},
        {"name": "joevess-IPTV", "url": "https://raw.githubusercontent.com/joevess/IPTV/main/m3u/iptv.m3u"},
    ]
    
    all_m3u_channels = []
    for source in m3u_sources:
        content = fetch_url(source['url'])
        if content:
            parsed = parse_m3u(content)
            for ch in parsed:
                ch['source'] = source['name']
                if ch.get('url'):
                    all_m3u_channels.append(ch)
            print(f"  ✅ {source['name']}: {len(parsed)} قناة")
    
    print(f"  إجمالي قنوات M3U: {len(all_m3u_channels)}")

    # 2. بناء قائمة موحدة من iptv-org
    print("\n[2/5] بناء القنوات من iptv-org...")
    all_channels_dict = {}
    
    for ch_id, ch_info in iptv_org_channels.items():
        streams = iptv_org_streams.get(ch_id, [])
        if not streams:
            continue
        
        name = ch_info.get('name', '')
        
        # فحص الحظر الإضافي
        if is_blocked(name):
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
        if key and key not in all_channels_dict:
            all_channels_dict[key] = {
                'id': ch_id,
                'name': name,
                'country': ch_info.get('country', 'XX'),
                'language': (ch_info.get('languages') or ['unknown'])[0],
                'category': (ch_info.get('categories') or ['general'])[0],
                'logo': None,
                'streams': streams_list
            }

    # 3. دمج قنوات M3U
    print("\n[3/5] دمج قنوات M3U...")
    for ch in all_m3u_channels:
        name = ch.get('name', '')
        if is_blocked(name):
            continue
        
        key = normalize_name(ch.get('tvg_name') or name)
        if not key:
            continue
        
        if key in all_channels_dict:
            # إضافة رابط البث إلى القناة الموجودة
            url = ch.get('url')
            if url and url not in [s['url'] for s in all_channels_dict[key]['streams']]:
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
            # قناة جديدة
            country_code = 'XX'
            if ch.get('tvg_id') and '.' in ch['tvg_id']:
                country_code = ch['tvg_id'].split('.')[-1].upper()
            
            all_channels_dict[key] = {
                'id': key,
                'name': name,
                'country': country_code,
                'language': 'unknown',
                'category': ch.get('group_title', 'general'),
                'logo': ch.get('tvg_logo'),
                'streams': [{
                    "url": ch.get('url'),
                    "quality": "unknown",
                    "protocol": 'hls' if '.m3u8' in ch.get('url', '') else 'unknown',
                    "priority": 5,
                    "last_checked": None,
                    "is_working": None
                }]
            }
    
    print(f"  إجمالي القنوات الفريدة: {len(all_channels_dict)}")

    # 4. بناء قائمة القنوات النهائية
    print("\n[4/5] بناء القنوات النهائية...")
    all_channels = []
    existing_codes = set()
    index = 1
    
    for key, ch_data in all_channels_dict.items():
        name = ch_data['name']
        
        # فحص الحظر النهائي
        if is_blocked(name):
            continue
        
        country_code = ch_data.get('country', 'XX')
        prefix = re.sub(r'[^A-Z]', '', name.upper())[:3].ljust(3, 'X')
        counter = 1
        while True:
            code = f"{prefix}-{country_code}-{counter:03d}"
            if code not in existing_codes:
                break
            counter += 1
        existing_codes.add(code)
        
        channel_data = {
            "id": ch_data.get('id', key),
            "code": code,
            "index": index,
            "tvg_id": None,
            "tvg_chno": 100 + index,
            "name_ar": name,
            "name_en": name,
            "country": country_code,
            "language": ch_data.get('language', 'unknown'),
            "category": ch_data.get('category', 'general'),
            "logo": ch_data.get('logo'),
            "website": None,
            "priority": 1,
            "last_checked": None,
            "is_working": None,
            "streams": ch_data['streams']
        }
        all_channels.append(channel_data)
        index += 1

    # 5. حفظ الملفات
    print("\n[5/5] حفظ الملفات...")
    channels_by_country = defaultdict(list)
    for ch in all_channels:
        country = ch.get('country', 'XX')
        channels_by_country[country].append(ch)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    master_index = {
        "version": "1.0.0",
        "total_channels": len(all_channels),
        "sources_used": ["iptv-org", "Free-TV", "YueChan-Live", "joevess-IPTV"],
        "filtering": {
            "adult_gambling_keywords": len(ADULT_GAMBLING_KEYWORDS),
            "racism_hate_keywords": len(RACISM_HATE_KEYWORDS),
            "iptv_org_nsfw_blocklist": len(iptv_org_blocklist)
        },
        "countries": [
            {"code": code, "channel_count": len(chs)}
            for code, chs in sorted(channels_by_country.items())
        ]
    }
    with open(f"{OUTPUT_DIR}/index.json", 'w', encoding='utf-8') as f:
        json.dump(master_index, f, ensure_ascii=False, indent=2)
    print(f"  ✅ index.json")

    for country_code, chs in channels_by_country.items():
        country_file = {
            "version": "1.0.0",
            "country": country_code,
            "total_channels": len(chs),
            "channels": chs
        }
        filepath = f"{OUTPUT_DIR}/channels_{country_code.lower()}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(country_file, f, ensure_ascii=False, indent=2)
        print(f"  ✅ {filepath} ({len(chs)} قناة)")

    print("\n" + "=" * 60)
    print(f"تم الانتهاء! إجمالي القنوات: {len(all_channels)}")
    print(f"تم استبعاد {len(iptv_org_blocklist)} قناة NSFW من iptv-org")
    print("=" * 60)

if __name__ == '__main__':
    build_channels()
