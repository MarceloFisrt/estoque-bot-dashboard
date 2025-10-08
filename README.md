# 📊 Dashboard de Estoque Interativo

![Dashboard Preview](https://img.shields.io/badge/Status-✅%20Funcionando-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![Chart.js](https://img.shields.io/badge/Chart.js-Interactive-orange)

## 🎯 **Visão Geral**

Dashboard moderno e interativo para gerenciamento de estoque com classificação ABC, alertas inteligentes e visualizações em tempo real.

## ✨ **Funcionalidades Principais**

### 📈 **Dashboard Interativo**
- **Gráficos dinâmicos** com Chart.js (barras, donut, linha)
- **Animações suaves** e efeitos hover responsivos
- **Auto-refresh** a cada 30 segundos
- **Interface moderna** com gradientes e design responsivo

### 🎯 **Sistema de Curva ABC**
- **Classificação automática** de produtos por importância
- **Visualização clara** da distribuição por categorias
- **Análise de performance** por curva

### 🚨 **Alertas Inteligentes**
- **Monitoramento automático** de estoque baixo
- **Notificações em tempo real** para produtos críticos (Curva A ≤ 5 unidades)
- **Sistema de badges** no menu lateral
- **Toast notifications** discretas

### 📱 **Design Responsivo**
- **Layout adaptativo** para desktop, tablet e mobile
- **Cards KPI** com efeitos de hover e animações
- **Sidebar moderna** com navegação intuitiva
- **Background animado** com gradiente dinâmico

## 🚀 **Como Executar**

### **Pré-requisitos**
- Python 3.11+
- Git
- Virtual Environment (recomendado)

### **1. Clone o Repositório**
```bash
git clone https://github.com/MarceloFisrt/estoque-bot-dashboard.git
cd estoque-bot-dashboard
```

### **2. Configure o Ambiente Virtual**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### **3. Instale as Dependências**
```bash
pip install -r requirements.txt
```

### **4. Configure o Banco de Dados**
```bash
# O banco SQLite será criado automaticamente
# Dados de exemplo já estão incluídos
```

### **5. Execute o Servidor**
```bash
# Opção 1: Usar o script personalizado (recomendado)
python server.py

# Opção 2: Usar uvicorn diretamente
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **6. Acesse o Dashboard**
```
🌐 Dashboard: http://127.0.0.1:8000/dashboard/
📊 API Docs: http://127.0.0.1:8000/docs
💚 Health: http://127.0.0.1:8000/health
```

## 🎨 **Capturas de Tela**

### Dashboard Principal
- Cards KPI com valores em tempo real
- Gráficos interativos com hover effects
- Sistema de alertas integrado

### Gráficos Interativos
- **Barras**: Distribuição por Curva ABC
- **Donut**: Produtos em alta (Top 5 Curva A)
- **Linha**: Análise de tendências

## 📡 **APIs Disponíveis**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/dashboard/dados` | GET | Estatísticas gerais do dashboard |
| `/curvaabc` | GET | Todos os produtos com classificação ABC |
| `/curva/{A\|B\|C}` | GET | Produtos por categoria específica |
| `/health` | GET | Status de saúde da aplicação |
| `/docs` | GET | Documentação interativa (Swagger) |

## 🎭 **Recursos Visuais**

### **Animações Suaves**
- Transições CSS com `cubic-bezier`
- Efeitos de hover em todos os elementos
- Loading animations coordenadas
- Background com gradiente animado

### **Interatividade**
- **Gráficos**: Hover com tooltips informativos
- **Cards**: Elevação e rotação suaves
- **Botões**: Ripple effect
- **Cursor**: Muda contextualmente (pointer/crosshair)

### **Responsive Design**
- Grid flexível para diferentes telas
- Typography escalável
- Layout adaptativo
- Sidebar colapsável (mobile)

## 🔧 **Estrutura do Projeto**

```
estoque-bot-dashboard/
├── app/
│   ├── dashboard/
│   │   ├── index.html          # Interface principal
│   │   └── static/
│   │       ├── css/style.css   # Estilos modernos
│   │       └── js/dashboard.js # Lógica interativa
│   ├── main.py                 # FastAPI app
│   ├── models.py               # Modelos SQLAlchemy
│   ├── crud.py                 # Lógica de negócio
│   └── database.py             # Configuração DB
├── server.py                   # Script de inicialização
├── requirements.txt            # Dependências
└── README.md                   # Este arquivo
```

## 📊 **Dados de Exemplo**

O sistema vem com **1,699 produtos** pré-carregados:
- **Curva A**: 166 produtos (10%)
- **Curva B**: 324 produtos (19%)
- **Curva C**: 1,209 produtos (71%)

## 🛠 **Tecnologias Utilizadas**

### **Backend**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados leve e eficiente
- **Uvicorn** - Servidor ASGI

### **Frontend**
- **HTML5** - Estrutura semântica
- **CSS3** - Animações e grid layout
- **JavaScript ES6+** - Lógica de interface
- **Chart.js** - Gráficos interativos
- **Font Awesome** - Ícones

## 🎯 **Próximas Funcionalidades**

- [ ] Filtros avançados por categoria
- [ ] Exportação de relatórios (PDF/Excel)
- [ ] Dashboard para mobile (PWA)
- [ ] Integração com APIs externas
- [ ] Sistema de usuários e permissões
- [ ] Previsão de demanda com ML

## 🤝 **Contribuição**

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 **Contato**

**Desenvolvedor**: Marcelo First  
**GitHub**: [@MarceloFisrt](https://github.com/MarceloFisrt)  
**Projeto**: [estoque-bot-dashboard](https://github.com/MarceloFisrt/estoque-bot-dashboard)

---

💡 **Dica**: Para uma experiência completa, execute o dashboard em tela cheia e interaja com os gráficos! Os efeitos visuais foram otimizados para proporcionar uma UX fluida e moderna.

🚀 **Status**: ✅ **Produção Ready** - Dashboard totalmente funcional e otimizado!