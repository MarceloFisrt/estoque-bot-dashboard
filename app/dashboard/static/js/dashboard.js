// Dashboard Estoque Bot - Versão Otimizada
// === CONFIGURAÇÕES GLOBAIS ===
const API_BASE = 'http://127.0.0.1:8000';

// Variáveis globais para os gráficos
let curvaChart = null;
let donutChart = null; 
let trendChart = null;
let evolutionChart = null;

// Configurações do Chart.js
Chart.defaults.animation.duration = 750;
Chart.defaults.animation.easing = 'easeInOutCubic';
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = false;

// === FUNÇÕES UTILITÁRIAS ===
function showLoading() {
    // Mostra indicador de carregamento se necessário
}

function hideLoading() {
    // Esconde indicador de carregamento se necessário
}

function ensureCanvasExists(id) {
    const canvas = document.getElementById(id);
    if (!canvas) {
        console.error(`❌ Canvas não encontrado: ${id}`);
        return false;
    }

    return true;
}

// === FUNÇÕES DE API ===
async function fetchDashboardData() {
    try {
    
        const response = await fetch(`${API_BASE}/dashboard/dados`);
    
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
    
    
    
        return data;
    } catch (error) {
        console.error('❌ Erro ao buscar dados dashboard:', error);
        throw error;
    }
}

async function fetchCurvaData() {
    try {
    
        const response = await fetch(`${API_BASE}/curvaabc`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
    
        return data;
    } catch (error) {
        console.error('❌ Erro ao buscar curva ABC:', error);
        throw error;
    }
}

async function fetchEvolucaoData(inicio, fim) {
    try {
    
        const url = `${API_BASE}/curvaabc/evolucao?inicio=${inicio}&fim=${fim}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
    
        return data;
    } catch (error) {
        console.error('❌ Erro ao buscar evolução:', error);
        throw error;
    }
}

// === FUNÇÕES DE ATUALIZAÇÃO DOS CARDS ===
function updateStatsCards(data) {


    
    // Valor Total (Lucro)
    const valorTotal = document.getElementById('valorTotal');
    if (valorTotal) {
        const valor = data.lucro_total || 0;
        valorTotal.textContent = `R$ ${valor.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
    
    }
    
    // Vendas do Mês (nova métrica)
    const vendasMes = document.getElementById('vendasMes');
    if (vendasMes) {
        const vendas = data.vendas_mes || data.lucro_total * 1.3 || 0;
        vendasMes.textContent = `R$ ${vendas.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
    
    }
    
    // Meta Mensal
    const metaMensal = document.getElementById('metaMensal');
    if (metaMensal) {
        const meta = data.meta_mensal || 25000;
        metaMensal.textContent = `R$ ${meta.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
    
    }
    
    // Crescimento
    const crescimento = document.getElementById('crescimento');
    if (crescimento) {
        const cresc = data.crescimento || 0;
        crescimento.textContent = `${cresc.toFixed(1)}%`;
        crescimento.className = cresc >= 0 ? 'text-success' : 'text-danger';
    
    }
    
    // Curvas ABC
    const curvaA = document.getElementById('curvaA');
    const curvaB = document.getElementById('curvaB');
    const curvaC = document.getElementById('curvaC');
    const totalProdutos = document.getElementById('totalProdutos');
    
    if (curvaA) {
        curvaA.textContent = data.curvaA || 0;
    
    }
    if (curvaB) {
        curvaB.textContent = data.curvaB || 0;
    
    }
    if (curvaC) {
        curvaC.textContent = data.curvaC || 0;
    
    }
    if (totalProdutos) {
        totalProdutos.textContent = data.total_produtos || 0;
    
    }
    
    // Atualização e Fonte
    const ultimaAtualizacao = document.getElementById('ultimaAtualizacao');
    if (ultimaAtualizacao) {
        ultimaAtualizacao.textContent = data.atualizacao || new Date().toLocaleString('pt-BR');
    }
    
    const fonteInfo = document.getElementById('fonteInfo');
    if (fonteInfo) {
        fonteInfo.textContent = data.fonte || 'Sistema';
    }
    
    // Status de filtros
    if (data.filtro_aplicado) {
        const statusFiltro = document.getElementById('statusFiltro');
        if (statusFiltro) {
            statusFiltro.textContent = `Filtros: Curva ${data.filtro_curva}, Produto: ${data.filtro_produto}`;
            statusFiltro.className = 'badge bg-info';
        }
    }
    

}

// === FUNÇÕES DE GRÁFICOS ===
function createCurvaChart(data) {
    console.log('🔧 DEBUG: createCurvaChart chamada com dados:', data);
    
    if (!ensureCanvasExists('curvaChart')) {
        console.error('❌ Canvas curvaChart não encontrado!');
        return;
    }
    
    console.log('✅ Canvas curvaChart encontrado');

    const ctx = document.getElementById('curvaChart').getContext('2d');
    
    if (curvaChart) {
        console.log('🔄 Destruindo gráfico anterior');
        curvaChart.destroy();
    }
    
    const chartData = [data.curvaA || 0, data.curvaB || 0, data.curvaC || 0];
    console.log('📊 Dados do gráfico:', chartData);
    
    curvaChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Curva A', 'Curva B', 'Curva C'],
            datasets: [{
                label: 'Produtos por Curva',
                data: chartData,
                backgroundColor: [
                    'rgba(220, 53, 69, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(40, 167, 69, 0.8)'
                ],
                borderColor: [
                    'rgba(220, 53, 69, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(40, 167, 69, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Distribuição por Curva ABC'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Quantidade de Produtos'
                    }
                }
            }
        }
    });
    
    console.log('✅ Gráfico curvaChart criado com sucesso');
}

