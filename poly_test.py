import asyncio
import aiohttp
import json

async def main():
    async with aiohttp.ClientSession() as s:
        try:
            url = 'https://gamma-api.polymarket.com/events?active=true&closed=false&limit=1'
            async with s.get(url) as r:
                data = await r.json()
                print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
