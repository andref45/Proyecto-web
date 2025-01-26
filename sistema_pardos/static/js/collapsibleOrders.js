class CollapsibleOrders {
    constructor() {
        this.init();
    }

    init() {
        // Seleccionar todos los elementos colapsables
        document.querySelectorAll('[data-collapse-toggle]').forEach(trigger => {
            // Obtener el objetivo del colapso
            const targetId = trigger.getAttribute('data-collapse-toggle');
            const target = document.getElementById(targetId);
            
            if (target) {
                // Configurar estado inicial
                const icon = trigger.querySelector('.bi-chevron-down');
                let isExpanded = false;

                // Agregar el listener para el clic
                trigger.addEventListener('click', (e) => {
                    e.preventDefault();
                    isExpanded = !isExpanded;
                    
                    // Actualizar atributos ARIA
                    trigger.setAttribute('aria-expanded', isExpanded);
                    
                    // Animar el icono
                    if (icon) {
                        icon.style.transform = isExpanded ? 'rotate(0)' : 'rotate(-90deg)';
                    }
                    
                    // Animar el contenido
                    if (isExpanded) {
                        target.style.maxHeight = target.scrollHeight + 'px';
                        target.classList.add('show');
                    } else {
                        target.style.maxHeight = '0px';
                        target.classList.remove('show');
                    }
                });

                // Configurar altura inicial
                target.style.maxHeight = '0px';
            }
        });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new CollapsibleOrders();
});