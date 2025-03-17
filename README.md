# OpenAI API 기반 뉴스 인사이트 얻기

## Requirements
```
- Anaconda
- Python 3.11
- 기타 Python 패키지 (requrements.txt) 참조
```

## Description
Google News에서 크롤링한 뉴스 헤드라인에서 OpenAI API를 활용하여 인사이트 얻기<br>
기타 자세한 설명은 아래 블로그 참고
- [OpenAI API를 활용한 관심 있는 주제에 대한 뉴스 인사이트 얻기]()

## Run
```
python main.py
```
```
news_list = list()
with GoogleNewsCrawler() as crawler:
    q_list = [
        {
            'q': 'economy',
            'time': '4h',
            'location': 'us'
        },
        {
            'q': '국내 경제',
            'time': '4h',
            'location': 'ko'
        }
    ]
    for q in q_list:
        news = crawler.crawl(q)
        news_list += news
print_log(news_list)
save_to_json(news_list)
```
- main.py 코드 내에서 `q_list` 내용 변경 후 실행
- 크롤링 결과는 `save_to_json` 함수를 사용하여 json 파일로 저장
- 결과 샘플 파일: `news_data.json`