from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
socketio = SocketIO(app)

# 企业微信的API凭据
corpid = 'ww27d37e1d8c21db73'
secret = 'qfFu_MbwjVWlI9QupuXwibq6QK68c2LPL_EqPhZoInE'
access_token = ''
message_callback_url = '/external_contact_message_callback'  # 替换为你的消息回调URL


# 处理消息回调的路由
@app.route(message_callback_url, methods=['POST'])
def handle_message_callback():
    try:
        data = request.json  # 解析接收到的 JSON 数据
        # 处理消息数据，可以根据需求编写逻辑
        print("Received message callback data:", data)
        # 在这里，你可以根据消息内容执行适当的操作

        # 将消息通过 WebSocket 发送给前端
        socketio.emit('message_received', {'message': data})

        return jsonify({"errcode": 0, "errmsg": "success"})  # 返回成功响应
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"errcode": 1, "errmsg": "error"}), 500  # 返回错误响应


# 获取访问令牌
def get_access_token():
    global access_token
    url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={secret}'
    response = requests.get(url)
    print("get_access_token --> ", response.json())
    access_token = response.json().get('access_token', '')


def get_user_id(access_token, user_id="PuXu"):
    url = f'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={access_token}&userid={user_id}'
    response = requests.get(url)
    print("get_user_id ---> ", response.json())
    return response.json().get('userid')


# 获取外部联系人列表
def get_external_contacts():
    if not access_token:
        get_access_token()

    user_id = get_user_id(access_token)

    url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/list?access_token={access_token}&userid={user_id}&external_contact.field=external_userid'
    response = requests.get(url)
    print("get_external_contacts --> ", response.json())
    external_user_ids = response.json().get('external_userid', [])

    # 获取每个 external_userid 的用户信息
    external_contacts_info = {}
    for external_user_id in external_user_ids:
        user_info = get_external_contact_info(access_token, external_user_id)
        external_contacts_info[external_user_id] = user_info

    return external_contacts_info


def get_external_contact_info(access_token, userid):
    url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/get?access_token={access_token}&external_userid={userid}'
    response = requests.get(url)
    print("get_external_contact_info --> ", response.json())
    data = response.json()
    if data.get('errcode') == 0:
        # 成功获取外部联系人信息
        external_contact_info = data.get('external_contact')
        name = external_contact_info.get('name')
        mobile = external_contact_info.get('mobile')
        email = external_contact_info.get('email')
        return {
            'name': name,
            'mobile': mobile,
            'email': email
        }
    else:
        # 处理错误
        return None


# 页面路由和应用逻辑
@app.route('/')
def select_contact():
    external_contacts = get_external_contacts()
    return render_template('select_contact.html', external_contacts=external_contacts)


@socketio.on('connect')
def handle_connect():
    socketio.emit('connection_message', {'message': 'Connected to the server'})


@socketio.on('send_message')
def handle_send_message(data):
    # 构建API请求
    # url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
    url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/message/send?access_token={access_token}&debug=1'

    # 从表单获取要发送的消息数据
    touser = data.get('touser')
    content = data.get('content')

    # 构建消息内容
    message_data = {
        "touser": touser,
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    response = requests.post(url, json=message_data)
    data = response.json()
    print("data ===> ", data)

    response_data = {'message': f'Sent to {touser}: {content}'}
    socketio.emit('message_received', response_data)
    # return redirect(url_for('select_contact'))


if __name__ == '__main__':
    socketio.run(app, debug=False, allow_unsafe_werkzeug=True)
