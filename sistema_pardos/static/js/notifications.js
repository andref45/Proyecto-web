class NotificationManager {
    constructor() {
        this.container = document.getElementById('notification-container');
        this.checkInterval = 30000; // 30 segundos
        this.init();
    }

    init() {
        this.checkNotifications();
        setInterval(() => this.checkNotifications(), this.checkInterval);
    }

    async checkNotifications() {
        try {
            const response = await fetch('/get-notifications/');
            const data = await response.json();
            this.updateNotifications(data.notifications);
        } catch (error) {
            console.error('Error checking notifications:', error);
        }
    }

    updateNotifications(notifications) {
        if (!this.container) return;
        
        if (notifications.length > 0) {
            this.container.innerHTML = notifications.map(n => this.createNotificationHTML(n)).join('');
            this.addEventListeners();
        } else {
            this.container.innerHTML = '<p class="text-muted m-0">No hay notificaciones nuevas</p>';
        }
    }

    createNotificationHTML(notification) {
        return `
            <div class="notification-item p-3 border-bottom" data-id="${notification.id}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <p class="mb-1">${notification.message}</p>
                        <small class="text-muted">${notification.created_at}</small>
                    </div>
                    <button class="btn btn-sm btn-link mark-read">
                        <i class="bi bi-check2"></i>
                    </button>
                </div>
            </div>
        `;
    }

    addEventListeners() {
        this.container.querySelectorAll('.mark-read').forEach(button => {
            button.addEventListener('click', (e) => {
                const item = e.target.closest('.notification-item');
                if (item) {
                    this.markAsRead(item.dataset.id);
                }
            });
        });
    }

    async markAsRead(notificationId) {
        try {
            await fetch(`/mark-notification-read/${notificationId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });
            this.checkNotifications();
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new NotificationManager();
});