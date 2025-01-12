document.addEventListener('DOMContentLoaded', function() {
    // Referencia al gráfico
    const chartCtx = document.getElementById('ordersChart').getContext('2d');
    let ordersChart;

    // Inicializar gráfico
    function initChart(data) {
        ordersChart = new Chart(chartCtx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Pedidos',
                        data: data.orders,
                        borderColor: '#4b6cb7',
                        fill: false
                    },
                    {
                        label: 'Metros²',
                        data: data.meters,
                        borderColor: '#182848',
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Función principal para actualizar el dashboard
    function updateDashboard() {
        fetch('/inventory/dashboard-data/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Actualizar contadores principales
            document.getElementById('pedidos-hoy').textContent = data.pedidos_hoy || '0';
            document.getElementById('completados').textContent = data.completados || '0';
            document.getElementById('en-proceso').textContent = data.en_proceso || '0';
            document.getElementById('metros-mes').textContent = (data.metros_mes || '0') + 'm²';

            // Actualizar gráfico
            if (ordersChart) {
                ordersChart.data.labels = data.chart_data.labels;
                ordersChart.data.datasets[0].data = data.chart_data.orders;
                ordersChart.data.datasets[1].data = data.chart_data.meters;
                ordersChart.update();
            } else {
                initChart(data.chart_data);
            }

            // Actualizar estadísticas
            document.getElementById('total-productos').textContent = data.total_productos + ' items';
            document.getElementById('productos-faltantes').textContent = data.productos_faltantes + ' items';
            document.getElementById('valor-total').textContent = '$' + data.valor_total.toFixed(2);

            // Actualizar tabla de pedidos recientes
            updateTableContent('pedidos-recientes', data.pedidos_recientes);
        })
        .catch(error => console.error('Error actualizando dashboard:', error));
    }

    // Función para actualizar tabla de pedidos
    function updateTableContent(tableId, data) {
        const tbody = document.querySelector(`#${tableId} tbody`);
        if (!tbody) return;

        tbody.innerHTML = data.map(pedido => `
            <tr>
                <td>#${pedido.id}</td>
                <td>${pedido.cliente}</td>
                <td>${pedido.tipo}</td>
                <td><span class="badge bg-${pedido.estado_color}">${pedido.estado}</span></td>
                <td>${pedido.fecha}</td>
                <td>${pedido.total_m2 || '--'}</td>
                <td>
                    <a href="/orders/${pedido.id}" class="btn btn-sm btn-info">
                        <i class="bi bi-eye"></i>
                    </a>
                </td>
            </tr>
        `).join('');
    }

    // Configurar actualización automática
    setInterval(updateDashboard, 60000); // Cada minuto

    // Configurar botón de actualización manual
    const refreshButton = document.getElementById('refresh-dashboard');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            const icon = this.querySelector('i');
            icon.classList.add('bi-arrow-clockwise-spin');
            
            updateDashboard().finally(() => {
                setTimeout(() => {
                    icon.classList.remove('bi-arrow-clockwise-spin');
                }, 1000);
            });
        });
    }

    // Inicializar dashboard
    updateDashboard();
});