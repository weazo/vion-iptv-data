import json
import requests
import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

# ==================== الإعدادات ====================
DATA_DIR = "data"
MAX_WORKERS = 50
TIMEOUT = 8
USER_AGENT = "VLC/3.0.14 LibVLC/3.0.14"

# ==================== دوال الفحص ====================
def check_url(url):
    """فحص إذا كان رابط البث يعمل"""
    if not url or not isinstance(url, str) or not url.startswith('http'):
        return False

    headers = {'User-Agent': USER_AGENT}
    try:
        # نجرب HEAD أولاً (أسرع)
        r = requests.head(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code == 200:
            return True
        # بعض السيرفرات لا تدعم HEAD، نجرب GET
        if r.status_code in (403, 405):
            with requests.get(url, headers=headers, timeout=TIMEOUT, stream=True) as r2:
                return r2.status_code == 200
        return False
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.RequestException:
        return False
    except Exception:
        return False

# ==================== الدالة الرئيسية ====================
def check_and_update():
    print("=" * 60)
    print("فحص الروابط")
    print("=" * 60)

    # 1. جمع كل الملفات
    files = glob.glob(os.path.join(DATA_DIR, "channels_*.json"))
    if not files:
        print("❌ لا توجد ملفات للفحص. شغّل build_channels.py أولاً.")
        return False

    print(f"\n[1/4] تحميل {len(files)} ملف...")

    # 2. جمع كل الروابط الفريدة
    all_data = {}
    unique_urls = set()

    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            all_data[filepath] = data
            for ch in data.get('channels', []):
                for s in ch.get('streams', []):
                    url = s.get('url')
                    if url:
                        unique_urls.add(url)
        except Exception as e:
            print(f"  خطأ في {filepath}: {e}")

    print(f"  ✅ تم تحميل {len(all_data)} ملف")
    print(f"  ✅ عدد الروابط الفريدة: {len(unique_urls)}")

    # 3. فحص الروابط بشكل متزامن
    print(f"\n[2/4] فحص الروابط (بالتزامن {MAX_WORKERS})...")
    results = {}
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_url, url): url for url in unique_urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                results[url] = future.result()
            except Exception:
                results[url] = False
            completed += 1
            if completed % 500 == 0:
                print(f"  تقدم: {completed}/{len(unique_urls)}")

    working_count = sum(1 for v in results.values() if v)
    print(f"  ✅ {working_count}/{len(unique_urls)} رابط يعمل")

    # 4. تحديث الملفات
    print(f"\n[3/4] تحديث الملفات...")
    now_iso = datetime.now(timezone.utc).isoformat()
    updated_files = 0

    for filepath, data in all_data.items():
        for ch in data.get('channels', []):
            channel_working = False
            for s in ch.get('streams', []):
                url = s.get('url')
                if url in results:
                    s['is_working'] = results[url]
                    s['last_checked'] = now_iso
                    if results[url]:
                        channel_working = True
            ch['is_working'] = channel_working
            ch['last_checked'] = now_iso

        data['last_updated'] = now_iso
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        updated_files += 1

    print(f"  ✅ تم تحديث {updated_files} ملف")

    # 5. تحديث index.json
    print(f"\n[4/4] تحديث index.json...")
    index_path = os.path.join(DATA_DIR, "index.json")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)

        # عد القنوات العاملة
        total_working = 0
        for filepath, data in all_data.items():
            for ch in data.get('channels', []):
                if ch.get('is_working'):
                    total_working += 1

        index_data['last_updated'] = now_iso
        index_data['total_working_channels'] = total_working
        index_data['total_broken_channels'] = index_data.get('total_channels', 0) - total_working

        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ index.json محدّث")

    print("\n" + "=" * 60)
    print(f"✅ اكتمل الفحص! {working_count}/{len(unique_urls)} رابط يعمل")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = check_and_update()
    if not success:
        exit(1)
