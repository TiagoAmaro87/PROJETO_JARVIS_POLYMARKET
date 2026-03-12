# 🤖 JARVIS - MISSION CONTROL & RESTORE POINT

## 🔋 SISTEMA JARVIS V2 (MULTI-TARGET)

A V2 permite monitorar dezenas de mercados simultaneamente usando o arquivo `targets.json`.

### 🚀 Como Operar
1.  **Edição Live:** Você pode editar `targets.json` enquanto o robô roda. Ele recarrega as configurações a cada 30 segundos.
2.  **Novos Alvos:** Basta copiar o bloco de um alvo no JSON e alterar o `id`, `name` e `token_ids`.
3.  **Execução:**
    ```powershell
    python jarvis_v2.py
    ```

### 🎯 Estratégia Atual: Arbitragem Pura
O robô busca mercados onde `Preço(YES) + Preço(NO) < 0.999`. Ao comprar ambos, garantimos um lucro fixo quando o mercado resolve.

---

## 🛠️ MANUTENÇÃO E LOGS
-   **Logs V1:** `jarvis_stable.log`
-   **Logs V2:** `jarvis_v2.log`
-   **Estado Financeiro:** `jarvis_v2_state.json`

## 📊 Status Atual da Operação (Windows Stable v2.1)
- **Patrimônio Gerenciado**: ~$1.548,17
- **Lucro por Minuto**: ~$0,21/min ($12,60/hora)
- **Arquitetura**: 4 Caixas (Arbitragem, Market Maker, Sentimento, Sniper).
- **Caixa de Elite**: Sniper (Caixa 04) já ativa com capital de lucro.

## 🛠️ Próximo Passo: ROADMAP LINUX (PRODUÇÃO)
Assim que o computador reiniciar (após o comando DISM ser executado como Admin), seguiremos esta sequência:

1. **WSL Export/Import**: Mover o Ubuntu de `C:` para `E:\JARVIS_SYSTEM\LINUX_VM\`.
2. **GPU NVIDIA Injection**: Instalar Drivers CUDA dentro do Ubuntu para acessar a GTX 1660.
3. **External Swap**: Configurar 16GB de Swap no Disco E: para proteção de memória.
4. **Alpha/Omega Setup**: Criar ambientes virtuais Python isolados no HD externo.

## 🦾 PROMPT ATIVO (Para colar quando voltar):
> "Antigravity, PC reiniciado. O WSL e a Virtual Machine Platform já foram habilitados via DISM. Prossiga com a migração do Ubuntu para o Disco E: e a configuração do ambiente NVIDIA/CUDA conforme nosso plano."

---
*Assinado: Antigravity - AI Co-Pilot*
