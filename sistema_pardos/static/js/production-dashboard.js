document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('production-form');
    const refreshButton = document.getElementById('refresh-dashboard');

    // Manejar envío del formulario
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            try {
                const response = await fetch('/production/add/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });

                if (response.ok) {
                    location.reload();
                } else {
                    alert('Error al guardar el registro');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al procesar la solicitud');
            }
        });
    }

    // Actualizar dashboard
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            location.reload();
        });
    }
});