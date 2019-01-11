import sys
import requests
import json
import urllib3
import logging

from bs4 import BeautifulSoup

urllib3.disable_warnings()
logging.basicConfig(level=logging.WARNING)
HTTP_ERROR_MSG = 'HTTP error {res.status_code} - {res.reason}'


class PttSpider:
    rs = requests.session()
    ptt_head = 'https://www.ptt.cc'
    ptt_middle = 'bbs'
    parser_page_count = 5

    def __init__(self, **kwargs):
        self._board = kwargs.get('board', None)
        self.parser_page = int(kwargs.get('parser_page', self.parser_page_count))

        self._soup = None
        self._index_seqs = None
        self._articles = []

    @property
    def info(self):
        return self._articles

    @property
    def board(self):
        return self._board.capitalize()

    def run(self):
        self._soup = self.check_board()
        self._index_seqs = self.parser_index()
        self._articles = self.parser_per_article_url()
        self.analyze_articles()
        self.crawler_data()

    def check_board(self):
        print('check board......')
        if self._board:
            return self.check_board_over18()
        else:
            print("請輸入看版名稱")
            sys.exit()

    def check_board_over18(self):
        load = {
            'from': '/{}/{}/index.html'.format(self.ptt_middle, self._board),
            'yes': 'yes'
        }
        try:
            res = self.rs.post('{}/ask/over18'.format(self.ptt_head), verify=False, data=load)
            res.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            logging.warning(HTTP_ERROR_MSG.format(res=exc.response))
            raise Exception('網頁有問題')
        return BeautifulSoup(res.text, 'html.parser')

    def parser_index(self):
        print('parser index......')
        max_page = self.get_max_page(self._soup.select('.btn.wide')[1]['href'])
        return (
            '{}/{}/{}/index{}.html'.format(self.ptt_head, self.ptt_middle, self._board, page)
            for page in range(max_page - self.parser_page + 1, max_page + 1, 1)
        )

    def parser_per_article_url(self):
        print('parser per article url......')
        articles = []
        for page in self._index_seqs:
            try:
                res = self.rs.get(page, verify=False)
                res.raise_for_status()
            except requests.exceptions.HTTPError as exc:
                logging.warning(HTTP_ERROR_MSG.format(res=exc.response))
            except requests.exceptions.ConnectionError:
                logging.error('Connection error')
            else:
                articles += self.crawler_info(res)
        return articles

    def analyze_articles(self):
        for article in self._articles:
            try:
                logging.debug('{}{} ing......'.format(self.ptt_head, article.url))
                res = self.rs.get('{}{}'.format(self.ptt_head, article.url), verify=False)
                res.raise_for_status()
            except requests.exceptions.HTTPError as exc:
                logging.warning(HTTP_ERROR_MSG.format(res=exc.response))
            except requests.exceptions.ConnectionError:
                logging.error('Connection error')
            else:
                article.res = res

    @staticmethod
    def check_format(soup, class_tag, index):
        # 避免有些文章會被使用者自行刪除 標題列 時間  之類......
        content = None
        try:
            content = soup.select(class_tag)[index].text
        except Exception as e:
            # print('checkformat error URL', link)
            logging.warning(e)
        return content

    @staticmethod
    def crawler_content(soup, time):
        main_content = None
        try:
            content = soup.find(id="main-content").text
            target_content = '※ 發信站: 批踢踢實業坊(ptt.cc),'
            content = content.split(target_content)
            content = content[0].split(time)
            main_content = content[1].replace('\n', '  ').strip()
        except Exception as e:
            logging.warning(e)
        return main_content

    def crawler_data(self):
        for data in self._articles:
            print('crawler data......')
            soup = BeautifulSoup(data.res.text, 'html.parser')
            data.time = self.check_format(soup, '.article-meta-value', 3)
            if data.time:
                data.content = self.crawler_content(soup, data.time)

    @staticmethod
    def crawler_info(res):
        logging.debug('crawler_info......{}'.format(res.url))
        soup = BeautifulSoup(res.text, 'html.parser')
        articles = []
        for r_ent in soup.find_all(class_="r-ent"):
            try:
                # 得到每篇文章的 url
                url = r_ent.find('a')['href']
                if not url:
                    continue
                title = r_ent.find(class_="title").text.strip()
                author = r_ent.find(class_="author").text.strip()
                articles.append(ArticleInfo(
                    title=title, author=author, url=url))
            except Exception as e:
                logging.debug('本文已被刪除')
                logging.debug(e)
        return articles

    @staticmethod
    def get_max_page(content):
        start_index = content.find('index')
        end_index = content.find('.html')
        page_number = content[start_index + 5: end_index]
        return int(page_number) + 1


class ArticleInfo:
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', None)
        self.author = kwargs.get('author', None)
        self.url = kwargs.get('url', None)
        self.time = kwargs.get('time', None)
        self.content = None
        self.res = None

    @staticmethod
    def data_process(info, board):
        data = []
        for article in info:
            data.append(
                {
                    "日期": article.time,
                    "作者": article.author,
                    "標題": article.title,
                    "內文": article.content,
                    "看板名稱": board
                }
            )
        json_data = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
        with open('result.txt', 'a', encoding='utf-8') as f:
            f.write(json_data)
