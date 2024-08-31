from socket import MsgFlag
import mysql.connector
import os
from flask import Flask, request, render_template, send_file, make_response, jsonify
import time
import csv
from flask_jwt_extended import JWTManager, create_access_token
import requests
import datetime
from requests.auth import HTTPBasicAuth
import subprocess

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'adahudhaohdoahf'  # 更改为你的密钥
jwt = JWTManager(app)

access_token_user = []

if("PORT" in os.environ):
    port = os.environ['PORT']
else:
    port = 8090
if("PUBLIC_IP_PORT" in os.environ):
    pub_ip_port = os.environ['PUBLIC_IP_PORT']
else:
    pub_ip_port = "http://api.emagen.cn"

CLIENT_ID = os.environ.get('JACCOUNT_CLIENT_ID')
CLIENT_SECRET = os.environ.get('JACCOUNT_CLIENT_SECRET')

# 登陆成功后的页面，可以输入密码
@app.route('/auth/login', methods=['GET'])
def registerWithCode():
    print("login:")
    try:
        code = request.args.get('code')
        print(code)
        print("ready to get access_token")
        access_token = request_access_token(code)
        print(access_token)
        response = send_get_request(f"https://api.sjtu.edu.cn/v1/me/profile?access_token={access_token}")
        print("response:")
        print(response)
        user_id = parse_user_id(response)
        user_name = parse_user_name(response)
        
        if not user_exists(user_id):
            create_user(user_id, user_name)

        # 生成 JWT
        jwt_data = {
            'user_id': user_id,
            'name': user_name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        # 打印 jwt_data
        print(jwt_data)
        
        token = create_access_token(identity=jwt_data)
        # 打印 token
        print(token)

        return jsonify(token=token)
    except Exception as e:
        print(e)  
        return render_template('initial.html', msg=CLIENT_ID)  # 发生异常时返回 initial.html

def create_auth_table_if_not_exists():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth (
            user_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    
# 初始界面，只有一个登陆按钮
@app.route('/auth', methods=['GET'])
def register():  
    print("auth:")
    return render_template('initial.html', msg=CLIENT_ID)

# 数据库连接配置
db_config = {
    'user': 'auth',
    'password': 'cyberlife',
    'host': 'localhost',
    'database': 'auth'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def user_exists(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM auth WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] > 0

def create_user(user_id, name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO auth (user_id, name) VALUES (%s, %s)", (user_id, name))
    conn.commit()
    cursor.close()
    conn.close()
    
# 获取 access_token， 用于获取学号 （实际部署可以把密钥写到环境变量中）
def request_access_token(code):
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    print("redirect_uri:")
    print(pub_ip_port + "/auth/login")
    try:
        response = requests.post(
            "http://jaccount.sjtu.edu.cn/oauth2/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "Host": "jaccount.sjtu.edu.cn",
                "Connection": "keep-alive"
            },
            auth=HTTPBasicAuth(client_id, client_secret),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": pub_ip_port + "/auth/login"
            }
        )
        response.raise_for_status()  # Raises stored HTTPError, if one occurred.
    except requests.exceptions.RequestException as e:
        raise Exception("Request access token failed") from e

    try:
        response_body = response.json()
        access_token = response_body["access_token"]
        return access_token
    except (ValueError, KeyError) as e:
        raise Exception("Request access token failed") from e


# 发送 GET 请求，获取学号
def send_get_request(url_str):
    try:
        response = requests.get(
            url_str,
            headers={
                "Accept": "*/*",
                "Host": "api.sjtu.edu.cn",
                "Connection": "keep-alive"
            }
        )
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json() # Assuming the response is JSON
    except requests.exceptions.RequestException as e:
        raise Exception("Sending GET request failed") from e

# 解析学号
def parse_user_id(response):
    try:
        code = response["entities"][0]["code"]
        return code
    except (ValueError, KeyError) as e:
        raise Exception("Parsing user id failed") from e
    
def parse_user_name(response):
    try:
        name = response["entities"][0]["name"]
        return name
    except (ValueError, KeyError) as e:
        raise Exception("Parsing user name failed") from e


if __name__ == '__main__':
    create_auth_table_if_not_exists()
    app.run(port=port, host="0.0.0.0", debug=True)
