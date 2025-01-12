document.addEventListener('DOMContentLoaded', function() {
    // Función principal para actualizar el dashboard
    function updateDashboard() {
        fetch('/inventory/dashboard-data/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Actualizar contadores
            document.getElementById('total-products').textContent = data.total_products;
            document.getElementById('total-value').textContent = data.total_value.toFixed(2);
            
            // Actualizar tablas
            updateTableContent('stale-products-table', data.stale_products);
            updateTableContent('low-stock-table', data.low_stock_products);
            updateTableContent('color-stats-container', data.color_stats);
        })
        .catch(error => console.error('Error actualizando dashboard:', error));
    }

    // Función para actualizar el contenido de las tablas
    function updateTableContent(tableId, data) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const tbody = table.querySelector('tbody');
        if (!tbody) return;

        tbody.innerHTML = data.length ? 
            data.map(createTableRow).join('') : 
            '<tr><td colspan="4" class="text-center py-3">No hay datos disponibles</td></tr>';
    }

    // Función para crear filas de tabla
    function createTableRow(item) {
        return `
            <tr>
                <td>${item.name || item.color__name}</td>
                <td>${item.stock || item.total_stock}</td>
                <td>${item.days_without_movement || item.avg_days}</td>
                <td>
                    ${item.id ? `
                        <a href="/boards/${item.id}/edit" class="btn btn-sm btn-warning">
                            <i class="bi bi-pencil"></i>
                        </a>
                    ` : ''}
                </td>
            </tr>
        `;
    }

    // Configurar actualización automática
    setInterval(updateDashboard, 60000);  // Cada minuto

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
});