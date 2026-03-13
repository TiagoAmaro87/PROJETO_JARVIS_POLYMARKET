import asyncio
import aiohttp

async def check_all_balances():
    address = "0x0151e92d329fe92f081ce3271e21c1febc6f4ce3"
    
    # IDs dos ativos na rede Polygon (usados pela API do Polymarket/Gamma)
    # Asset 2 = USDC (Nativo)
    # Asset 1 = USDC.e (Bridged/Antigo - O que o Polymarket usa para apostas)
    
    tokens = {
        "USDC (Nativo - O que você enviou)": "2",
        "USDC.e (O que o Polymarket usa para apostar)": "1"
    }
    
    print(f"\n--- VERIFICAÇÃO DE SALDO REAL NA CARTEIRA {address[:10]}... ---")
    
    headers = {"User-Agent": "Mozilla/5.0"}
    async with aiohttp.ClientSession(headers=headers) as session:
        for name, asset_id in tokens.items():
            url = f"https://gamma-api.polymarket.com/balance?address={address}&asset_id={asset_id}"
            try:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        balance = float(data.get("balance", 0)) / 1_000_000
                        print(f"-> {name}: ${balance:.6f}")
            except Exception as e:
                print(f"Erro ao checar {name}: {e}")
    print("----------------------------------------------------------\n")

if __name__ == "__main__":
    asyncio.run(check_all_balances())
