import json
import requests
import re
import os
from collections import defaultdict

# --- الإعدادات ---
API_BASE = "https://iptv-org.github.io/api"
OUTPUT_DIR = "data"
CHANNEL_LIMIT = 0  # 0 = بلا حد، ضع رقم لتحديد عدد القنوات للتجربة

def fetch_json(endpoint):
    """جلب ملف JSON من iptv-org API"""
    url = f"{API_BASE}/{endpoint}"
    print(f"  جاري جلب {url}...")
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  خطأ في جلب {endpoint}: {e}")
        return []

def generate_code(name_en, country_code, existing_codes):
    """توليد كود فريد للقناة"""
    prefix = re.sub(r'[^A-Z]', '', name_en.upper())[:3]
    if len(prefix) < 3:
        prefix = prefix.ljust(3, 'X')
    counter = 1
    while True:
        code = f"{prefix}-{country_code}-{counter:03d}"
        if code not in existing_codes:
            return code
        counter += 1

def build_channels():
    print("=" * 60)
    print("بدء بناء قائمة Vion IPTV")
    print("=" * 60)

    # 1. جلب البيانات
    print("\n[1/5] جلب البيانات من iptv-org...")
    channels_raw = fetch_json("channels.json")
    streams_raw = fetch_json("streams.json")
    logos_raw = fetch_json("logos.json")
    countries_raw = fetch_json("countries.json")
    categories_raw = fetch_json("categories.json")

    if not channels_raw:
        print("فشل جلب القنوات. توقف.")
        return

    print(f"  تم جلب {len(channels_raw)} قناة، {len(streams_raw)} رابط بث")

    # 2. بناء خرائط للوصول السريع
    print("\n[2/5] بناء الخرائط...")
    streams_by_channel = defaultdict(list)
    for stream in streams_raw:
        ch_id = stream.get('channel')
        if ch_id:
            streams_by_channel[ch_id].append(stream)

    logos_by_channel = defaultdict(list)
    for logo in logos_raw:
        ch_id = logo.get('channel')
        if ch_id and logo.get('in_use'):
            logos_by_channel[ch_id].append(logo)

    countries_map = {c['code']: c for c in countries_raw}
    categories_map = {c['id']: c for c in categories_raw}

    # 3. بناء قائمة القنوات الموحدة
    print("\n[3/5] معالجة القنوات...")
    all_channels = []
    existing_codes = set()
    index = 1

    for ch in channels_raw:
        ch_id = ch.get('id')
        if not ch_id:
            continue
        # تجاهل القنوات المغلقة أو غير الأخلاقية
        if ch.get('closed') or ch.get('is_nsfw'):
            continue

        ch_streams = streams_by_channel.get(ch_id, [])
        if not ch_streams:
            continue

        # بناء قائمة البث
        streams_list = []
        for s in ch_streams:
            url = s.get('url', '')
            protocol = 'hls' if '.m3u8' in url else ('rtmp' if 'rtmp' in url else 'unknown')
            streams_list.append({
                "url": url,
                "quality": s.get('quality', 'unknown'),
                "protocol": protocol,
                "priority": 1 if s.get('quality') == '1080p' else (2 if s.get('quality') == '720p' else 3),
                "last_checked": None,
                "is_working": None
            })

        # ترتيب الروابط حسب الأولوية
        streams_list.sort(key=lambda x: x['priority'])

        # الشعار
        logo_url = None
        ch_logos = logos_by_channel.get(ch_id, [])
        if ch_logos:
            # تفضيل الشعار الأفقي
            for lg in ch_logos:
                if 'horizontal' in lg.get('tags', []):
                    logo_url = lg.get('url')
                    break
            if not logo_url:
                logo_url = ch_logos[0].get('url')

        # الكود
        code = generate_code(ch.get('name', 'UNKNOWN'), ch.get('country', 'XX'), existing_codes)
        existing_codes.add(code)

        # اللغة الأولى
        languages = ch.get('languages', [])
        lang = languages[0] if languages else 'unknown'

        # التصنيف الأول
        categories = ch.get('categories', [])
        category = categories[0] if categories else 'general'

        channel_data = {
            "id": ch_id,
            "code": code,
            "index": index,
            "tvg_id": f"{ch.get('name', '').replace(' ', '')}.{ch.get('country', '').lower()}",
            "tvg_chno": 100 + index,
            "name_ar": ch.get('name', ''),  # يمكن تحسينه لاحقاً
            "name_en": ch.get('name', ''),
            "country": ch.get('country', ''),
            "language": lang,
            "category": category,
            "logo": logo_url,
            "website": ch.get('website'),
            "priority": 1,
            "last_checked": None,
            "is_working": None,
            "streams": streams_list
        }
        all_channels.append(channel_data)
        index += 1

        if CHANNEL_LIMIT > 0 and len(all_channels) >= CHANNEL_LIMIT:
            break

    print(f"  تمت معالجة {len(all_channels)} قناة")

    # 4. تجميع حسب الدولة
    print("\n[4/5] تجميع القنوات حسب الدولة...")
    channels_by_country = defaultdict(list)
    for ch in all_channels:
        country = ch.get('country', 'XX')
        channels_by_country[country].append(ch)

    # 5. حفظ الملفات
    print("\n[5/5] حفظ الملفات...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ملف الفهارس العام
    master_index = {
        "version": "1.0.0",
        "total_channels": len(all_channels),
        "countries": [
            {
                "code": code,
                "name_en": countries_map.get(code, {}).get('name', code),
                "name_ar": countries_map.get(code, {}).get('name', code),
                "flag": countries_map.get(code, {}).get('flag', '🏳️'),
                "channel_count": len(chs)
            }
            for code, chs in sorted(channels_by_country.items())
        ],
        "categories": [
            {"id": cid, "name": cat.get('name', cid)}
            for cid, cat in categories_map.items()
        ]
    }
    with open(f"{OUTPUT_DIR}/index.json", 'w', encoding='utf-8') as f:
        json.dump(master_index, f, ensure_ascii=False, indent=2)
    print(f"  ✅ index.json ({len(master_index['countries'])} دولة)")

    # ملف لكل دولة
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
    print("=" * 60)

if __name__ == '__main__':
    build_channels()
