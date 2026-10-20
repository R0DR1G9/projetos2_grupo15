const dados = JSON.parse(document.getElementById('dados-grafico').textContent);
const ultimo = dados.rotulos.length - 1;
let grafico;

const explicacoes = {
    linha: 'Cada ponto é um diagnóstico. Se a linha sobe, sua nota geral está melhorando.',
    barras: 'Compara as três dimensões em cada diagnóstico. Barras mais altas significam notas melhores.',
    radar: 'Compara o diagnóstico anterior com o mais recente. Quanto maior a área colorida, melhor a nota.'
};

const eixoPercentual = { min: 0, max: 100, ticks: { callback: v => v + '%' } };

const tooltipDiagnostico = {
    callbacks: {
        title: itens => {
            const i = itens[0].dataIndex;
            return `${dados.rotulos[i]} — ${dados.empresas[i]} (${dados.datas[i]})`;
        },
        label: item => ` ${item.dataset.label}: ${item.parsed.y}%`
    }
};

function config(tipo) {
    if (tipo === 'linha') {
        return { type: 'line',
            data: { labels: dados.rotulos, datasets: [{
                label: 'Nota geral', data: dados.geral,
                borderColor: '#3d5a2c', backgroundColor: 'rgba(61,90,44,0.15)',
                fill: true, tension: 0.3, pointRadius: 7, pointHoverRadius: 9 }] },
            options: { maintainAspectRatio: false,
                scales: { y: eixoPercentual },
                plugins: { legend: { display: false }, tooltip: tooltipDiagnostico } } };
    }
    if (tipo === 'barras') {
        return { type: 'bar',
            data: { labels: dados.rotulos, datasets: [
                { label: 'Ambiental', data: dados.ambiental, backgroundColor: '#3d5a2c' },
                { label: 'Social', data: dados.social, backgroundColor: '#b4532f' },
                { label: 'Governança', data: dados.governanca, backgroundColor: '#c78a45' }] },
            options: { maintainAspectRatio: false,
                scales: { y: eixoPercentual },
                plugins: { legend: { position: 'bottom' }, tooltip: tooltipDiagnostico } } };
    }
    const ant = ultimo - 1;
    return { type: 'radar',
        data: { labels: ['Ambiental', 'Social', 'Governança'], datasets: [
            { label: dados.rotulos[ant] + ' (anterior)',
              data: [dados.ambiental[ant], dados.social[ant], dados.governanca[ant]],
              borderColor: '#6c757d', backgroundColor: 'rgba(108,117,125,0.15)' },
            { label: dados.rotulos[ultimo] + ' (atual)',
              data: [dados.ambiental[ultimo], dados.social[ultimo], dados.governanca[ultimo]],
              borderColor: '#3d5a2c', backgroundColor: 'rgba(61,90,44,0.25)' }] },
        options: { maintainAspectRatio: false,
            scales: { r: { min: 0, max: 100, ticks: { stepSize: 25, callback: v => v + '%' } } },
            plugins: { legend: { position: 'bottom' } } } };
}

function desenhar(tipo) {
    if (grafico) grafico.destroy();
    grafico = new Chart(document.getElementById('grafico'), config(tipo));
    document.getElementById('explicacao').textContent = explicacoes[tipo];
}

document.querySelectorAll('[data-tipo]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('[data-tipo]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        desenhar(btn.dataset.tipo);
    });
});
desenhar('linha');
