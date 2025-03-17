from crawlers import *


def main():
    print_log("Starting crawling...")
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


if __name__ == '__main__':
    main()
