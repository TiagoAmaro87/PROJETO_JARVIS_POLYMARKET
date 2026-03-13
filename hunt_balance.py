import asyncio
import aiohttp

async def hunt_the_balance():
    # Endereços que podem ter o dinheiro
    addresses = [
        "0x639f7e0b317f586b350cdcc1ceb22a2ed44e2211", # Sua MetaMask
        "0x0151e92d329fe92f081ce3271e21c1febc6f4ce3", # Sua antiga carteira de depósito
        "0x1b5511cd1a08b3bd94d50df44de5455a7276df9c", # Sua nova Proxy vinculada à MetaMask
        "0xd05419B324A95a02F6cCf11b182752Fe02E542fD"  # Sua carteira do Google (Privy)
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "RELAYER_API_KEY": "019ce415-3849-7ac4-88ec-27c84dcbf097",
        "RELAYER_API_KEY_ADDRESS": "0x1b5511cd1a08b3bd94d50df44de5455a7276df9c"
    }
    print("\n--- CAÇADA AO SALDO COM API AUTH ---")
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for addr in addresses:
            for endpoint in ["balance", "balance-allowance"]:
                for asset in ["1", "2"]:
                    url = f"https://clob.polymarket.com/{endpoint}?address={addr}&asset_id={asset}"
                    try:
                        async with session.get(url, timeout=5) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                bal_key = "balance" if "balance" in data else "bal"
                                bal = float(data.get(bal_key, 0)) / 1_000_000
                                print(f"ADR: {addr[:10]} | END: {endpoint} | AST: {asset} | SALDO: ${bal:.4f}")
                            else:
                                print(f"ADR: {addr[:10]} | END: {endpoint} | Error: {resp.status}")
                    except Exception as e:
                        print(f"Erro em {addr} no endpoint {endpoint}: {e}")
    print("---------------------------------\n")

if __name__ == "__main__":
    asyncio.run(hunt_the_balance())
