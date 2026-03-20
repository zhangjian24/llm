import httpx
import asyncio
import json

async def simple_test():
    async with httpx.AsyncClient() as client:
        payload = {
            "query": "人工智能的发展历程是什么？",
            "stream": False
        }
        
        resp = await client.post(
            'http://localhost:8000/api/v1/chat/',
            json=payload,
            timeout=30.0
        )
        
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print("Response received successfully!")
            print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(simple_test())