function createDonutChart(data) {
    if (!ensureCanvasExists('donutChart')) return;
    

    const ctx = document.getElementById('donutChart').getContext('2d');
    
    if (donutChart) {
        donutChart.destroy();
    }
    
    // Dados de exemplo para produtos em alta
    const produtos = data.produtos_alta || [
        {nome: 'Produto A', valor: 15},
        {nome: 'Produto B', valor: 12},
        {nome: 'Produto C', valor: 10},
        {nome: 'Produto D', valor: 8},
        {nome: 'Outros', valor: 5}
    ];
    
    donutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: produtos.map(p => p.nome),
            datasets: [{
                data: produtos.map(p => p.valor),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Top Produtos'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    

}

function createTrendChart(data) {
    if (!ensureCanvasExists('trendChart')) return;
    

    const ctx = document.getElementById('trendChart').getContext('2d');
    
    if (trendChart) {
        trendChart.destroy();
    }
    
    const meses = data.meses || ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul'];
    const curvaA = data.A || [21, 26, 24, 19, 28, 27, 6];
    const curvaB = data.B || [6, 18, 9, 17, 16, 11, 2];
    const curvaC = data.C || [10, 14, 9, 8, 12, 10, 7];
    
    trendChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: meses,
            datasets: [
                {
                    label: 'Curva A',
                    data: curvaA,
                    backgroundColor: 'rgba(220, 53, 69, 0.8)',
                    borderColor: 'rgba(220, 53, 69, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Curva B',
                    data: curvaB,
                    backgroundColor: 'rgba(255, 193, 7, 0.8)',
                    borderColor: 'rgba(255, 193, 7, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Curva C',
                    data: curvaC,
                    backgroundColor: 'rgba(40, 167, 69, 0.8)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 2
                }
            ]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Evolução das Curvas por Período'
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    stacked: false,
                    title: {
                        display: true,
                        text: 'Quantidade de Produtos'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Período'
                    }
                }
            }
        }
    });
    

}

function createEvolutionChart() {
    if (!ensureCanvasExists('curvaEvolutionChart')) return;
    

    const ctx = document.getElementById('curvaEvolutionChart').getContext('2d');
    
    if (evolutionChart) {
        evolutionChart.destroy();
    }
    
    // Dados simulados de evolução financeira
    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'];
    const vendas = [45000, 52000, 48000, 61000, 55000, 67000];
    const custos = [30000, 35000, 32000, 40000, 38000, 42000];
    const lucros = vendas.map((v, i) => v - custos[i]);
    
    evolutionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: meses,
            datasets: [
                {
                    label: 'Vendas',
                    data: vendas,
                    borderColor: 'rgba(40, 167, 69, 1)',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Custos',
                    data: custos,
                    borderColor: 'rgba(220, 53, 69, 1)',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Lucro',
                    data: lucros,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Evolução Financeira Mensal'
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Valor (R$)'
                    },
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toLocaleString('pt-BR');
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Mês'
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    });
    

}

