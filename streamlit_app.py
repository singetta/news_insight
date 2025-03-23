import streamlit as st
import time
from crawlers import get_latest_news_data, rerun_script
from job_news_insight import get_news_insight_config
from job_news_insight import set_news_insight_config

use_text_input = False


def show_toast_message(message, is_success):
    if is_success:
        toast_widget = st.success(message)
    else:
        toast_widget = st.error(message)
    time.sleep(3)
    toast_widget.empty()


def main():
    st.set_page_config(
        layout="wide",
        page_title="최신 뉴스 인사이트",
        page_icon="📰",
        initial_sidebar_state="collapsed",
    )
    st.header("최신 뉴스 크롤링 및 OpenAI 기반 인사이트 얻기")
    side_col, main_col = st.columns([2, 8], border=True)
    with side_col:
        st.subheader("검색 쿼리")
        keyword_list, time_data, location = get_news_insight_config('news_insight_config.txt')
        keyword_str = ';'.join(keyword_list)
        new_keyword = st.text_input("키워드", keyword_str if len(keyword_list) > 0 else ';으로 키워드 추가',
                                    disabled=use_text_input)
        new_time_data = st.text_input("검색 주기", time_data if time_data != '' else 'xd(날짜), xh(시간)',
                                      disabled=use_text_input)
        new_location = st.selectbox("지역", ['us', 'ko'], index=0, disabled=use_text_input)
        if st.button("저장", use_container_width=True):
            try:
                set_news_insight_config(new_keyword, new_time_data, new_location, 'news_insight_config.txt')
                show_toast_message("저장 완료", True)
                process_id = rerun_script('job_news_insight')
                show_toast_message(f'{process_id} 재실행 완료', True)
            except Exception as e:
                show_toast_message(str(e), False)

    with main_col:
        st.subheader("검색 결과")
        news_insight_list = get_latest_news_data()
        keyword_list = [item['keyword'] for item in news_insight_list]
        st_tab_list = st.tabs(keyword_list)
        for news_insight, st_tab in zip(news_insight_list, st_tab_list):
            with st_tab:
                st.subheader(f'인사이트 ({news_insight["time"]})')
                st.markdown(f'- {news_insight["insight"]}')
                st.subheader(f'뉴스 헤드라인 ({news_insight["time"]})')
                if news_insight['news'] is not None:
                    st.dataframe(news_insight['news'], hide_index=True, column_config={
                        'date': st.column_config.Column(
                            '날짜',
                            width='small',
                            disabled=True
                        ),
                        'title': st.column_config.Column(
                            '헤드라인',
                            width='large',
                            disabled=True
                        ),
                        'url': st.column_config.LinkColumn(
                            'url',
                            display_text='🔗',
                            width='small',
                            disabled=True
                        )
                    }, use_container_width=True, height=500)
                else:
                    st.write("No news data to display.")


if __name__ == '__main__':
    main()
