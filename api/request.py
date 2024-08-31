import requests

# 生成一个有效的 JWT 令牌（在实际使用中，你应该从你的认证系统获取这个令牌）
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyNDk5NTg2MiwianRpIjoiZjk3NTgyM2MtZDRmMy00MjcyLWEwMjktODQzYWQ4MTJjNmY0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJ1c2VyX2lkIjoiNTIyMDMxOTEwMjk5IiwibmFtZSI6Ilx1OTY0OFx1NTQyZlx1NzA5YyIsImV4cCI6IlNhdCwgMzEgQXVnIDIwMjQgMDU6MzE6MDIgR01UIn0sIm5iZiI6MTcyNDk5NTg2MiwiY3NyZiI6ImIyNTVmYmNhLTAzN2ItNDMzMy05MDBmLWExNzEwNDc1ZmE4ZCIsImV4cCI6MTcyNDk5Njc2Mn0.gp8IXtn_yvDwrz7HfjCwTPcUTVLXuksacAb3n5WlkZM"

# 设置请求头
headers = {
    "Authorization": f"Bearer {jwt_token}"
}

# 发送请求
response = requests.get("http://localhost:9000/protected", headers=headers)

# 打印响应
print(response.status_code)
print(response.json())