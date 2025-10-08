// Dashboard Estoque Bot
const API_BASE = 'http://127.0.0.1:8000';
let curvaChart, donutChart, trendChart;
let alertsData = [];

// Configurações globais do Chart.js para animações suaves
Chart.defaults.animation.duration = 750;
Chart.defaults.animation.easing = 'easeInOutCubic';
Chart.defaults.interaction.mode = 'nearest';
Chart.defaults.interaction.intersect = false;
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = false;

// Inicialização quando a página carrega
document.addEventListener('DOMContentLoaded', async function() {
    // Preloader effect
    showLoadingAnimation();
    
    await initializeDashboard();
    initializeCalendar();
    setupEventListeners();
    
    // Remove loading animation
    hideLoadingAnimation();
});

// Funções de loading animation
function showLoadingAnimation() {
    document.body.style.opacity = '0.8';
    document.body.style.pointerEvents = 'none';
}

function hideLoadingAnimation() {
    document.body.style.opacity = '1';
    document.body.style.pointerEvents = 'auto';
}

async function initializeDashboard() {
    try {
        await loadDashboardData();
        await checkStockAlerts();
    } catch (error) {
        console.error('Erro ao inicializar:', error);
    }
}

async function loadDashboardData() {
    try {
        const response = await fetch(API_BASE + '/dashboard/dados');
        const dashboardData = await response.json();
        
        const curvaResponse = await fetch(API_BASE + '/curvaabc');
        const curvaData = await curvaResponse.json();
        
        updateStatsCards(dashboardData, curvaData);
        updateCharts(dashboardData, curvaData);
        
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
    }
}

function updateStatsCards(dashboardData, curvaData) {
    const valorTotal = curvaData.reduce((total, produto) => {
        return total + (produto.sale_price * produto.stock);
    }, 0);
    
    document.getElementById('valorTotal').textContent = 'R$ ' + valorTotal.toFixed(2);
    document.getElementById('curvaA').textContent = dashboardData.curvaA;
    document.getElementById('curvaB').textContent = dashboardData.curvaB;
    document.getElementById('curvaC').textContent = dashboardData.curvaC;
}

function updateCharts(dashboardData, curvaData) {
    // Se os gráficos já existem, apenas atualiza os dados
    if (curvaChart) {
        updateBarChart(dashboardData);
    } else {
        createBarChart(dashboardData);
    }
    
    if (donutChart) {
        updateDonutChart(curvaData);
    } else {
        createDonutChart(curvaData);
    }
    
    if (trendChart) {
        updateTrendChart();
    } else {
        createTrendChart();
    }
}

// Função para atualizar apenas os dados do gráfico de barras
function updateBarChart(data) {
    curvaChart.data.datasets[0].data = [data.curvaA, data.curvaB, data.curvaC];
    curvaChart.update('show'); // Animação mais suave
}

// Função para atualizar apenas os dados do gráfico donut
function updateDonutChart(curvaData) {
    const produtosEmAlta = curvaData
        .filter(p => p.curva === 'A')
        .slice(0, 5);
    
    donutChart.data.labels = produtosEmAlta.map(p => p.sku);
    donutChart.data.datasets[0].data = produtosEmAlta.map(p => p.sale_price);
    donutChart.update('show'); // Animação mais suave
}

// Função para atualizar o gráfico de tendência (pode ter dados dinâmicos futuramente)
function updateTrendChart() {
    // Por enquanto, apenas faz uma animação suave
    trendChart.update('show'); // Animação mais suave
}

function createBarChart(data) {
    const ctx = document.getElementById('curvaChart').getContext('2d');
    
    if (curvaChart) {
        curvaChart.destroy();
    }
    
    curvaChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Curva A', 'Curva B', 'Curva C'],
            datasets: [{
                data: [data.curvaA, data.curvaB, data.curvaC],
                backgroundColor: ['#f39c12', '#3498db', '#95a5a6'],
                borderColor: ['#e67e22', '#2980b9', '#7f8c8d'],
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#f39c12',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            return `${context.parsed.y} produtos`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255,255,255,0.1)'
                    },
                    ticks: {
                        color: '#7f8c8d'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#7f8c8d'
                    }
                }
            },
            animation: {
                duration: 800,
                easing: 'easeOutQuart'
            },
            onHover: (event, activeElements) => {
                event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
            }
        }
    });
}

