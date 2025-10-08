# 🌐 Configuração Ngrok - Acesso Via Internet

## 📋 Passo a Passo para Configurar

### 1️⃣ **Criar Conta Ngrok (GRATUITO)**
1. Acesse: https://dashboard.ngrok.com/signup
2. Crie uma conta gratuita (pode usar Google/GitHub)
3. Confirme seu email

### 2️⃣ **Obter Token de Autenticação**
1. Acesse: https://dashboard.ngrok.com/get-started/your-authtoken
2. Copie seu authtoken (algo como: `2abc123def456...`)

### 3️⃣ **Configurar o Token**
Execute este comando no PowerShell (substitua SEU_TOKEN pelo token copiado):
```powershell
.\ngrok.exe config add-authtoken SEU_TOKEN_AQUI
```

### 4️⃣ **Criar o Túnel**
Depois de configurar o token, execute:
```powershell
.\ngrok.exe http 8000
```

### 5️⃣ **Obter Link Público**
O Ngrok mostrará algo assim:
```
Forwarding    https://abc123.ngrok-free.app -> http://localhost:8000
```

### 6️⃣ **Compartilhar o Dashboard**
Compartilhe o link público (ex: `https://abc123.ngrok-free.app/dashboard/`)

---

## 🚀 **Alternativa Rápida: Serveo (Sem Cadastro)**

Se preferir uma opção sem cadastro, posso configurar o Serveo:

### **Comando Serveo:**
```powershell
ssh -R 80:localhost:8000 serveo.net
```

---

## ⚠️ **Importante:**
- ✅ **Ngrok Gratuito**: 1 túnel ativo, 120 conexões/minuto
- ✅ **Link funciona em qualquer lugar do mundo**
- ✅ **HTTPS automático**
- ✅ **Válido enquanto o túnel estiver ativo**

---

## 📞 **Status Atual:**
- ✅ Servidor rodando na porta 8000
- ✅ Ngrok baixado e pronto
- ⏳ Aguardando configuração do authtoken

### **Próximos passos:**
1. Criar conta no Ngrok
2. Configurar authtoken
3. Executar `.\ngrok.exe http 8000`
4. Compartilhar o link gerado!