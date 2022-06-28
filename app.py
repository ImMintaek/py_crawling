from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

# DBはnoSQLサービスであるMongoDBを使用
from pymongo import MongoClient
import os
import certifi

ca = certifi.where()
client = MongoClient(os.environ.get('mongo_db_path'), tlsCAFile=ca)
db = client.dbsparta


@app.route('/')
def home():
    return render_template('index.html')

# POSTメソッドで、サイト表示に必要な、url、評価、コメントをindex.htmlよりajaxコールする関数を作成
@app.route("/movie", methods=["POST"])
def movie_post():
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    # Crawling練習、「映画.com」のサイト内の映画のタイトル、画像、説明をcrawlingしました。
    # 課題点：映画.comサイトのmetaタグ内にあるcontentに合わせてtitle、descriptionをsplitしたため、他のサイトではいらない情報も入ってくる。
    title = soup.select_one('meta[property="og:title"]')['content'].split(':')[0]
    image = soup.select_one('meta[property="og:image"]')['content']
    desc = soup.select_one('meta[property="og:description"]')['content'].split('。')[2]

    # 記録するボタンを押すと最終的にmongoDBにタイトル、画像URL、映画の説明、評価、コメントが保存できるように作成
    doc = {
        'title': title,
        'image': image,
        'desc': desc,
        'star': star_receive,
        'comment': comment_receive
    }
    db.movies.insert_one(doc)
    # エラーなく、成功した場合は「保存完了」とメッセージ表示
    return jsonify({'msg': '保存完了!'})

# GETメソッドで、mongoDBに保存された全てのデータを表示させるため持ってくる関数を作成
@app.route("/movie", methods=["GET"])
def movie_get():
    movie_list = list(db.movies.find({}, {'_id': False}))
    return jsonify({'movies': movie_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
