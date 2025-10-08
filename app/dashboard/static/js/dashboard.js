// Dashboard Estoque Bot - Versão Reorganizada e Funcional
console.log('🚀 Iniciando Dashboard...');

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
    console.log('⏳ Carregando...');
}

function hideLoading() {
    console.log('✅ Carregado!');
}

function ensureCanvasExists(id) {
    const canvas = document.getElementById(id);
    if (!canvas) {
        console.error(`❌ Canvas não encontrado: ${id}`);
        return false;
    }
    console.log(`✅ Canvas encontrado: ${id}`);
    return true;
}

// === FUNÇÕES DE API ===
async function fetchDashboardData() {
    try {
        console.log('📡 Buscando dados do dashboard...');
        const response = await fetch(`${API_BASE}/dashboard/dados`);
        console.log('📋 Response:', response);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        console.log('📊 Dados dashboard recebidos:', data);
        console.log('📊 Tipo dos dados:', typeof data);
        console.log('📊 Chaves dos dados:', Object.keys(data || {}));
        return data;
    } catch (error) {
        console.error('❌ Erro ao buscar dados dashboard:', error);
        throw error;
    }
}

async function fetchCurvaData() {
    try {
        console.log('📡 Buscando dados curva ABC...');
        const response = await fetch(`${API_BASE}/curvaabc`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        console.log('📈 Dados curva ABC recebidos:', data);
        return data;
    } catch (error) {
        console.error('❌ Erro ao buscar curva ABC:', error);
        throw error;
    }
}

async function fetchEvolucaoData(inicio, fim) {
    try {
        console.log(`📡 Buscando evolução ABC (${inicio} - ${fim})...`);
        const url = `${API_BASE}/curvaabc/evolucao?inicio=${inicio}&fim=${fim}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        console.log('📊 Dados evolução recebidos:', data);
        return data;
    } catch (error) {
        console.error('❌ Erro ao buscar evolução:', error);
        throw error;
    }
}

// === FUNÇÕES DE ATUALIZAÇÃO DOS CARDS ===
function updateStatsCards(data) {
    console.log('📋 Atualizando cards estatísticos...');
    console.log('📋 Dados recebidos para cards:', data);
    
    // Valor Total (Lucro)
    const valorTotal = document.getElementById('valorTotal');
    if (valorTotal) {
        const valor = data.lucro_total || 0;
        valorTotal.textContent = `R$ ${valor.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
        console.log('💰 Lucro Total atualizado:', valorTotal.textContent);
    }
    
    // Vendas do Mês (nova métrica)
    const vendasMes = document.getElementById('vendasMes');
    if (vendasMes) {
        const vendas = data.vendas_mes || data.lucro_total * 1.3 || 0;
        vendasMes.textContent = `R$ ${vendas.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
        console.log('� Vendas do Mês atualizada:', vendasMes.textContent);
    }
    
    // Meta Mensal
    const metaMensal = document.getElementById('metaMensal');
    if (metaMensal) {
        const meta = data.meta_mensal || 25000;
        metaMensal.textContent = `R$ ${meta.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
        console.log('🎯 Meta Mensal atualizada:', metaMensal.textContent);
    }
    
    // Crescimento
    const crescimento = document.getElementById('crescimento');
    if (crescimento) {
        const cresc = data.crescimento || 0;
        crescimento.textContent = `${cresc.toFixed(1)}%`;
        crescimento.className = cresc >= 0 ? 'text-success' : 'text-danger';
        console.log('� Crescimento atualizado:', crescimento.textContent);
    }
    
    // Curvas ABC
    const curvaA = document.getElementById('curvaA');
    const curvaB = document.getElementById('curvaB');
    const curvaC = document.getElementById('curvaC');
    const totalProdutos = document.getElementById('totalProdutos');
    
    if (curvaA) {
        curvaA.textContent = data.curvaA || 0;
        console.log('🅰️ Curva A:', curvaA.textContent);
    }
    if (curvaB) {
        curvaB.textContent = data.curvaB || 0;
        console.log('🅱️ Curva B:', curvaB.textContent);
    }
    if (curvaC) {
        curvaC.textContent = data.curvaC || 0;
        console.log('🆑 Curva C:', curvaC.textContent);
    }
    if (totalProdutos) {
        totalProdutos.textContent = data.total_produtos || 0;
        console.log('📦 Total Produtos:', totalProdutos.textContent);
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
    
    console.log('✅ Cards atualizados com sucesso');
}

// === FUNÇÕES DE GRÁFICOS ===
function createCurvaChart(data) {
    if (!ensureCanvasExists('curvaChart')) return;
    
    console.log('📊 Criando gráfico Curva ABC...');
    const ctx = document.getElementById('curvaChart').getContext('2d');
    
    if (curvaChart) {
        curvaChart.destroy();
    }
    
    const chartData = [data.curvaA || 0, data.curvaB || 0, data.curvaC || 0];
    
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
    
    console.log('✅ Gráfico Curva ABC criado');
}

function createDonutChart(data) {
    if (!ensureCanvasExists('donutChart')) return;
    
    console.log('📊 Criando gráfico donut...');
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
    
    console.log('✅ Gráfico donut criado');
}

function createTrendChart(data) {
    if (!ensureCanvasExists('trendChart')) return;
    
    console.log('📊 Criando gráfico de análise...');
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
    
    console.log('✅ Gráfico de análise criado');
}

function createEvolutionChart() {
    if (!ensureCanvasExists('curvaEvolutionChart')) return;
    
    console.log('📊 Criando gráfico de evolução...');
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
    
    console.log('✅ Gráfico de evolução criado');
}

// === FUNÇÃO PRINCIPAL DE CARREGAMENTO ===
async function initDashboard() {
    console.log('🚀 Inicializando dashboard...');
    showLoading();
    
    try {
        // Carregar dados básicos
        console.log('1️⃣ Carregando dados básicos...');
        const dashboardData = await fetchDashboardData();
        
        // Atualizar cards
        console.log('2️⃣ Atualizando cards...');
        updateStatsCards(dashboardData);
        
        // Criar gráficos básicos
        console.log('3️⃣ Criando gráficos básicos...');
        createCurvaChart(dashboardData);
        createDonutChart(dashboardData);
        
        // Carregar e criar gráfico de evolução
        console.log('4️⃣ Carregando evolução ABC...');
        const evolucaoData = await fetchEvolucaoData('2025-04-01', '2025-10-31');
        createTrendChart(evolucaoData);
        
        // Criar gráfico de evolução financeira
        console.log('5️⃣ Criando gráfico de evolução...');
        createEvolutionChart();
        
        console.log('✅ Dashboard inicializado com sucesso!');
        
    } catch (error) {
        console.error('❌ Erro ao inicializar dashboard:', error);
        
        // Dados de fallback em caso de erro
        const fallbackData = {
            lucro_total: 150000,
            curvaA: 25,
            curvaB: 35,
            curvaC: 40
        };
        
        console.log('🔄 Usando dados de fallback...');
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
function setupEventListeners() {
    console.log('🎯 Configurando event listeners...');
    
    const filtrarBtn = document.getElementById('filtrarEvolucao');
    const dataInicio = document.getElementById('dataInicio');
    const dataFim = document.getElementById('dataFim');
    
    // Definir datas padrão
    if (dataInicio) dataInicio.value = '2025-04-01';
    if (dataFim) dataFim.value = '2025-10-31';
    
    // Event listener do botão filtrar
    if (filtrarBtn) {
        filtrarBtn.addEventListener('click', async function() {
            console.log('🔍 Filtrando dados...');
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
                console.log('✅ Filtro aplicado com sucesso!');
                
            } catch (error) {
                console.error('❌ Erro ao aplicar filtro:', error);
                alert('Erro ao carregar dados. Tente novamente.');
                filtrarBtn.textContent = 'Filtrar';
                filtrarBtn.disabled = false;
            }
        });
    }
    
    console.log('✅ Event listeners configurados');
}

// === INICIALIZAÇÃO ===
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM carregado, iniciando dashboard...');
    setupEventListeners();
    initDashboard();
});

console.log('✅ Script dashboard.js carregado');