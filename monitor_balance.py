import asyncio
import aiohttp
import time

async def check_balance():
    address = "0x0151e92d329fe92f081ce3271e21c1febc6f4ce3"
    asset_id = "2" # USDC
    url = f"https://gamma-api.polymarket.com/balance?address={address}&asset_id={asset_id}"
    
    print(f"Monitorando saldo para {address}...")
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        balance = float(data.get("balance", 0)) / 1_000_000
                        if balance > 0:
                            print(f"\n[!!!] SALDO DETECTADO: ${balance:.2f} USDC")
                        else:
                            # Print a dot every 10 seconds to show it's alive
                            print(".", end="", flush=True)
                    else:
                        print(f"Erro API: {resp.status}")
            except Exception as e:
                print(f"Erro: {e}")
            
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(check_balance())