// === FUNÇÃO PRINCIPAL DE CARREGAMENTO ===
async function initDashboard() {

    showLoading();
    
    try {
        // Carregar dados básicos
    
        const dashboardData = await fetchDashboardData();
        
        // Atualizar cards
    
        updateStatsCards(dashboardData);
        
        // Criar gráficos básicos
    
        createCurvaChart(dashboardData);
        createDonutChart(dashboardData);
        
        // Carregar e criar gráfico de evolução
    
        const evolucaoData = await fetchEvolucaoData('2025-04-01', '2025-10-31');
        createTrendChart(evolucaoData);
        
        // Criar gráfico de evolução financeira
    
        createEvolutionChart();
        
    
        
    } catch (error) {
        console.error('❌ Erro ao inicializar dashboard:', error);
        
        // Dados de fallback em caso de erro
        const fallbackData = {
            lucro_total: 150000,
            curvaA: 25,
            curvaB: 35,
            curvaC: 40
        };
        
    
        updateStatsCards(fallbackData);
        createCurvaChart(fallbackData);
        createDonutChart(fallbackData);
        createTrendChart({
            meses: ['Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out'],
            A: [21, 26, 24, 19, 28, 27, 6],
            B: [6, 18, 9, 17, 16, 11, 2],
            C: [10, 14, 9, 8, 12, 10, 7]
        });
        createEvolutionChart();
    }
    
    hideLoading();
}

// === EVENTOS DE FILTROS ===
// === FUNÇÕES DE PRODUTOS COM LOCALIZAÇÃO ===
async function fetchProdutosPorCurva(curva = '') {
    try {
    
        const url = curva ? `${API_BASE}/produtos/curva/${curva}` : `${API_BASE}/curva-abc`;
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
    
        return data;
    } catch (error) {
        console.error('❌ Erro ao buscar produtos:', error);
        return [];
    }
}

function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor || 0);
}

function getCurvaEmoji(curva) {
    switch(curva) {
        case 'A': return '🏆';
        case 'B': return '🥈';
        case 'C': return '🥉';
        default: return '📦';
    }
}

function exibirProdutos(produtos) {

    const container = document.getElementById('produtosLista');
    
    if (!container) {
        console.error('❌ Container produtosLista não encontrado');
        return;
    }
    
    if (!produtos || produtos.length === 0) {
        container.innerHTML = `
            <div class="loading-produtos">
                <p>📭 Nenhum produto encontrado</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    produtos.forEach((produto, index) => {
        const sku = produto.sku || 'N/A';
        const nome = produto.name || produto.nome || 'Produto sem nome';
        const estoque = produto.stock || produto.estoque || 0;
        const curva = produto.curve || produto.curva || 'C';
        const salePrice = produto.sale_price || produto.preco || 0;
        const valorEstoque = salePrice * estoque;
        const localizacao = produto.location || produto.localizacao || 'Não informado';
        
        const curvaEmoji = getCurvaEmoji(curva);
        const curvaClass = `curva-${curva.toLowerCase()}`;
        
        html += `
            <div class="produto-row ${curvaClass}">
                <div class="produto-cell sku">${sku}</div>
                <div class="produto-cell nome" title="${nome}">${nome}</div>
                <div class="produto-cell estoque">${estoque}</div>
                <div class="produto-cell curva">${curvaEmoji}</div>
                <div class="produto-cell localizacao" title="${localizacao}">${localizacao}</div>
                <div class="produto-cell valor">${formatarMoeda(valorEstoque)}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;

}

function setupProdutosEventListeners() {

    
    const curvaFilter = document.getElementById('curvaFilter');
    const refreshBtn = document.getElementById('refreshProdutos');
    
    if (curvaFilter) {
        curvaFilter.addEventListener('change', async function() {
            const curvaSelecionada = this.value;
        
            
            document.getElementById('produtosLista').innerHTML = `
                <div class="loading-produtos">
                    <p>🔄 Carregando produtos...</p>
                </div>
            `;
            
            const produtos = await fetchProdutosPorCurva(curvaSelecionada);
            exibirProdutos(produtos);
        });
    }
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async function() {
        
            
            this.disabled = true;
            this.textContent = '🔄 Carregando...';
            
            document.getElementById('produtosLista').innerHTML = `
                <div class="loading-produtos">
                    <p>🔄 Atualizando produtos...</p>
                </div>
            `;
            
            const curvaFilter = document.getElementById('curvaFilter');
            const curvaSelecionada = curvaFilter ? curvaFilter.value : '';
            
            const produtos = await fetchProdutosPorCurva(curvaSelecionada);
            exibirProdutos(produtos);
            
            this.textContent = '🔄 Atualizar';
            this.disabled = false;
        });
    }
}

