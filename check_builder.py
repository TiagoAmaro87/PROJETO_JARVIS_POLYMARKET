import asyncio
import aiohttp

async def check_builder_balance():
    addr = "0x05aaa06f5d08c307c307e9bf2b28990a5205c2b8"
    print(f"\n--- CHECKING BUILDER ADDRESS: {addr} ---")
    
    async with aiohttp.ClientSession() as session:
        for asset in ["1", "2"]:
            # Testing CLOB
            url_clob = f"https://clob.polymarket.com/balance?address={addr}&asset_id={asset}"
            try:
                async with session.get(url_clob, timeout=5) as resp:
                    print(f"\nCLOB Asset {asset}: {resp.status}")
                    print(await resp.text())
            except Exception as e:
                print(f"CLOB Error: {e}")
                
        # Testing Gamma account info
        url_gamma = f"https://gamma-api.polymarket.com/users/?address={addr}"
        try:
            async with session.get(url_gamma, timeout=5) as resp:
                print(f"\nGamma User Profile: {resp.status}")
                print(await resp.text())
        except Exception as e:
            print(f"Gamma Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_builder_balance())
