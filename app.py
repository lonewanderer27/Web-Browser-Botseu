from dataclasses import replace
from multiprocessing.sharedctypes import Value
import os
import json
from flask import Flask, Response, jsonify, request, redirect, abort
from newspaper import Article, Config
import requests
from bs4 import BeautifulSoup
import google_custom_search
from duckduckgo_search import ddg
import textwrap
from pprint import pprint

# ENVIRON VARIABLES
cw_link = os.environ.get('cw_link', 'https://m.informativestore.com/the-amazing-son-in-law-chapter-list')
gg_custom_search_api_key = os.environ.get('gg_custom_search_api_key', None)
gg_custom_search_engine_id = os.environ.get('gg_custom_search_engine_id', None)
app_homepage_url = os.environ.get('app_homepage_url', 'https://lonewanderer27.github.io/web-browser-botseu/')

# NEWSPAPER CONFIG
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0'
config = Config()
config.browser_user_agent = user_agent
config.request_timeout = 10

# GENERAL LAYOUT
users = {
    123456: {
        'current_results': [
            {"url": "www.xyz.com", "title": "Alphabet Inc.", "text": "Alphabet Inc. is an American multinational technology conglomerate holding company headquartered in Mountain View, California. It was created through a restructuring of Google on October 2, 2015, and became the parent company of Google and several former Google subsidiaries."},
            {"url": "www.google.com", "title": "Google", "text": "This is a short snippet of the website"}
        ],
        'history': [
            {"url": "www.xyz.com", "title": "Alphabet Inc.", "snippet": "This is a short snippet of the website"},
            {"url": "www.google.com", "title": "Google", "snippet": "This is a short snippet of the website"}
        ]
    }
}

# DB
db = {}

# FUNCTIONS FOR ARTICLE PROCESSING

def get_article(url: str) -> object:
    article = Article(url, config)
    article.download()
    article.parse()
    return article

def get_article_text(article: object) -> str:
    return article.text

def get_article_author(article: object) -> list:
    return article.authors

def get_article_publish_date(article: object) -> list:
    return article.publish_date


# FUNCTIONS FOR CHARLIE WADE

def get_cw_site_links():
    page = requests.get(cw_link)
    soup = BeautifulSoup(page.content, 'html.parser')
    a_classes = soup.find_all("a",class_='wp-block-button__link')
    return a_classes

def get_cw_chapters() -> str:
    chapters = ''
    for chapter in get_cw_site_links():
        if chapter.text != 'Join Telegram Group For Fast Update':
            chapters += f"{chapter.text}"
    return chapters

def get_cw_chapter_link(chapter):
    for chapter in get_cw_site_links():
        if chapter.text == str(chapter):
            return chapter['href']

def get_cw_chapter(chapter: str) -> str:
    link = get_cw_chapter_link(chapter)
    return get_article_text(get_article(link))

def get_cw_latest_chapter_link():
    return get_cw_site_links()[-2]['href']

def get_cw_latest_chapter() -> str:
    link = get_cw_latest_chapter_link()
    return get_article_text(get_article(link))


# GENERAL FUNCTIONS !!!

def verify_environ_vars():
    if not gg_custom_search_api_key:
        raise NameError('gg_custom_search_api_key not found in environment variables')
    if not gg_custom_search_engine_id:
        raise NameError('gg_custom_search_engine_id not found in environment variables')

def split_message(json, text, n: 9):
    if n != 9:
        n = round(len(text) / 9)    # makes sure that all the message is split evenly across 9 messages
    text_blocks = textwrap.wrap(text, width=n, break_long_words=False, break_on_hyphens=False, drop_whitespace=True, replace_whitespace=False)
    for text_block in text_blocks:
        json['messages'].append({'text': f'{text_block}'},)
    return json

def arg_is_none(message: str):
    print(f'Error 400: {message}')
    return Response(
        message,
        status=400
    )


# FUNCTIONS FOR DB !!!

def init_db() -> None:
    if 'users' in db:
        print('DB already initialized, continuing')
    else:
        print('DB not ready')
        print('init DB') 
        db['users'] = {}

def user_exists(user_id) -> bool:
    try:
        if user_id in db['users']:
            return True
        else:
            return False
    except KeyError: 
        return False

def add_user(user_id) -> None:
    if not user_exists(user_id):
        db['users'][user_id] = {
            'current_results': [],
            'current_article': {},
            'history': []
        }

def add_user_history(url, title, user_id) -> None:
    db['users'][user_id]['history'].append(
        {'url': url, 'title': title}
    )


# FUNCTIONS FOR DUCKDUCKGO SEARCH !!!

def search_ddg(query):
    return ddg(keywords=query, region='ph')

def add_to_current_results(result, user_id) -> None:
    result_amt = 9

    db['users'][user_id]['current_results'].clear()

    count = 0
    while count < result_amt:
        db['users'][user_id]['current_results'].append(
            {
                'url': result[count]['href'],
                'title': result[count]['title'],
                'snippet': result[count]['body']
            },)
        count += 1

def encode_current_results(user_id):
    current_results = {
        'messages': [
            {'text': "These are what we've found!"}
        ]
    }

    count = 0
    for result in db['users'][user_id]['current_results']:
        count += 1
        text_block = ''
        text_block += f"[{count}]\n\n{result['title']}\n{result['url']}\n\n{result.get('snippet', '')}"
        current_results['messages'].append({'text': f'{text_block}'},)

    return current_results

def get_article_text_from_ddg_search_result(search_result: int, user_id):
    # search result num     |       actual num on the list
    #       0                               1
    #       1                               2
    #       2                               3
    # and so on...
    url = db['users'][user_id]['current_results'][search_result -1]['url']
    return get_article_text(get_article(url))


app = Flask(__name__)


@app.route('/')
def index():
    return redirect(app_homepage_url)

@app.route('/charlie_wade/')
def charlie_wade():
    rqst = request.args.get('request', None)

    print('/charlie_wade/ triggered')

    if rqst == 'chapter':
        return 'Charlie Wade Chapter'

    elif rqst == 'chapters':
        return 'Charlie Wade Chapters'

    elif rqst == 'latest_chapter':
        return 'Latest Charlie Wade Chapter'

    else:
        abort(404)

@app.route('/search/')
def search():
    print('/search/ triggered')

    rqst = request.args.get('request', None)
    query = request.args.get('query', None)
    user_id = request.args.get('user_id', None)

    if not rqst:
        return arg_is_none('Error: request is None')

    if not query:
        return arg_is_none('Error: query is None')
    
    if not user_id:
        return arg_is_none('Error: user_id is None')

    add_user(user_id)

    if rqst == 'search_ddg':
        print('search_ddg triggered')

        result = search_ddg(query)
        print(f'result: {result}')

        add_to_current_results(result, user_id)

        encoded_results = encode_current_results(user_id)
        print(f'encoded_results: {encoded_results}')

        json = jsonify(encoded_results)
        return json

    else:
        abort(404)


if __name__ == '__main__':
    # verify_environ_vars()
    init_db()

    app.secret_key = os.urandom(12)
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)      