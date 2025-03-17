import json
from datetime import datetime
from dateutil import parser
from zoneinfo import ZoneInfo


def print_log(info):
    utc_time = datetime.now(ZoneInfo("UTC"))
    kst_time = utc_time.astimezone(ZoneInfo("Asia/Seoul"))
    timestamp = kst_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    print(f'[{timestamp}] {info}', flush=True)


def parse_datetime(time_str):
    try:
        dt = parser.parse(time_str)
        kst_dt = dt.astimezone(ZoneInfo('Asia/Seoul'))
        return kst_dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None


def save_to_json(data, filename="news_data.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