async function initProdutos() {

    
    setupProdutosEventListeners();
    
    // Carregar produtos iniciais
    document.getElementById('produtosLista').innerHTML = `
        <div class="loading-produtos">
            <p>🔄 Carregando produtos...</p>
        </div>
    `;
    
    const produtos = await fetchProdutosPorCurva();
    exibirProdutos(produtos);
    

}

function setupEventListeners() {

    
    const filtrarBtn = document.getElementById('filtrarEvolucao');
    const dataInicio = document.getElementById('dataInicio');
    const dataFim = document.getElementById('dataFim');
    
    // Definir datas padrão
    if (dataInicio) dataInicio.value = '2025-04-01';
    if (dataFim) dataFim.value = '2025-10-31';
    
    // Event listener do botão filtrar
    if (filtrarBtn) {
        filtrarBtn.addEventListener('click', async function() {
        
            const inicio = dataInicio.value;
            const fim = dataFim.value;
            
            if (!inicio || !fim) {
                alert('Por favor, selecione as datas de início e fim.');
                return;
            }
            
            try {
                filtrarBtn.disabled = true;
                filtrarBtn.textContent = 'Carregando...';
                
                const evolucaoData = await fetchEvolucaoData(inicio, fim);
                createTrendChart(evolucaoData);
                
                filtrarBtn.textContent = 'Filtrar';
                filtrarBtn.disabled = false;
            
                
            } catch (error) {
                console.error('❌ Erro ao aplicar filtro:', error);
                alert('Erro ao carregar dados. Tente novamente.');
                filtrarBtn.textContent = 'Filtrar';
                filtrarBtn.disabled = false;
            }
        });
    }
    

}

// === INICIALIZAÇÃO ===
document.addEventListener('DOMContentLoaded', function() {

    setupEventListeners();
    initDashboard();
    initProdutos(); // Inicializar seção de produtos
    initTabs(); // Inicializar abas
    initProdutoFilters(); // Inicializar filtros de produtos
});

console.log('✅ Script dashboard.js carregado');

// === FUNCIONALIDADE DAS ABAS ===

// Funcionalidade das abas
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            
            // Remove active de todas as abas
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Adiciona active na aba clicada
            btn.classList.add('active');
            document.getElementById(`${tabName}-content`).classList.add('active');
            
            // Carrega conteúdo específico da aba
            if (tabName === 'produtos') {
                loadProdutos();
            }
        });
    });
}

// === FUNCIONALIDADE DA ABA PRODUTOS ===

// Carrega lista de produtos
let todosProdutos = [];

async function loadProdutos() {
    const loading = document.getElementById('produtosLoading');
    const tableBody = document.getElementById('produtosTableBody');
    
    if (loading) loading.style.display = 'block';
    
    try {
        const response = await fetch('/api/produtos');
        const produtos = await response.json();
        
        todosProdutos = produtos;
        displayProdutos(produtos);
        updateProdutosStats(produtos);
        
    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
        if (tableBody) {
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">Erro ao carregar produtos</td></tr>';
        }
    } finally {
        if (loading) loading.style.display = 'none';
    }
}

// Exibe produtos na tabela
function displayProdutos(produtos) {
    const tableBody = document.getElementById('produtosTableBody');
    
    if (!tableBody) return;
    
    if (produtos.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">Nenhum produto encontrado</td></tr>';
        return;
    }
    
    tableBody.innerHTML = produtos.map(produto => {
        const estoque = parseFloat(produto.estoque_atual) || 0;
        const valorUnitario = parseFloat(produto.preco_venda) || 0;
        const valorTotal = estoque * valorUnitario;
        
        const estoqueClass = estoque > 0 ? 'estoque-positivo' : 'estoque-zero';
        const estoqueText = estoque > 0 ? estoque.toFixed(2) : 'Sem estoque';
        
        const curvaText = produto.curva_abc || 'N/A';
        const curvaClass = `curva-${curvaText}`;
        const curvaEmoji = curvaText === 'A' ? '💎' : curvaText === 'B' ? '⭐' : '🌟';
        
        return `
            <tr>
                <td><strong>${produto.codigo}</strong></td>
                <td>${produto.nome}</td>
                <td>
                    <span class="estoque-badge ${estoqueClass}">
                        ${estoqueText}
                    </span>
                </td>
                <td>${produto.localizacao || 'Não informado'}</td>
                <td>R$ ${valorUnitario.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
                <td>R$ ${valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
                <td>
                    <span class="curva-badge ${curvaClass}">
                        ${curvaEmoji} ${curvaText}
                    </span>
                </td>
            </tr>
        `;
    }).join('');
}

