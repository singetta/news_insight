import os
import pandas as pd
import json
import subprocess
import time
from datetime import datetime
from dateutil import parser
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

env = dict(os.environ)
load_dotenv()

conda_python_path = os.getenv('CONDA_PYTHON_PATH')


def _run_shell(cmd, cwd=None):
    print_log(f'COMMAND: {cmd}')
    rr = subprocess.check_output(cmd, text=True, cwd=cwd, shell=True, env=env, timeout=10)
    return rr


def get_script_process_id(script_name):
    try:
        result = _run_shell('ps aux')
        for line in result.splitlines():
            if script_name in line:
                return int(line.split()[1])
        return -1
    except Exception as e:
        print_log(f'Error in get_cron_script_process_id: {e}')


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


def get_latest_news_data():
    root_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    full_path_news_directory = os.path.join(root_directory, 'news_data')
    file_list = os.listdir(full_path_news_directory)
    file_list = sorted(file_list, reverse=True)

    if len(file_list) == 0:
        news_insight_info = {
            'keyword': '',
            'insight': 'news insight is not available',
            'time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'news': None
        }
        return [news_insight_info]

    news_insight_list = list()
    for file_name in file_list:
        news_data = json.load(open(os.path.join(full_path_news_directory, file_name)))
        keyword = news_data['keyword']
        insight = news_data['news_insight']
        time_data = file_name.split('_')[0]
        unix_timestamp_ms = float(time_data)
        unix_timestamp = unix_timestamp_ms / 1000
        dt = datetime.fromtimestamp(unix_timestamp)
        time_data = dt.strftime('%Y-%m-%dT%H:%M:%S')
        data = pd.DataFrame(news_data['news_data'])
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values(by='date', ascending=False)
        data = data[['date', 'title', 'url']]
        data['date'] = data['date'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        news_insight_list.append({
            'keyword': keyword,
            'insight': insight,
            'time': time_data,
            'news': data
        })
    return news_insight_list


def rerun_script(script_name):
    try:
        process_id = get_script_process_id(script_name)
        if process_id > 0:
            _run_shell(f'kill -9 {process_id}')
            time.sleep(1)
        root_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        full_script_path = os.path.join(root_directory, f'{script_name}.py')
        full_log_path = os.path.join(root_directory, f'{script_name}_log.log')
        _run_shell([f'nohup {conda_python_path} {full_script_path} > {full_log_path} 2>&1 &', 'disown'])
    except Exception as e:
        print_log(f'Error in rerun_cron_script: {e}')