function createDonutChart(curvaData) {
    const ctx = document.getElementById('donutChart').getContext('2d');
    
    if (donutChart) {
        donutChart.destroy();
    }
    
    const produtosEmAlta = curvaData
        .filter(p => p.curva === 'A')
        .slice(0, 5);
    
    donutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: produtosEmAlta.map(p => p.sku),
            datasets: [{
                data: produtosEmAlta.map(p => p.sale_price),
                backgroundColor: ['#f39c12', '#e74c3c', '#3498db', '#2ecc71', '#9b59b6'],
                borderColor: ['#e67e22', '#c0392b', '#2980b9', '#27ae60', '#8e44ad'],
                borderWidth: 2,
                hoverBorderWidth: 4,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            interaction: {
                mode: 'point'
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#f39c12',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            return `SKU: ${context[0].label}`;
                        },
                        label: function(context) {
                            return `Preço: R$ ${context.parsed.toFixed(2)}`;
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutBounce'
            },
            onHover: (event, activeElements, chart) => {
                event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
                
                // Efeito de rotação suave no hover
                if (activeElements.length > 0) {
                    chart.options.rotation += 0.5;
                    chart.update('none');
                }
            }
        }
    });
}

function createTrendChart() {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    if (trendChart) {
        trendChart.destroy();
    }
    
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            datasets: [{
                label: 'Curva A',
                data: [20, 25, 30, 28, 35, 40],
                borderColor: '#f39c12',
                backgroundColor: 'rgba(243, 156, 18, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointHoverRadius: 10,
                pointBackgroundColor: '#f39c12',
                pointBorderColor: '#fff',
                pointBorderWidth: 3,
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#f39c12'
            }, {
                label: 'Curva B/C',
                data: [15, 18, 22, 20, 25, 28],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointHoverRadius: 10,
                pointBackgroundColor: '#3498db',
                pointBorderColor: '#fff',
                pointBorderWidth: 3,
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#3498db'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: { 
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#7f8c8d',
                        font: {
                            size: 12
                        },
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#f39c12',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            return `Mês: ${context[0].label}`;
                        },
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y} vendas`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255,255,255,0.1)'
                    },
                    ticks: {
                        color: '#7f8c8d'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255,255,255,0.05)'
                    },
                    ticks: {
                        color: '#7f8c8d'
                    }
                }
            },
            animation: {
                duration: 1200,
                easing: 'easeInOutQuart'
            },
            onHover: (event, activeElements) => {
                event.native.target.style.cursor = activeElements.length > 0 ? 'crosshair' : 'default';
            }
        }
    });
}

async function checkStockAlerts() {
    try {
        const response = await fetch(API_BASE + '/curva/A');
        const curvaA = await response.json();
        
        const baixoEstoque = curvaA.filter(p => p.stock <= 5);
        
        if (baixoEstoque.length > 0) {
            alertsData = baixoEstoque;
            updateAlertsUI();
            showNotification(baixoEstoque.length + ' produtos com estoque baixo!');
        }
        
    } catch (error) {
        console.error('Erro ao verificar alertas:', error);
    }
}

function updateAlertsUI() {
    const alertCount = document.getElementById('alertCount');
    alertCount.textContent = alertsData.length;
    alertCount.style.display = alertsData.length > 0 ? 'block' : 'none';
}

function showNotification(message) {
    const toast = document.getElementById('toast');
    const messageElement = toast.querySelector('.toast-message');
    
    messageElement.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 5000);
}

function initializeCalendar() {
    const calendar = document.getElementById('calendar');
    const hoje = new Date();
    const monthName = hoje.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
    
    calendar.innerHTML = '<div class="calendar-header">' + monthName + '</div>';
}

function setupEventListeners() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function() {
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    document.querySelectorAll('.check-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            loadDashboardData();
            showNotification('Dados atualizados!');
        });
    });
}

// Auto-refresh a cada 30 segundos
setInterval(loadDashboardData, 30000);