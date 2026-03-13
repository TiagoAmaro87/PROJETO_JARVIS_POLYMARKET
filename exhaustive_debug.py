import asyncio
import aiohttp

async def debug_balance():
    # Endereços fornecidos
    addrs = {
        "Builder": "0x05aaa06f5d08c307c307e9bf2b28990a5205c2b8",
        "MetaMask": "0x639f7e0b317f586b350cdcc1ceb22a2ed44e2211",
        "Relayer": "0x1b5511cd1a08b3bd94d50df44de5455a7276df9c",
        "Deposit": "0x0151e92d329fe92f081ce3271e21c1febc6f4ce3"
    }
    
    # Credenciais
    api_key = "019ce41c-0e22-74ed-a9e5-8dbb92e0a7f6"
    api_secret = "yuQm2U78o6k6-9qc6Q1j58ojTZAkMJym9SAlpJpH1rc="
    api_passphrase = "349e31c9cc55af8f8673405d5a3069e586e2cab8200864dfc85052ebbadb8c69"
    
    headers = {
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SECRET": api_secret,
        "OK-ACCESS-PASSPHRASE": api_passphrase,
    }

    print("\n--- DEBUG EXAUSTIVO DE SALDO ---")
    async with aiohttp.ClientSession(headers=headers) as session:
        for name, addr in addrs.items():
            print(f"\n>>> TESTANDO {name}: {addr}")
            
            # 1. CLOB Balance (Auth)
            for asset in ["1", "2"]:
                url = f"https://clob.polymarket.com/balance?address={addr}&asset_id={asset}"
                async with session.get(url) as r:
                    print(f"  CLOB Asset {asset} (Auth): {r.status} {await r.text()}")
            
            # 2. Data API Value
            url = f"https://data-api.polymarket.com/value?user={addr}"
            async with session.get(url) as r:
                print(f"  Data API (No Auth): {r.status} {await r.text()}")
                
            # 3. Gamma User (Path-based)
            url = f"https://gamma-api.polymarket.com/users/{addr}"
            async with session.get(url) as r:
                print(f"  Gamma User (Path): {r.status} {await r.text()}")

if __name__ == "__main__":
    asyncio.run(debug_balance())
