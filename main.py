import json
import os
from flask import Flask, request, render_template
from newspaper import Article, Config
import requests
from bs4 import BeautifulSoup
import google_custom_search
from duckduckgo_search import ddg
import textwrap
from replit import db as replit_db
from pprint import pprint

# del replit_db['users']
# with open('my_all_around_husband.json', 'r') as my_all_around_husband_json:
#     replit_db['my_all_around_husband'] = dict(json.load(my_all_around_husband_json))

cw_link = os.environ.get('cw_link', None)
google_custom_search_api_key = os.environ.get('google_custom_search_api_key', None)
google_custom_search_engine_id = os.environ.get('google_custom_search_engine_id', None)
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0'
config = Config()
config.browser_user_agent = user_agent
config.request_timeout = 10

def verify_environ_variables():
    if not cw_link:
        print("WARN: Charlie Wade Link is not present.")
    if not google_custom_search_api_key:
        print("ERROR: Programmable Search Engine API Key not found in Environment Variables")
        print("You may go to https://developers.google.com/custom-search to know how to get one.")
        return quit()
    if not google_custom_search_engine_id:
        print("ERROR: Programmable Search Engine ID not found in Environment Variables")
        print("You may go to https://developers.google.com/custom-search to know how to get one.")
        return quit()

    print("Necessary credentials present, continuing...")
    return


def download_and_parse_article(url):
    article = Article(url=url, config=config)
    article.download()
    article.parse()
    return article


def get_article_text(url):
    article = download_and_parse_article(url)
    article_text = article.text
    return article_text


def get_available_my_all_around_husband_pages_num():
    # chapters_num = len(replit_db['my_all_around_husband'])
    pages_text = ""
    for page in replit_db.get('my_all_around_husband'):
        if page != None:
            pages_text += f"{page} "
    return pages_text


def get_specific_my_all_around_husband_page_text(page_num):
    page_text = replit_db['my_all_around_husband'][page_num]
    return page_text


def get_available_charlie_wade_chapters_num():
    url = cw_link
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    a_classes = soup.find_all("a",class_='wp-block-button__link')
    chapters = ""
    for chapter in a_classes:
        if chapter.text != 'Join Telegram Group For Fast update':
            # print(chapter.text)
            chapters += f"{chapter.text} "

    # print(chapters)
    return chapters


def get_specific_charlie_wade_chapter_link(chapter_num):
    url = cw_link
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    a_classes = soup.find_all("a",class_='wp-block-button__link')
    for chapter in a_classes:
        if chapter.text == str(chapter_num):
            print(chapter.text)
            link = (chapter['href'])
            print(link)

    return link


def get_specific_charlie_wade_chapter_text(chapter_num):
    link = get_specific_charlie_wade_chapter_link(chapter_num)
    text = get_article_text(link)
    
    return text


def get_latest_charlie_wade_chapter_link():
    url = cw_link
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    a_classes = soup.find_all("a",class_='wp-block-button__link')
    print(type(a_classes))
    link = a_classes[-2]['href']

    return link


def get_latest_charlie_wade_chapter_text():
    link = get_latest_charlie_wade_chapter_link()
    text = get_article_text(link)
    
    return text


def split_message_cw(json, text, n):
    # special version of split message function, this allows manual control of n variable. - used for Charlie Wade
    print(n)
    text_blocks = textwrap.wrap(text, width=n, break_long_words=False, break_on_hyphens=False,drop_whitespace=False, replace_whitespace=False)

    for text_block in text_blocks:
        json['messages'].append({"text": f"{text_block}"}, )

    return json


def split_message(json, text, n):
    n = round(len(text) / 9)   # makes sure that all the message is split evenly across 9 messages
    print(n)
    text_blocks = textwrap.wrap(text, width=n, break_long_words=False, break_on_hyphens=False,drop_whitespace=True, replace_whitespace=False)

    for text_block in text_blocks:
        json['messages'].append({"text": f"{text_block}"}, )

    return json


def initialize_database():
    if 'users' in replit_db:
        print("Database is already initialized, continuing...")
    else:
        print("Database hasn't been set up")
        print("Initializing replit_db")
        replit_db['users'] = {}
    
    return


def check_database(replit_db):
    try:
        pprint(replit_db['users'])
    except:
        print("Database could not be set up. Please make sure this is running on Replit or provide the direct URL to the database.")
        quit()


# checks if the user exists
def check_if_user_exists(chatfuel_user_id):
    users = replit_db['users'].keys()
    if chatfuel_user_id in users:
        print("True")
        return True
    else:
        print("False")
        return False


# adding the user
def add_user(chatfuel_user_id):
    if check_if_user_exists(chatfuel_user_id) is True:
        print(f"{chatfuel_user_id} already exists. Continuing")
        return False
    else:
        print(f"{chatfuel_user_id} doesn't exist yet. Adding...")
        replit_db['users'][chatfuel_user_id] = {
            'last_google_search_results': [],
            'last_duckduckgo_search_results': [],
            'current_article_user_is_on': {},
            'user_browsing_history': []
        }

        return True


