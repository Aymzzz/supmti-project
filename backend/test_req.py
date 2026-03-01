import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        with open("test.webm", "wb") as f:
            f.write(b"dummy audio data")
        
        files = {'audio': ('test.webm', open('test.webm', 'rb'), 'audio/webm')}
        data = {'language': 'fr'}
        resp = await client.post('http://127.0.0.1:8000/api/voice/transcribe', files=files, data=data)
        print("Status", resp.status_code)
        print("Text", resp.text)

asyncio.run(test())
