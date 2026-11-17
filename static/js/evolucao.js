const dados = JSON.parse(document.getElementById('dados-grafico').textContent);
let grafico;

const VINHO = '#673a40';
const PILARES = [
    { chave: 'ambiental', nome: 'Ambiental', cor: '#3e462f' },
    { chave: 'social', nome: 'Social', cor: '#7d2028' },
    { chave: 'governanca', nome: 'Governança', cor: '#5fa8c2' }
];

const explicacoes = {
    linha: 'Cada ponto é um diagnóstico. Se a linha sobe, sua nota geral está melhorando.',
    pilares: 'Acompanhe Ambiental, Social e Governança lado a lado. Linhas mais altas significam notas melhores.'
};

Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
Chart.defaults.font.size = 13;
Chart.defaults.color = '#7a6467';

const eixoY = {
    min: 0,
    max: 100,
    ticks: { stepSize: 25, padding: 10, callback: v => v + '%' },
    grid: { color: 'rgba(103, 58, 64, 0.1)', drawTicks: false },
    border: { display: false }
};

const eixoX = {
    grid: { display: false },
    border: { color: 'rgba(103, 58, 64, 0.25)' },
    ticks: { padding: 10 }
};

const tooltip = {
    backgroundColor: '#4a2a30',
    titleColor: '#fae4b2',
    bodyColor: '#ffffff',
    padding: 14,
    cornerRadius: 10,
    boxPadding: 6,
    usePointStyle: true,
    callbacks: {
        title: itens => {
            const i = itens[0].dataIndex;
            return `${dados.rotulos[i]} - ${dados.empresas[i]}`;
        },
        afterTitle: itens => dados.datas[itens[0].dataIndex],
        label: item => ` ${item.dataset.label}: ${item.parsed.y.toLocaleString('pt-BR')}%`
    }
};

function degrade(contexto) {
    const area = contexto.chart.chartArea;
    if (!area) return 'rgba(103, 58, 64, 0.12)';
    const g = contexto.chart.ctx.createLinearGradient(0, area.top, 0, area.bottom);
    g.addColorStop(0, 'rgba(103, 58, 64, 0.3)');
    g.addColorStop(1, 'rgba(103, 58, 64, 0)');
    return g;
}

const valoresNosPontos = {
    id: 'valoresNosPontos',
    afterDatasetsDraw(chart) {
        if (dados.rotulos.length > 12) return;
        const ctx = chart.ctx;
        ctx.save();
        ctx.font = "700 14px 'Inter', sans-serif";
        ctx.fillStyle = VINHO;
        ctx.textAlign = 'center';
        chart.getDatasetMeta(0).data.forEach((ponto, i) => {
            ctx.fillText(dados.geral[i].toLocaleString('pt-BR') + '%', ponto.x, ponto.y - 18);
        });
        ctx.restore();
    }
};

function config(tipo) {
    const base = { maintainAspectRatio: false, interaction: { mode: 'index', intersect: false }, layout: { padding: { top: 12, right: 8 } } };
    if (tipo === 'linha') {
        const ultimo = dados.rotulos.length - 1;
        return { type: 'line', plugins: [valoresNosPontos],
            data: { labels: dados.rotulos, datasets: [{
                label: 'Nota geral', data: dados.geral,
                borderColor: VINHO, borderWidth: 3, backgroundColor: degrade,
                fill: true, tension: 0.35,
                pointBackgroundColor: '#ffffff', pointBorderColor: VINHO, pointBorderWidth: 3,
                pointRadius: dados.geral.map((_, i) => i === ultimo ? 8 : 6), pointHoverRadius: 9 }] },
            options: { ...base,
                scales: { y: eixoY, x: eixoX },
                plugins: { legend: { display: false }, tooltip } } };
    }
    return { type: 'line',
        data: { labels: dados.rotulos, datasets: PILARES.map(p => ({
            label: p.nome, data: dados[p.chave],
            borderColor: p.cor, backgroundColor: p.cor, borderWidth: 3, tension: 0.35,
            pointBackgroundColor: '#ffffff', pointBorderColor: p.cor, pointBorderWidth: 3,
            pointRadius: 5, pointHoverRadius: 8 })) },
        options: { ...base,
            scales: { y: eixoY, x: eixoX },
            plugins: { legend: { position: 'top', align: 'end', labels: { usePointStyle: true, pointStyle: 'circle', boxWidth: 8, boxHeight: 8, padding: 18 } }, tooltip } } };
}

function desenhar(tipo) {
    if (grafico) grafico.destroy();
    grafico = new Chart(document.getElementById('grafico'), config(tipo));
    document.getElementById('explicacao').textContent = explicacoes[tipo];
}

document.querySelectorAll('[data-tipo]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('[data-tipo]').forEach(b => {
            b.classList.remove('active');
            b.setAttribute('aria-pressed', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
        desenhar(btn.dataset.tipo);
    });
});
desenhar('linha');
