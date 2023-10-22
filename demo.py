from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# 企业微信的API凭据
corpid = 'ww27d37e1d8c21db73'
secret = 'qfFu_MbwjVWlI9QupuXwibq6QK68c2LPL_EqPhZoInE'
agent_id = 'ww5b8a600d9499a130'
access_token = ''
permanent_code = ''
agent_secret = ''
AUTH_CODE = ''


# 获取访问令牌
def get_access_token():
    global access_token
    url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={secret}'
    response = requests.get(url)
    print("response.json() ---> ", response.json())
    access_token = response.json().get('access_token', '')


# 获取永久授权码（Permanent Code）
def get_permanent_code(auth_code):
    global permanent_code  # 使用 global 声明全局变量
    url = f'https://qyapi.weixin.qq.com/cgi-bin/service/get_permanent_code?suite_access_token={access_token}'
    data = {
        'auth_code': auth_code
    }
    response = requests.post(url, json=data)
    permanent_code = response.json().get('permanent_code', '')  # 设置 permanent_code


# 获取企业应用的 Secret
def get_agent_secret(permanent_code, corp_id, agent_id):
    global agent_secret  # 使用 global 声明全局变量
    url = f'https://qyapi.weixin.qq.com/cgi-bin/agent/get?access_token={get_corp_token(corp_id, permanent_code)}'
    params = {
        'agentid': agent_id
    }
    response = requests.get(url, params=params)
    agent_secret = response.json().get('agent_secret', '')  # 设置 agent_secret


# 获取企业访问令牌
def get_corp_token(corp_id, permanent_code):
    url = f'https://qyapi.weixin.qq.com/cgi-bin/service/get_corp_token?suite_access_token={access_token}'
    data = {
        'auth_corpid': corp_id,
        'permanent_code': permanent_code
    }
    response = requests.post(url, json=data)
    return response.json().get('access_token', '')


# 获取外部联系人列表
# 获取外部联系人列表
def get_external_contacts():
    global permanent_code  # 声明 permanent_code 和 agent_secret 为全局变量
    global agent_secret

    if not access_token:
        get_access_token()

    if not permanent_code:
        # 获取永久授权码（Permanent Code）
        permanent_code = get_permanent_code(AUTH_CODE)

    if not agent_secret:
        # 获取企业应用的 Secret
        agent_secret = get_agent_secret(permanent_code, corpid, agent_id)

    # 使用企业应用的 Secret获取企业访问令牌
    corp_access_token = get_corp_token(corpid, permanent_code)

    # 使用企业访问令牌调用获取外部联系人的接口
    url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/list?access_token={corp_access_token}'
    response = requests.get(url)
    return response.json().get('external_userid', [])


# 页面路由和应用逻辑
@app.route('/')
def select_contact():
    external_contacts = get_external_contacts()
    return render_template('select_contact.html', external_contacts=external_contacts)


@app.route('/send_message', methods=['POST'])
def send_message_route():
    # 在此处理发送消息的逻辑
    return redirect(url_for('select_contact'))


if __name__ == '__main__':
    app.run(debug=True)
