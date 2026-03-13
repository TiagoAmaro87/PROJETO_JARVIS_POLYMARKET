import asyncio
import aiohttp

async def rpc_ground_truth():
    addresses = {
        "MetaMask": "0x639f7e0b317f586b350cdcc1ceb22a2ed44e2211",
        "Deposit": "0x0151e92d329fe92f081ce3271e21c1febc6f4ce3",
        "Relayer": "0x1b5511cd1a08b3bd94d50df44de5455a7276df9c",
        "Builder": "0x05aaa06f5d08c307c307e9bf2b28990a5205c2b8"
    }
    
    tokens = {
        "USDC.e (Bridged)": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "USDC (Native)": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
    }
    
    rpc_url = "https://polygon-rpc.com"
    
    print("\n--- BLOCKCHAIN GROUND TRUTH CHECK ---")
    async with aiohttp.ClientSession() as session:
        for name, addr in addresses.items():
            print(f"\nAccount: {name} ({addr})")
            for t_name, t_addr in tokens.items():
                # balanceOf(address) data
                data = f"0x70a08231000000000000000000000000{addr[2:]}"
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_call",
                    "params": [{"to": t_addr, "data": data}, "latest"],
                    "id": 1
                }
                try:
                    async with session.post(rpc_url, json=payload, timeout=5) as resp:
                        res = await resp.json()
                        hex_val = res.get("result", "0x0")
                        val = int(hex_val, 16) / 1_000_000
                        print(f"  {t_name}: ${val:.4f}")
                except Exception as e:
                    print(f"  {t_name} Error: {e}")
    print("\n--- FIM DO CHECK ---")

if __name__ == "__main__":
    asyncio.run(rpc_ground_truth())
