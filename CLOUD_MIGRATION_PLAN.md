# ☁️ JARVIS Cloud Migration Plan - Projeto Latência Zero

Este documento detalha os passos técnicos para mover o JARVIS de uma máquina local para um servidor de alta performance (VPS), visando reduzir a latência de execução de ~350ms para menos de 100ms.

---

## 🏗️ 1. Infraestrutura Recomendada

Para trading de alta frequência (HFT) no Polymarket/Polygon, a localização geográfica do servidor é crucial.

| Provedor | Região Recomendada | Justificativa |
| :--- | :--- | :--- |
| **AWS** | `us-east-1` (N. Virginia) | Proximidade com a maioria dos RPCs da Polygon e infraestrutura da Polymarket. |
| **DigitalOcean** | `NYC3` (New York) | Excelente custo-benefício e latência estável para hubs financeiros. |
| **Hetzner** | `Falkenstein` (Germany) | Alta performance de CPU para processamento de sentimento. |

---

## 📦 2. Dockerização (Portabilidade)

Criamos uma estrutura Docker para que o sistema rode de forma idêntica na nuvem e no seu Windows.

### Arquivos Criados:
*   **`Dockerfile`**: Imagem otimizada para Python 3.12 com suporte a processamento assíncrono.
*   **`docker-compose.yml`**: Orquestra o `Master Bot` e o `Dashboard` de forma independente.

---

## 🚀 3. Passos da Migração

1.  **Provisionamento**: Criar um Droplet ou Instância EC2 (Mínimo: 2 vCPUs, 4GB RAM, Ubuntu 24.04).
2.  **Segurança SSH**: Configurar chaves SSH para acesso seguro (sem senhas).
3.  **Deploy em 1-Clique**:
    ```bash
    git clone https://github.com/TiagoAmaro87/PROJETO_JARVIS_POLYMARKET.git
    cd PROJETO_JARVIS_POLYMARKET
    # Criar o arquivo .env manualmente no servidor
    docker-compose up -d --build
    ```

---

## 📉 4. Tabela de Comparação de Latência

| Métrica | Local (Windows/WSL) | Cloud (Dedicated VPS) | Impacto no Sniper |
| :--- | :--- | :--- | :--- |
| **Compute Time** | ~350ms | **<50ms** | 🚀 Alta Prioridade |
| **Network RTT** | ~80ms | **<10ms** | 🎯 Preenchimento Garantido |
| **Uptime** | Depende de energia/net | **99.99%** | 🛡️ Proteção 24/7 |

---

> [!TIP]
> **RECOMENDAÇÃO**: Começar com a **DigitalOcean (New York)**. A configuração é mais simples e a latência para os servidores da Polymarket costuma ser excelente.
