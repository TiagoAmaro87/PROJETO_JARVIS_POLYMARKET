import asyncio
import aiohttp

async def check_real_clob_balance():
    api_key = "019ce41c-0e22-74ed-a9e5-8dbb92e0a7f6"
    api_secret = "yuQm2U78o6k6-9qc6Q1j58ojTZAkMJym9SAlpJpH1rc="
    api_passphrase = "349e31c9cc55af8f8673405d5a3069e586e2cab8200864dfc85052ebbadb8c69"
    address = "0x1b5511cd1a08b3bd94d50df44de5455a7276df9c"

    headers = {
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SECRET": api_secret,
        "OK-ACCESS-PASSPHRASE": api_passphrase,
    }

    url = f"https://clob.polymarket.com/balance?address={address}&asset_id=1"

    print("--- TESTE DE SALDO AUTENTICADO ---")
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            print(f"Status: {resp.status}")
            data = await resp.json()
            print(f"Data: {data}")
            
    print("\n--- TESTE DE POSITIONS ---")
    url_pos = f"https://clob.polymarket.com/positions?user={address}"
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url_pos) as resp:
            print(f"Status Pos: {resp.status}")
            print(f"Data Pos: {await resp.text()}")

if __name__ == "__main__":
    asyncio.run(check_real_clob_balance())
