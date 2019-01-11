from bs4 import BeautifulSoup
from flask import Flask
import requests
import random
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.WARNING)


@app.route("/", methods=['GET'])
def home():
    target_url = 'https://en.wikipedia.org/wiki/Zen_of_Python'
    rs = requests.session()

    try:
        res = rs.get(target_url, verify=False)
        res.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        logging.warning(exc)
        raise Exception('網頁有問題')
    else:
        soup = BeautifulSoup(res.text, 'html.parser')
    return random.choice(soup.select('.poem')[0].text.strip().split('\n'))


if __name__ == '__main__':
    # http://127.0.0.1:5000/
    app.run(debug=True)
