import requests

# 测试 API
response = requests.post(
    'http://localhost:8000/api/v1/chat',
    json={'query': '什么是人工智能', 'top_k': 2}
)

print(f"Status Code: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Response Text: {response.text[:500]}")
print(f"Response Content: {response.content[:500]}")

try:
    json_data = response.json()
    print(f"JSON Response: {json_data}")
except Exception as e:
    print(f"Not JSON: {e}")