def search_on_duckduckgo(query):
    results = ddg(keywords=query, region='ph', max_results=9)
    return results


def add_to_last_duckduckgo_search_results(result, chatfuel_user_id):
    # if len(result) < 9:
    #     result_amount = len(result)
    # elif len(result) > 9:
    #     result_amount = 9
    # else:
    result_amount = 9

    count = 0
    replit_db['users'][chatfuel_user_id]['last_duckduckgo_search_results'] = []
    while count < result_amount:
        replit_db['users'][chatfuel_user_id]['last_duckduckgo_search_results'].append(
                {
                    "url": result[count]['href'],
                    "title": result[count]['title'],
                    "snippet": result[count]['body'],
                },
        )
        count += 1


def encode_duckduckgo_search_results(chatfuel_user_id):
    duckduckgo_search_results = {
        "messages": [
            {"text": "These are what we've found!"}
        ]
    }

    count = 0
    for entry in replit_db['users'][chatfuel_user_id]['last_duckduckgo_search_results']:
        count += 1
        text_block = ""
        text_block += f"[{count}] {entry['title']}\n"
        text_block += f"{entry['url']}\n\n"
        text_block += f"{entry.get('snippet', '')}"
        duckduckgo_search_results['messages'].append({"text": f"{text_block}"},)

    return duckduckgo_search_results


def get_article_text_from_duckduckgo_search_result_num(search_result_num, chatfuel_user_id):
    # search result num     |       actual num on the list
    #       0                               1
    #       1                               2
    #       2                               3
    # and so on...
    search_result_num = int(search_result_num) - 1
    url = replit_db['users'][chatfuel_user_id]['last_duckduckgo_search_results'][search_result_num]['url']
    article_text = get_article_text(url)
    return article_text


def search_on_google(query):
    google=google_custom_search.custom_search(apikey=google_custom_search_api_key, engine_id=google_custom_search_engine_id)
    result = google.search(query)

    return result


def add_to_last_google_search_results(result, chatfuel_user_id):
    # replit_db[chatfuel_user_id]['last_google_search_results']
    # print(type(result))
    if len(result.urls) < 9:
        result_amount = len(result.urls)
    else:
        result_amount = 9    # apparently Chatfuel or Facebook API doesn't quite work when you send 10 messages which is the default amount that google-custom-search returns. Will work on this later... There must be a way to send 10 queries hahaha
    if result_amount > 0:
        count = 0
        replit_db['users'][chatfuel_user_id]['last_google_search_results'] = []
        while count < result_amount: 
            replit_db['users'][chatfuel_user_id]['last_google_search_results'].append(
                {
                    "url": result.urls[count],
                    "title": result.titles[count],
                    "snippet": result.snippets[count],
                },
            )
            count += 1
        return True
    else:
        return False


def add_to_user_browsing_history(url, title, chatfuel_user_id):
    replit_db['users'][chatfuel_user_id]['user_browsing_history'].append(
        {
            'url': url,
            'title': title,
        }
    )


def encode_google_search_results(chatfuel_user_id):
    google_search_results = {
        "messages": [
            {"text": "These are what we've found!"}
        ]
    }

    count = 0
    for entry in replit_db['users'][chatfuel_user_id]['last_google_search_results']:
        count += 1
        text_block = ""
        text_block += f"[{count}] {entry['title']}\n"
        text_block += f"{entry['url']}\n\n"
        text_block += f"{entry.get('snippet', '')}"
        google_search_results['messages'].append({"text": f"{text_block}"},)

    return google_search_results


def get_article_text_from_google_search_result_num(search_result_num, chatfuel_user_id):
    # search result num     |       actual num on the list
    #       0                               1
    #       1                               2
    #       2                               3
    # and so on...
    search_result_num = int(search_result_num) - 1
    url = replit_db['users'][chatfuel_user_id]['last_google_search_results'][search_result_num]['url']
    article_text = get_article_text(url)
    return article_text


app = Flask(__name__)


@app.route('/')
def hello_world():
    return '<h1>Hello World!</h1>'


@app.route('/chatfuel/web_demo/')
def chatfuel_web_demo():
    return render_template('index.html')


@app.route('/chatfuel/fun_activities/', methods=['GET', 'POST'])
def chatfuel_fun_activities():
    request_type = request.args.get('request_type', None)

    if request_type == 'send_test_message':
        return {
                    "messages": [{
                        "text": "Sent you a test message!"
                    }]
                }

    elif request_type == 'test_post_on_backend':
        json_response = request.get_json(silent=True)
        pprint(json_response)
        print(f"json_response type: {json_response}")


    return '<h1>Chatfuel: Fun Activities</h1>'


