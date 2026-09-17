import json
import requests
import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

# --- الإعدادات ---
DATA_DIR = "data"
MAX_WORKERS = 50
TIMEOUT = 10
USER_AGENT = "VLC/3.0.14 LibVLC/3.0.14"

def check_url(url):
    """فحص ما إذا كان رابط البث يعمل"""
    if not url or not isinstance(url, str) or not url.startswith('http'):
        return False

    headers = {'User-Agent': USER_AGENT}
    try:
        # نجرب HEAD أولاً (أسرع)
        with requests.head(url, headers=headers, timeout=TIMEOUT, allow_redirects=True) as response:
            if response.status_code == 200:
                return True
            # بعض السيرفرات لا تدعم HEAD، نجرب GET
            if response.status_code in (405, 403):
                with requests.get(url, headers=headers, timeout=TIMEOUT, stream=True) as r:
                    return r.status_code == 200
            return False
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.RequestException:
        return False
    except Exception:
        return False

def load_all_channels():
    """تحميل كل القنوات من ملفات الدول"""
    all_channels = []
    pattern = os.path.join(DATA_DIR, "channels_*.json")
    for filepath in glob.glob(pattern):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for ch in data.get('channels', []):
                all_channels.append((filepath, ch))
        except Exception as e:
            print(f"  خطأ في تحميل {filepath}: {e}")
    return all_channels

def check_and_update():
    print("=" * 60)
    print("بدء فحص الروابط")
    print("=" * 60)

    all_channels = load_all_channels()
    if not all_channels:
        print("لا توجد قنوات للفحص.")
        return False

    print(f"  تم تحميل {len(all_channels)} قناة من {len(set(f for f, _ in all_channels))} ملف")

    # جمع كل الروابط الفريدة للفحص
    unique_urls = set()
    for _, ch in all_channels:
        for stream in ch.get('streams', []):
            url = stream.get('url')
            if url:
                unique_urls.add(url)

    print(f"  عدد الروابط الفريدة: {len(unique_urls)}")
    print("  جاري الفحص (قد يستغرق بضع دقائق)...")

    # فحص متزامن
    results = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(check_url, url): url for url in unique_urls}
        completed = 0
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception:
                results[url] = False
            completed += 1
            if completed % 500 == 0:
                print(f"    تم فحص {completed}/{len(unique_urls)}...")

    # تحديث الملفات
    now_iso = datetime.now(timezone.utc).isoformat()
    updated_count = 0
    files_updated = set()

    for filepath, ch in all_channels:
        for stream in ch.get('streams', []):
            url = stream.get('url')
            if url in results:
                is_working = results[url]
                if stream.get('is_working') != is_working:
                    updated_count += 1
                stream['is_working'] = is_working
                stream['last_checked'] = now_iso

    # إعادة حفظ الملفات المعدلة
    # (نجمع القنوات حسب الملف أولاً)
    files_data = {}
    for filepath, ch in all_channels:
        if filepath not in files_data:
            with open(filepath, 'r', encoding='utf-8') as f:
                files_data[filepath] = json.load(f)

    # تحديث بيانات كل ملف
    for filepath, ch in all_channels:
        # البحث عن القناة في بيانات الملف وتحديثها
        for existing_ch in files_data[filepath]['channels']:
            if existing_ch['id'] == ch['id']:
                existing_ch['streams'] = ch['streams']
                existing_ch['last_checked'] = now_iso
                existing_ch['is_working'] = any(s.get('is_working') for s in ch['streams'])
                break

    # حفظ الملفات
    for filepath, data in files_data.items():
        data['last_updated'] = now_iso
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        files_updated.add(filepath)

    # تحديث ملف الفهرس
    index_path = os.path.join(DATA_DIR, "index.json")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        index_data['last_updated'] = now_iso
        index_data['total_working_channels'] = sum(
            1 for _, ch in all_channels if any(s.get('is_working') for s in ch.get('streams', []))
        )
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"\n  ✅ تم فحص {len(unique_urls)} رابط")
    print(f"  ✅ تم تحديث {updated_count} رابط")
    print(f"  ✅ تم تحديث {len(files_updated)} ملف")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = check_and_update()
    if not success:
        exit(1)
