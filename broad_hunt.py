import asyncio
import aiohttp

async def broad_hunt():
    addresses = [
        "0x639f7e0b317f586b350cdcc1ceb22a2ed44e2211", # MetaMask
        "0x0151e92d329fe92f081ce3271e21c1febc6f4ce3", # Deposit/Former
        "0x1b5511cd1a08b3bd94d50df44de5455a7276df9c", # Relayer/Proxy
        "0x05aaa06f5d08c307c307e9bf2b28990a5205c2b8", # Builder
        "0xd05419B324A95a02F6cCf11b182752Fe02E542fD"  # Google/Privy
    ]
    
    print("\n--- BROAD HUNT FOR $1.62 ---")
    async with aiohttp.ClientSession() as session:
        for addr in addresses:
            url = f"https://gamma-api.polymarket.com/users/?address={addr}"
            try:
                async with session.get(url, timeout=5) as resp:
                    print(f"\nAddress: {addr}")
                    print(f"Status: {resp.status}")
                    data = await resp.json()
                    print(f"Data: {data}")
            except Exception as e:
                print(f"Error on {addr}: {e}")
    print("\n--- END BROAD HUNT ---")

if __name__ == "__main__":
    asyncio.run(broad_hunt())