@app.route('/chatfuel/search_tools/')
def chatfuel_search_tools():
    request_type = request.args.get('request_type', None)
    query = str(request.args.get('query', None))
    chatfuel_user_id = str(request.args.get('chatfuel_user_id', None))

    add_user(chatfuel_user_id)

    if request_type == 'search_on_google' and query:
        print("search_on_google has been triggered")
        query = str(query)
        result = search_on_google(query)
        add_to_last_google_search_results(result, chatfuel_user_id)
        json = encode_google_search_results(chatfuel_user_id)
        pprint(json)
        return json

    elif request_type == 'get_latest_google_search_results':
        print("get_latest_google_search_results has been triggered")
        json = encode_google_search_results(chatfuel_user_id)
        pprint(json)
        return json

    elif request_type == 'get_article_text_from_google_search_result_num':
        print("get_article_text_from_google_search_result_num has been triggered")
        gg_search_result_num = int(request.args.get('gg_search_result_num', None))
        json = {"messages": []}
        article_text = get_article_text_from_google_search_result_num(gg_search_result_num, chatfuel_user_id)
        if article_text:
            json = split_message(json, article_text, 1000)
            pprint(json)
            return json

        else:
            return {
                "messages": [{
                    "text": "Sorry, you entered an invalid number. Please try again:"
                }]
            }

    elif request_type == 'search_on_duckduckgo' and query:
        print("search_on_duckduckgo has been triggered")
        query = str(query)
        result = search_on_duckduckgo(query)
        add_to_last_duckduckgo_search_results(result, chatfuel_user_id)
        json = encode_duckduckgo_search_results(chatfuel_user_id)
        pprint(json)
        return json

    elif request_type == 'get_latest_duckduckgo_search_results':
        print("get_latest_duckduckgo_search_results has been triggered")
        json = encode_duckduckgo_search_results(chatfuel_user_id)
        pprint(json)
        return json

    elif request_type == 'get_article_text_from_duckduckgo_search_result_num':
        print("get_article_text_from_duckduckgo_search_result_num has been triggered")
        ddg_search_result_num = int(request.args.get('ddg_search_result_num', None))
        json = {"messages": []}
        article_text = get_article_text_from_duckduckgo_search_result_num(ddg_search_result_num, chatfuel_user_id)
        if article_text:
            json = split_message(json, article_text, 1000)
            pprint(json)
            return json

        else:
            return {
                "messages": [{
                    "text": "Sorry, you entered an invalid number. Please try again:"
                }]
            }


    return '<h1>Chatfuel: Search Tools</h1>'


@app.route('/chatfuel/my_all_around_husband/')
def chatfuel_my_all_around_husband():
    request_type = request.args.get('request_type', None)
    pprint(request.get_json(silent=True))

    if request_type == 'get_available_my_all_around_husband_pages_num':
        json = {"messages": []}
        pages_text = get_available_my_all_around_husband_pages_num()
        json = split_message(json, pages_text, 9)
        return json

    elif request_type == 'get_specific_my_all_around_husband_page':
        json = {"messages": []}
        page_num = request.args.get('page_num', None)
        page_text = get_specific_my_all_around_husband_page_text(page_num)
        if page_text != "":
            json["messages"].append({"text": f"Page {page_num}:"})
            json["messages"].append({"text": f"{page_text}"})
            return json
        else:
            return {
                "messages": [{
                    "text": "Sorry... I cannot find that page."
                }]
            }


@app.route('/chatfuel/charlie_wade/')
def chatfuel_charlie_wade():
    request_type = request.args.get('request_type', None)
    pprint(request.get_json(silent=True))

    if request_type == 'get_specific_charlie_wade_chapter':
        json = {"messages": []}

        chapter_num = request.args.get('chapter_num', None)
        chapter_text = get_specific_charlie_wade_chapter_text(chapter_num)
        if chapter_text:
            json = split_message_cw(json, chapter_text, 1000)
            return json

        else:
            return {
                "messages": [{
                    "text": "Sorry... I cannot find that chapter."
                }]
            }

    elif request_type == 'get_available_charlie_wade_chapters_num':
        json = {
            "messages": [
                {
                    "text": "Available Charlie Wade Chapters:"
                },
            ]
        }

        print('get_available_charlie_wade_chapters_num triggered')
        chapters = get_available_charlie_wade_chapters_num()
        json = split_message_cw(json, chapters, 1996)
        print(json)
        return json

    elif request_type == 'get_latest_charlie_wade_chapter':
        json = {"messages": []}
        print('get_latest_charlie_wade_chapter triggered')
        chapter_text = get_latest_charlie_wade_chapter_text()
        json = split_message_cw(json, chapter_text, 1000)
        return json

    return '<h1>Chatfuel: Charlie Wade</h1>'


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    verify_environ_variables()
    initialize_database()
    check_database(replit_db)
    app.run(host='0.0.0.0', port=port)