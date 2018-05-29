from flask import Flask, request, Response, send_file, abort, redirect, url_for, jsonify, render_template
from flask_cors import CORS
import itchat, time
from itchat.content import *
from datetime import datetime
from threading import Thread
import requests


############################################################
DOMAIN = 'http://localhost'
PORT = 8082
HOST_URL = '{0}:{1}'.format(DOMAIN, PORT)

RORWARD_URL = 'https://www.magicbowen.top:443/intramirror/msg'

############################################################
MSG_ID = 101101

@itchat.msg_register(TEXT, isGroupChat=False)
def text_reply(msg):
    senderId = msg['FromUserName']
    sender = itchat.search_friends(userName=senderId)
    profilePath = './profiles/{0}.png'.format(sender['NickName'])
    from_profile = itchat.get_head_img(userName = senderId, picDir = profilePath)

    myself = itchat.search_friends()

    print(msg)
    print(myself)

    forward_msg = {
        "id"   : MSG_ID,
        "timestamp" : datetime.utcnow(),
        "from" : {
            "userId"   : senderId,
            "username" : sender['NickName'],
            "profile"  : '{0}/profile?name={1}.png'.format(HOST_URL, sender['NickName'])
        },
        "to"  : {
            "userId"   : myself['NickName']
        },
        "text"  : msg['Content']
        # "photo" : "http://localhost/photo/abc.jpg",
        # "audio" : "http://localhost/audio/abc.mp3",
        # "vedio" : "http://localhost/vedio/abc.mp4"
    }

    r = requests.post(RORWARD_URL, json=forward_msg)
    if r.status_code == 200:
        print('received msg [{0} : {1}] from [{2}] to [{3}]'.format(msg['MsgType'], msg['Content'], sender['NickName'], myself['NickName']))
    else:
        print('send msg to telegram failed!')


############################################################
app = Flask(__name__)
CORS(app) 
thread = Thread()

def wechat_login(itchat):
    itchat.auto_login(hotReload=True)
    itchat.run(True)

@app.route('/profile', methods=['GET'])
def query_image():
    profile = request.args.get('name')
    return send_file("./profiles/{}".format(profile), mimetype='image/jpeg')

@app.route('/msg', methods=['POST'])
def send_msg():
    msg = request.json
    print('wechat assistant received msg:')
    print(msg)
    author = itchat.search_friends(nickName=msg.to.userId)[0]
    author.send(msg.text)

@app.route('/')
def index():
    return "Welcome to wechat assistant!"

if __name__ == '__main__':
    thread = Thread(target = wechat_login, args = (itchat, ))
    thread.start()
    app.run(host='0.0.0.0', port=PORT, debug=True)
    

