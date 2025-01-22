document.addEventListener('DOMContentLoaded', function () {
    const measurementsList = document.getElementById('measurementsList');
    const addRowBtn = document.getElementById('addRow');
    const form = document.getElementById('measurementForm');
    const submitBtn = document.getElementById('submitBtn');

    const MAX_LARGO = 3.66;
    const MAX_ANCHO = 2.44;

    function validateMeasurement(value, max) {
        return value > 0 && value <= max;
    }

    function createMeasurementRow() {
        const row = document.createElement('div');
        row.className = 'measurement-row';
        row.innerHTML = `
            <div class="row align-items-center">
                <div class="col-md-3 mb-2 mb-md-0">
                    <div class="input-group">
                        <input type="number" step="0.01" max="${MAX_LARGO}" name="largo[]" 
                               class="form-control" placeholder="Largo (m)" required>
                        <span class="input-group-text">m</span>
                    </div>
                    <div class="error-message"></div>
                </div>
                <div class="col-md-3 mb-2 mb-md-0">
                    <div class="input-group">
                        <input type="number" step="0.01" max="${MAX_ANCHO}" name="ancho[]" 
                               class="form-control" placeholder="Ancho (m)" required>
                        <span class="input-group-text">m</span>
                    </div>
                    <div class="error-message"></div>
                </div>
                <div class="col-md-2 mb-2 mb-md-0">
                    <input type="number" min="1" name="cantidad[]" class="form-control" 
                           placeholder="Cantidad" required>
                    <div class="error-message"></div>
                </div>
                <div class="col-md-3 mb-2 mb-md-0">
                    <span class="subtotal"></span>
                </div>
                <div class="col-md-1">
                    <button type="button" class="btn btn-danger btn-sm remove-row">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>`;

        const inputs = row.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                validateInput(this);
                calculateTotals();
            });
        });

        row.querySelector('.remove-row').addEventListener('click', function() {
            row.remove();
            calculateTotals();
            if (document.querySelectorAll('.measurement-row').length === 0) {
                createMeasurementRow();
            }
        });

        measurementsList.appendChild(row);
        calculateTotals();
    }

    function validateInput(input) {
        const errorDiv = input.parentElement.nextElementSibling;
        input.classList.remove('validation-error');
        errorDiv.textContent = '';

        if (input.name.includes('largo') && !validateMeasurement(input.value, MAX_LARGO)) {
            input.classList.add('validation-error');
            errorDiv.textContent = `Máximo permitido: ${MAX_LARGO}m`;
            return false;
        }
        if (input.name.includes('ancho') && !validateMeasurement(input.value, MAX_ANCHO)) {
            input.classList.add('validation-error');
            errorDiv.textContent = `Máximo permitido: ${MAX_ANCHO}m`;
            return false;
        }
        if (input.name.includes('cantidad') && input.value < 1) {
            input.classList.add('validation-error');
            errorDiv.textContent = 'Mínimo: 1';
            return false;
        }
        return true;
    }

    function calculateTotals() {
        let total = 0;
        document.querySelectorAll('.measurement-row').forEach(row => {
            const largo = parseFloat(row.querySelector('[name="largo[]"]').value) || 0;
            const ancho = parseFloat(row.querySelector('[name="ancho[]"]').value) || 0;
            const cantidad = parseInt(row.querySelector('[name="cantidad[]"]').value) || 0;

            const subtotal = largo * ancho * cantidad;
            total += subtotal;

            row.querySelector('.subtotal').textContent = 
                subtotal > 0 ? `${subtotal.toFixed(2)} m²` : '';
        });

        document.getElementById('totalMeters').textContent = 
            `Total: ${total.toFixed(2)} m²`;
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        submitBtn.disabled = true;

        try {
            const measurements = [];
            let isValid = true;

            document.querySelectorAll('.measurement-row').forEach(row => {
                const inputs = row.querySelectorAll('input');
                inputs.forEach(input => {
                    if (!validateInput(input)) {
                        isValid = false;
                    }
                });

                if (isValid) {
                    measurements.push({
                        largo: parseFloat(row.querySelector('[name="largo[]"]').value),
                        ancho: parseFloat(row.querySelector('[name="ancho[]"]').value),
                        cantidad: parseInt(row.querySelector('[name="cantidad[]"]').value)
                    });
                }
            });

            if (!isValid) {
                throw new Error('Por favor, corrija los errores en las medidas');
            }

            const response = await fetch(`/orders/${orderId}/measurements/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ measurements })
            });

            const data = await response.json();
            if (data.success) {
                window.location.href = `${orderDetailUrl}`;
            } else {
                throw new Error(data.error || 'Error al guardar las medidas');
            }
        } catch (error) {
            alert(error.message || 'Error al procesar la solicitud');
        } finally {
            submitBtn.disabled = false;
        }
    });

    addRowBtn.addEventListener('click', createMeasurementRow);
    createMeasurementRow();
});