// Atualiza estatísticas dos produtos
function updateProdutosStats(produtos) {
    const totalProdutos = document.getElementById('totalProdutos');
    const produtosComEstoque = document.getElementById('produtosComEstoque');
    const produtosSemEstoque = document.getElementById('produtosSemEstoque');
    
    const comEstoque = produtos.filter(p => parseFloat(p.estoque_atual) > 0).length;
    const semEstoque = produtos.length - comEstoque;
    
    if (totalProdutos) totalProdutos.textContent = produtos.length;
    if (produtosComEstoque) produtosComEstoque.textContent = comEstoque;
    if (produtosSemEstoque) produtosSemEstoque.textContent = semEstoque;
}

// === FILTROS DOS PRODUTOS ===

// Filtros dos produtos
function initProdutoFilters() {
    const curvaFilter = document.getElementById('curvaFilter');
    const estoqueFilter = document.getElementById('estoqueFilter');
    const pesquisaInput = document.getElementById('pesquisaProduto');
    
    if (curvaFilter) {
        curvaFilter.addEventListener('change', filterProdutos);
    }
    
    if (estoqueFilter) {
        estoqueFilter.addEventListener('change', filterProdutos);
    }
    
    if (pesquisaInput) {
        pesquisaInput.addEventListener('input', filterProdutos);
    }
}

function filterProdutos() {
    const curvaFilter = document.getElementById('curvaFilter');
    const estoqueFilter = document.getElementById('estoqueFilter');
    const pesquisaInput = document.getElementById('pesquisaProduto');
    
    const curvaFiltro = curvaFilter ? curvaFilter.value : '';
    const estoqueFiltro = estoqueFilter ? estoqueFilter.value : '';
    const pesquisaFiltro = pesquisaInput ? pesquisaInput.value.toLowerCase() : '';
    
    let produtosFiltrados = todosProdutos.filter(produto => {
        // Filtro por curva
        if (curvaFiltro && produto.curva_abc !== curvaFiltro) {
            return false;
        }
        
        // Filtro por estoque
        const estoque = parseFloat(produto.estoque_atual) || 0;
        if (estoqueFiltro === 'com-estoque' && estoque <= 0) {
            return false;
        }
        if (estoqueFiltro === 'sem-estoque' && estoque > 0) {
            return false;
        }
        
        // Filtro por pesquisa
        if (pesquisaFiltro) {
            const nome = produto.nome.toLowerCase();
            const codigo = produto.codigo.toLowerCase();
            if (!nome.includes(pesquisaFiltro) && !codigo.includes(pesquisaFiltro)) {
                return false;
            }
        }
        
        return true;
    });
    
    displayProdutos(produtosFiltrados);
    updateProdutosStats(produtosFiltrados);
}

// === FUNÇÕES PARA RELATÓRIOS ===

// Funções para relatórios
function gerarRelatorioABC() {
    alert('Funcionalidade de relatório ABC em desenvolvimento');
}

function gerarRelatorioMovimentacao() {
    alert('Funcionalidade de relatório de movimentação em desenvolvimento');
}

function gerarRelatorioLocalizacao() {
    alert('Funcionalidade de relatório de localização em desenvolvimento');
}

// === FUNÇÕES PARA TEMPO REAL ===

let autoRefreshInterval = null;
let dadosTempoRealCache = null;

