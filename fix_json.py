import json
import os

def fix_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                content = f.read().strip()
            
            # Remove o ] extra se houver
            if content.endswith(']]'):
                content = content[:-1]
                with open(filename, 'w') as f:
                    f.write(content)
                print(f"Corrigido: {filename}")
            
            # Tenta carregar para validar
            with open(filename, 'r') as f:
                json.load(f)
            print(f"Arquivo {filename} está íntegro.")
        except Exception as e:
            print(f"Erro ao corrigir {filename}: {e}")
            # Se estiver muito quebrado, reinicia
            with open(filename, 'w') as f:
                json.dump([], f)
            print(f"Arquivo {filename} resetado para evitar travamento.")

fix_json("wealth_history.json")
fix_json("live_status.json")
fix_json("jarvis_state.json")
fix_json("trades_history.json")
