import httpx
import asyncio

async def upload_document():
    async with httpx.AsyncClient() as client:
        with open('test_document.txt', 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            resp = await client.post('http://localhost:8000/api/v1/documents/upload', files=files)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.json()}")

if __name__ == "__main__":
    asyncio.run(upload_document())