async function buscarDadosTempoReal() {
    try {
        // Atualizar status
        updateTempoRealStatus('loading', 'Buscando dados...');
        
        // Obter filtros selecionados
        const filtros = obterFiltrosSelecionados();
        
        // Fazer requisição
        const response = await fetch(`${API_BASE}/api/tempo-real/produtos?filtros=${filtros.join(',')}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const dados = await response.json();
        
        // Cache dos dados
        dadosTempoRealCache = dados;
        
        // Atualizar interface
        updateTempoRealData(dados);
        updateTempoRealStatus('online', `Última atualização: ${new Date().toLocaleTimeString()}`);
        
        console.log('✅ Dados tempo real atualizados:', dados.estatisticas);
        
    } catch (error) {
        console.error('❌ Erro ao buscar dados tempo real:', error);
        updateTempoRealStatus('offline', 'Erro na conexão');
        showToast('Erro ao buscar dados em tempo real', 'error');
    }
}

function obterFiltrosSelecionados() {
    const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function updateTempoRealStatus(status, message) {
    const statusIndicator = document.querySelector('.status-indicator');
    const lastUpdate = document.querySelector('.last-update');
    
    if (statusIndicator) {
        statusIndicator.className = `status-indicator ${status}`;
        
        const statusIcons = {
            'online': '🟢',
            'offline': '🔴',
            'loading': '🟡'
        };
        
        const statusTexts = {
            'online': 'Conectado',
            'offline': 'Desconectado',
            'loading': 'Carregando...'
        };
        
        statusIndicator.textContent = `${statusIcons[status]} ${statusTexts[status]}`;
    }
    
    if (lastUpdate) {
        lastUpdate.textContent = message;
    }
}

function updateTempoRealData(dados) {
    const stats = dados.estatisticas;
    
    // Atualizar KPIs
    updateElement('totalEncontrados', stats.total_encontrados);
    updateElement('comEstoque', stats.com_estoque);
    updateElement('semEstoque', stats.sem_estoque);
    updateElement('valorTotalEstoque', `R$ ${stats.valor_total_estoque.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
    
    // Atualizar distribuição por categoria
    updateCategoriasGrid(stats.por_categoria);
    
    // Atualizar produtos destaque
    updateProdutosDestaque(dados.produtos, stats);
    
    // Atualizar lista de produtos
    updateProdutosTempoRealList(dados.produtos);
}

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function updateCategoriasGrid(porCategoria) {
    const grid = document.getElementById('categoriasGrid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    Object.entries(porCategoria).forEach(([categoria, count]) => {
        const card = document.createElement('div');
        card.className = 'categoria-card';
        card.innerHTML = `
            <div class="categoria-nome">${categoria}*</div>
            <div class="categoria-count">${count}</div>
        `;
        grid.appendChild(card);
    });
}

function updateProdutosDestaque(produtos, stats) {
    const container = document.getElementById('produtosDestaque');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Produto mais caro
    if (stats.produto_mais_caro) {
        const produtoMaisCaro = stats.produto_mais_caro;
        const item = document.createElement('div');
        item.className = 'produto-destaque-item';
        item.innerHTML = `
            <div class="produto-destaque-nome">💰 Mais Caro: ${produtoMaisCaro.sku}</div>
            <div class="produto-destaque-info">${produtoMaisCaro.nome} - R$ ${produtoMaisCaro.preco_venda.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
        `;
        container.appendChild(item);
    }
    
    // Produto com maior estoque
    if (stats.produto_maior_estoque) {
        const produtoMaiorEstoque = stats.produto_maior_estoque;
        const item = document.createElement('div');
        item.className = 'produto-destaque-item';
        item.innerHTML = `
            <div class="produto-destaque-nome">📦 Maior Estoque: ${produtoMaiorEstoque.sku}</div>
            <div class="produto-destaque-info">${produtoMaiorEstoque.nome} - ${produtoMaiorEstoque.estoque_atual} unidades</div>
        `;
        container.appendChild(item);
    }
}

function updateProdutosTempoRealList(produtos) {
    const container = document.getElementById('produtosTempoRealList');
    if (!container) return;
    
    // Aplicar filtro de pesquisa se houver
    const filtro = document.getElementById('filtrarProdutoTR')?.value.toLowerCase() || '';
    const produtosFiltrados = produtos.filter(p => 
        p.sku.toLowerCase().includes(filtro) || 
        p.nome.toLowerCase().includes(filtro)
    );
    
    // Aplicar ordenação
    const ordenacao = document.getElementById('ordenarPorTR')?.value || 'estoque';
    produtosFiltrados.sort((a, b) => {
        switch (ordenacao) {
            case 'estoque':
                return b.estoque_atual - a.estoque_atual;
            case 'preco':
                return b.preco_venda - a.preco_venda;
            case 'valor':
                return b.valor_total - a.valor_total;
            case 'alfabetico':
                return a.nome.localeCompare(b.nome);
            default:
                return 0;
        }
    });
    
    // Cabeçalho
    container.innerHTML = `
        <div class="produto-tempo-real" style="font-weight: 600; background: #f8f9fa; color: #495057;">
            <div class="produto-sku">SKU</div>
            <div class="produto-nome">Nome</div>
            <div class="produto-estoque">Estoque</div>
            <div class="produto-preco">Preço</div>
            <div class="produto-valor-total">Valor Total</div>
            <div class="produto-localizacao">Localização</div>
        </div>
    `;
    
    // Produtos
    produtosFiltrados.slice(0, 50).forEach(produto => { // Limitar a 50 para performance
        const row = document.createElement('div');
        row.className = 'produto-tempo-real';
        
        const temEstoque = produto.estoque_atual > 0;
        const estoqueClass = temEstoque ? 'com-estoque' : 'sem-estoque';
        
        row.innerHTML = `
            <div class="produto-sku">${produto.sku}</div>
            <div class="produto-nome" title="${produto.nome}">${produto.nome}</div>
            <div class="produto-estoque ${estoqueClass}">${produto.estoque_atual}</div>
            <div class="produto-preco">R$ ${produto.preco_venda.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
            <div class="produto-valor-total">R$ ${produto.valor_total.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
            <div class="produto-localizacao" title="${produto.localizacao}">${produto.localizacao}</div>
        `;
        
        container.appendChild(row);
    });
    
    // Mostrar total
    if (produtosFiltrados.length > 50) {
        const moreRow = document.createElement('div');
        moreRow.className = 'produto-tempo-real';
        moreRow.style.fontStyle = 'italic';
        moreRow.style.color = '#6b7280';
        moreRow.innerHTML = `
            <div colspan="6" style="grid-column: 1 / -1; text-align: center; padding: 1rem;">
                ... e mais ${produtosFiltrados.length - 50} produtos
            </div>
        `;
        container.appendChild(moreRow);
    }
}

function toggleAutoRefresh() {
    const checkbox = document.getElementById('autoRefresh');
    
    if (checkbox.checked) {
        // Iniciar auto-refresh a cada 30 segundos
        autoRefreshInterval = setInterval(buscarDadosTempoReal, 30000);
        console.log('✅ Auto-refresh ativado (30s)');
    } else {
        // Parar auto-refresh
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
        console.log('⏹️ Auto-refresh desativado');
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.querySelector('.toast-message');
    
    if (!toast || !toastMessage) return;
    
    // Definir cor baseada no tipo
    const colors = {
        'info': '#3498db',
        'success': '#2ecc71',
        'error': '#e74c3c',
        'warning': '#f39c12'
    };
    
    toast.style.background = colors[type] || colors.info;
    toastMessage.textContent = message;
    
    // Mostrar toast
    toast.classList.add('show');
    
    // Esconder após 3 segundos
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Event Listeners para Tempo Real
document.addEventListener('DOMContentLoaded', function() {
    // Botão buscar tempo real
    const btnBuscar = document.getElementById('buscarTempoReal');
    if (btnBuscar) {
        btnBuscar.addEventListener('click', buscarDadosTempoReal);
    }
    
    // Auto-refresh checkbox
    const autoRefreshCheckbox = document.getElementById('autoRefresh');
    if (autoRefreshCheckbox) {
        autoRefreshCheckbox.addEventListener('change', toggleAutoRefresh);
    }
    
    // Filtros de produto tempo real
    const filtrarProduto = document.getElementById('filtrarProdutoTR');
    if (filtrarProduto) {
        filtrarProduto.addEventListener('input', () => {
            if (dadosTempoRealCache) {
                updateProdutosTempoRealList(dadosTempoRealCache.produtos);
            }
        });
    }
    
    // Ordenação produtos tempo real
    const ordenarPor = document.getElementById('ordenarPorTR');
    if (ordenarPor) {
        ordenarPor.addEventListener('change', () => {
            if (dadosTempoRealCache) {
                updateProdutosTempoRealList(dadosTempoRealCache.produtos);
            }
        });
    }
});
