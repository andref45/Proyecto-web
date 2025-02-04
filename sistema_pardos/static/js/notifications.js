function updateNotifications() {
    fetch('/get-notifications/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('notification-container');
            const badge = document.getElementById('notification-badge');
            if (data.notifications.length > 0) {
                badge.style.display = 'block';
                badge.textContent = data.notifications.length;
                container.innerHTML = data.notifications.map(notification => `
                    <div class="dropdown-item border-bottom py-2">
                        <div class="d-flex justify-content-between">
                            <small class="text-muted">${notification.created_at}</small>
                            <button onclick="markAsRead(${notification.id})" class="btn btn-sm btn-link p-0">
                                <i class="bi bi-check2"></i>
                            </button>
                        </div>
                        <div>${notification.message}</div>
                    </div>
                `).join('');
            } else {
                badge.style.display = 'none';
                container.innerHTML = '<div class="p-3 text-center text-muted">No hay notificaciones</div>';
            }
        })
        .catch(error => console.error('Error:', error));
}

function markAsRead(notificationId) {
    fetch(`/mark-notification-read/${notificationId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotifications();
            }
        })
        .catch(error => console.error('Error:', error));
}

function clearAllNotifications() {
    fetch('/clear-notifications/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotifications();
            }
        })
        .catch(error => console.error('Error:', error));
}

// Actualizar notificaciones cada 30 segundos
document.addEventListener('DOMContentLoaded', function() {
    updateNotifications();
    setInterval(updateNotifications, 30000);
});