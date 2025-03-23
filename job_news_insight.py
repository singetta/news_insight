import os
import json
import re
import shutil
import time
import schedule
from datetime import datetime
from datetime import timezone
from crawlers import print_log
from crawlers import GoogleNewsCrawler
from crawlers import save_to_json
from crawlers import get_latest_news_data
from openai_api import chat_request_news_insight


def get_news_insight_config(file_path):
    keyword_list = list()
    time_data = ''
    location = ''
    if os.path.isfile(file_path):
        print_log('Get Keyword List')
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
        if len(lines) > 0:
            keyword_list = lines[0].split(';')
            time_data = lines[1]
            location = lines[2]
    return keyword_list, time_data, location


def set_news_insight_config(keyword_list, time_data, location, file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
    with open(file_path, 'w') as f:
        f.write(f'{keyword_list}\n{time_data}\n{location}')


def job_news_insight():
    keyword_list, time_data, location = get_news_insight_config('news_insight_config.txt')
    print_log('Keyword List: {}'.format(keyword_list))
    print_log('Time: {}'.format(time_data))
    print_log('Location: {}'.format(location))

    if len(keyword_list) == 0:
        print_log('No Keyword List')
        return False

    print_log('Get Latest News Headlines')

    query_list = list()
    for keyword in keyword_list:
        query_list.append({
            'q': keyword,
            'time': time_data,
            'location': location
        })

    news_list = list()
    if not os.path.exists('news_data'):
        os.makedirs('news_data')
    else:
        shutil.rmtree('news_data')
        os.makedirs('news_data')

    with GoogleNewsCrawler() as crawler:
        for query in query_list:
            news = crawler.crawl(query)
            seen_news = set()
            unique_news = list()
            for news_item in news:
                if news_item['title'] not in seen_news:
                    unique_news.append(news_item)
                    seen_news.add(news_item['title'])
            seen_news.clear()
            news_list.append(unique_news)

    for keyword, news_item in zip(keyword_list, news_list):
        news_headline_list = [{'title': item} for item in news_item]

        contents = [f'keyword: {keyword}',
                    f'news headlines: {json.dumps(news_headline_list)}',
                    f'response language: {location}']
        ins_path = os.path.join('instructions', 'news_instructions.md')
        result = chat_request_news_insight(ins_path, contents)
        result = re.sub(r'\n+', ' ', result['news_insight'])
        print_log(f'keyword: {keyword}, news insight: {result}')
        unix_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        save_to_json({
            'keyword': keyword,
            'news_insight': result,
            'news_data': news_item
        }, os.path.join('news_data', f'{unix_time_ms}_news_headline.json'))
    return True


def job_news_insight_schedule():
    max_retry = 2
    retries = 0
    for retry in range(max_retry):
        print_log(f'{retry} Get News Insight')
        retries += 1
        try:
            rr = job_news_insight()
            if rr:
                break
            else:
                continue
        except Exception as e:
            print_log(f'Error occurred in news insight script: {e}')
            time.sleep(10)

    if retries >= max_retry:
        print_log(f'Max retries exceeded')


if __name__ == '__main__':
    _, time_data, _ = get_news_insight_config('news_insight_config.txt')
    time_data = time_data[:-1]
    time_data = int(time_data)
    print_log(f'Schedule Interval: {time_data}')
    job_news_insight_schedule()

    for hour in range(0, 24, time_data):
        time_info = f'{hour:02d}:00'
        schedule.every().day.at(time_info).do(job_news_insight_schedule)

    while True:
        schedule.run_pending()
        time.sleep(10)
