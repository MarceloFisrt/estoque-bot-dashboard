# 🌐 Como Acessar o Dashboard Estratégico

## 📋 Instruções para Acesso

### 🔗 **Link do Dashboard:**
```
http://192.168.43.222:8000/dashboard/
```

### 📍 **Requisitos:**
- O computador visitante deve estar na **mesma rede WiFi/LAN**
- O servidor deve estar rodando no computador principal

### 🖥️ **Como Acessar:**

1. **Abra qualquer navegador** (Chrome, Firefox, Safari, Edge)
2. **Digite ou cole o link** na barra de endereços:
   ```
   http://192.168.43.222:8000/dashboard/
   ```
3. **Pressione Enter** e o dashboard carregará automaticamente

### 📊 **O que você verá:**
- ✅ **Dados em tempo real** do estoque
- ✅ **Análise Curva ABC** com gráficos interativos
- ✅ **Métricas de desempenho** atualizadas
- ✅ **300+ produtos reais** do Tiny ERP

### 🔧 **Resolução de Problemas:**

#### ❌ **Se não conseguir acessar:**
1. Verifique se ambos os computadores estão na mesma rede
2. Teste se o link funciona no computador principal primeiro
3. Verifique se o firewall não está bloqueando a porta 8000

#### 🛡️ **Liberar no Firewall (se necessário):**
1. Abra o **Painel de Controle**
2. Vá em **Sistema e Segurança** > **Firewall do Windows**
3. Clique em **Configurações Avançadas**
4. Crie uma **Nova Regra de Entrada**:
   - Tipo: **Porta**
   - Protocolo: **TCP**
   - Porta: **8000**
   - Ação: **Permitir conexão**

### 📱 **Funciona em:**
- 💻 **Computadores** (Windows, Mac, Linux)
- 📱 **Smartphones** (Android, iPhone)
- 📟 **Tablets** (iPad, Android)

### ⚠️ **Importante:**
- O dashboard ficará disponível enquanto o servidor estiver rodando
- Para parar o servidor: `Ctrl + C` no terminal
- Para iniciar novamente: rode o comando uvicorn

---

## 🚀 **Link Direto:**
### http://192.168.43.222:8000/dashboard/

*Dashboard criado por Náutica Refrigeração - Dados em tempo real do Tiny ERP*