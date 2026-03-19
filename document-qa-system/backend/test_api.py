import httpx
import asyncio

async def test_health():
    async with httpx.AsyncClient() as client:
        resp = await client.get('http://localhost:8000/health')
        print('Health check:', resp.status_code, resp.json())

async def upload_document():
    async with httpx.AsyncClient() as client:
        with open('test_document.txt', 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            params = {
                'filename': 'test_document.txt',
                'mime_type': 'text/plain'
            }
            resp = await client.post('http://localhost:8000/api/v1/documents/upload', files=files, params=params)
            print(f"Upload Status: {resp.status_code}")
            print(f"Upload Response: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_health())
    print("---")
    asyncio.run(upload_document())