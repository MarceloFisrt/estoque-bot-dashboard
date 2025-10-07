let curvaChart, margemChart, lucroChart;

async function carregarDashboard(filtroCurva = "todas", filtroProduto = "") {
  try {
    const url = new URL("http://127.0.0.1:8000/dashboard/dados");
    url.searchParams.append("curva", filtroCurva);
    url.searchParams.append("produto", filtroProduto);

    const response = await fetch(url);
    const data = await response.json();

    // Atualiza informações nos cards
    document.getElementById("atualizacao").textContent = "Atualizado em " + data.atualizacao;
    document.getElementById("total_produtos").textContent = data.total_produtos;
    document.getElementById("lucro_total").textContent = "R$ " + data.lucro_total.toFixed(2);
    document.getElementById("total_estoque").textContent = data.curvaA + data.curvaB + data.curvaC;

    atualizarGraficos(data);

  } catch (error) {
    console.error("Erro ao carregar dashboard:", error);
  }
}

function atualizarGraficos(data) {
  // 🔁 Apaga gráficos antigos antes de recriar
  if (curvaChart) curvaChart.destroy();
  if (margemChart) margemChart.destroy();
  if (lucroChart) lucroChart.destroy();

  // Curva ABC
  const ctxCurva = document.getElementById("curvaChart").getContext("2d");
  curvaChart = new Chart(ctxCurva, {
    type: "doughnut",
    data: {
      labels: ["Curva A", "Curva B", "Curva C"],
      datasets: [{
        data: [data.curvaA, data.curvaB, data.curvaC],
        backgroundColor: ["#00b894", "#fdcb6e", "#d63031"]
      }]
    },
    options: { plugins: { legend: { position: "bottom" } } }
  });

  // Margem %
  const ctxMargem = document.getElementById("margemChart").getContext("2d");
  margemChart = new Chart(ctxMargem, {
    type: "line",
    data: {
      labels: data.produtos_top,
      datasets: [{
        label: "Margem %",
        data: data.lucros_top.map(v => (v / 100) || 0),
        borderColor: "#0984e3",
        fill: false,
        tension: 0.3
      }]
    },
    options: { scales: { y: { beginAtZero: true } } }
  });

  // Lucro R$
  const ctxLucro = document.getElementById("lucroChart").getContext("2d");
  lucroChart = new Chart(ctxLucro, {
    type: "bar",
    data: {
      labels: data.produtos_top,
      datasets: [{
        label: "Lucro (R$)",
        data: data.lucros_top,
        backgroundColor: "#74b9ff"
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  });
}

// 🧭 Eventos dos filtros
document.getElementById("btnFiltrar").addEventListener("click", () => {
  const curva = document.getElementById("filtroCurva").value;
  const produto = document.getElementById("filtroProduto").value;
  carregarDashboard(curva, produto);
});

// Carrega inicialmente
carregarDashboard();
