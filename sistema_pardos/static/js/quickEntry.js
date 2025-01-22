function quickEntry(boardId) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const modalHtml = `
        <div class="modal fade" id="quickEntryModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Agregar Stock</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="quickEntryForm" method="post">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                            <div class="mb-3">
                                <label class="form-label">Cantidad a agregar</label>
                                <input type="number" name="quantity" class="form-control" required min="1">
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                                <button type="submit" class="btn btn-primary">Guardar</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;

    const existingModal = document.getElementById('quickEntryModal');
    if (existingModal) {
        existingModal.remove();
    }

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    const modal = new bootstrap.Modal(document.getElementById('quickEntryModal'));
    const form = document.getElementById('quickEntryForm');

    form.onsubmit = async function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        try {
            const response = await fetch(`/boards/${boardId}/quick-entry/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            const data = await response.json();
            
            if (data.success) {
                modal.hide();
                alert(data.message);
                location.reload();
            } else {
                alert(data.error || 'Error al actualizar el stock');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al procesar la solicitud');
        }
    };

    modal.show();
}

document.addEventListener('hide.bs.modal', function (event) {
    if (event.target.id === 'quickEntryModal') {
        document.getElementById('quickEntryForm').reset();
    }
});

function confirmDelete(boardId) {
    if (confirm('¿Estás seguro de que deseas eliminar este tablero?')) {
        window.location.href = `/boards/${boardId}/delete/`;
    }
}