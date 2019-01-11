from crawler import PttSpider, ArticleInfo
import sys

if __name__ == "__main__":
    # python app.py [版名] [爬幾頁]
    # python app.py soft_job 3
    board, page_term = sys.argv[1], int(sys.argv[2])
    # board, page_term = 'soft_job', 2  # for debugger
    print("開始爬 ptt {} 版...".format(board))
    spider = PttSpider(board=board,
                       parser_page=page_term)
    spider.run()
    print("下載完畢...")
    print("檔案處理中...")
    info = ArticleInfo.data_process(spider.info, spider.board)
    print("完成...")
