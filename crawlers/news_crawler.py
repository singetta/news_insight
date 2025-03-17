import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .base_crawler import BaseCrawler
from .utility import parse_datetime
from .utility import print_log


class GoogleNewsCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = "https://news.google.com/search"

    def scroll_to_bottom(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        max_retries = 4
        retry = 0
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height or retry >= max_retries:
                break
            last_height = new_height
            retry += 1

    def get_news_details(self, article_url):
        try:
            self.driver.execute_script(f"window.open('{article_url}');")
            self.driver.switch_to.window(self.driver.window_handles[-1])

            title = None
            selectors = [
                "h1",
                ".headline",
                "article h1",
                "[class*='title']"
            ]

            for selector in selectors:
                try:
                    element = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    title = element.text
                    if title:
                        break
                except:
                    continue

            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

            return title

        except Exception as e:
            print_log(f"Error getting article details: {str(e)}")
            return None

    def get_url(self, query):
        url = self.base_url
        if 'q' in query:
            url += f"?q={query['q']}"
        if 'time' in query:
            url += f"%20when%3A{query['time']}"
        if 'location' in query:
            if query['location'] == 'ko':
                lang = 'KR'
            elif query['location'] == 'jp':
                lang = 'JP'
            elif query['location'] == 'us':
                lang = 'EN'
            else:
                raise Exception(f"Unknown location: {query['location']}")
            url += f"&hl={query['location']}&gl={lang}&ceid={lang}%3A{query['location']}"
        return url

    def crawl(self, query, max_count=50):
        query_url = self.get_url(query)

        try:
            self.driver.get(query_url)
            self.scroll_to_bottom()

            news_data = []

            articles = self.driver.find_elements(By.XPATH, "//article")
            for article in articles:
                try:
                    a_tag_value = (".//a[@href and string-length(text()) > 0 and (contains(@href, './articles/') or "
                                   "contains(@href, './read/'))]")
                    link_element = article.find_element(By.XPATH, a_tag_value)
                    time_element = article.find_element(By.XPATH, ".//time")

                    title = link_element.text
                    article_url = link_element.get_attribute("href")

                    if title == '':
                        title = link_element.accessible_name

                    if title == '' and article_url is not None:
                        title = self.get_news_details(article_url)

                    date_str = time_element.get_attribute("datetime")
                    formatted_date = parse_datetime(date_str)

                    if title and formatted_date:  # 둘 다 있는 경우만 추가
                        news_data.append({
                            "title": title,
                            "date": formatted_date,
                            "url": article_url if article_url is not None else ''
                        })

                except Exception as e:
                    print_log(f"Error processing news item: {str(e)}")
                    continue
            news_data.sort(key=lambda x: x['date'], reverse=True)
            if len(news_data) > max_count:
                news_data = news_data[0:max_count]
            print_log(f"Found {len(news_data)} articles")
            return news_data

        except Exception as e:
            print_log(f"Error during crawling: {str(e)}")
            return []
