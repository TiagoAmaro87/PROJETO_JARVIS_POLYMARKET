import asyncio
import aiohttp

async def locate_cash():
    # Endereço Builder/Oficial do Usuário
    address = "0x05aaa06f5d08c307c307e9bf2b28990a5205c2b8"
    
    print(f"\n--- BUSCANDO $1,62 NO ENDEREÇO {address} ---")
    
    endpoints = [
        # Data API (O que o site usa para o Portfolio Value)
        f"https://data-api.polymarket.com/value?user={address}",
        # Gamma Account
        f"https://gamma-api.polymarket.com/accounts/{address}",
        # CLOB Asset 1 (USDC.e)
        f"https://clob.polymarket.com/balance?address={address}&asset_id=1",
        # CLOB Asset 2 (USDC Nativo)
        f"https://clob.polymarket.com/balance?address={address}&asset_id=2"
    ]
    
    async with aiohttp.ClientSession() as session:
        for url in endpoints:
            try:
                async with session.get(url, timeout=5) as resp:
                    print(f"\nURL: {url}")
                    print(f"Status: {resp.status}")
                    data = await resp.json()
                    print(f"Resposta: {data}")
            except Exception as e:
                print(f"Erro ao acessar {url}: {e}")
    print("\n--- FIM DA BUSCA ---")

if __name__ == "__main__":
    asyncio.run(locate_cash())
