// static/js/dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('ordersChart');
    if (!ctx) return;

    // Obtener los datos del elemento canvas
    const chartData = {
        labels: JSON.parse(ctx.getAttribute('data-labels')),
        orders: JSON.parse(ctx.getAttribute('data-orders')),
        meters: JSON.parse(ctx.getAttribute('data-meters'))
    };

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Pedidos',
                data: chartData.orders,
                borderColor: '#4b6cb7',
                backgroundColor: 'rgba(75, 108, 183, 0.1)',
                tension: 0.4,
                fill: true,
                yAxisID: 'y'
            }, {
                label: 'Metros²',
                data: chartData.meters,
                borderColor: '#182848',
                backgroundColor: 'rgba(24, 40, 72, 0.1)',
                tension: 0.4,
                fill: true,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Número de Pedidos'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Metros Cuadrados'
                    }
                }
            }
        }
    });
});