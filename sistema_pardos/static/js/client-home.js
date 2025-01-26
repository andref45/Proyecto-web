class ClientHome {
    constructor() {
        this.initializeEventListeners();
        this.initializeCollapsibles();
        this.initializeAnimations();
    }

    initializeEventListeners() {
        // Smooth scroll para enlaces internos
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => this.handleSmoothScroll(e, anchor));
        });

        // Manejo del botón flotante
        const fab = document.querySelector('.floating-action');
        if (fab) {
            window.addEventListener('scroll', () => this.handleFloatingButton(fab));
        }
    }

    initializeCollapsibles() {
        const collapseElements = document.querySelectorAll('[data-bs-toggle="collapse"]');
        
        collapseElements.forEach(element => {
            const targetId = element.getAttribute('data-bs-target');
            const icon = element.querySelector('.bi-chevron-down');
            
            if (targetId && icon) {
                const collapseContent = document.querySelector(targetId);
                
                if (collapseContent) {
                    // Crear la instancia de collapse
                    const bsCollapse = new bootstrap.Collapse(collapseContent, {
                        toggle: false
                    });
    
                    // Manejar el click manualmente
                    element.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        const isCollapsed = !collapseContent.classList.contains('show');
                        
                        if (isCollapsed) {
                            bsCollapse.show();
                            icon.style.transform = 'rotate(0deg)';
                        } else {
                            bsCollapse.hide();
                            icon.style.transform = 'rotate(-90deg)';
                        }
                    });
    
                    // Manejar eventos de collapse
                    collapseContent.addEventListener('shown.bs.collapse', () => {
                        icon.style.transform = 'rotate(0deg)';
                    });
    
                    collapseContent.addEventListener('hidden.bs.collapse', () => {
                        icon.style.transform = 'rotate(-90deg)';
                    });
                }
            }
        });
    }

    initializeAnimations() {
        // Configuración del observador de intersección
        const observerOptions = {
            threshold: 0.2,
            rootMargin: '0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate__animated');
                    entry.target.classList.add(entry.target.dataset.animation);
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observar elementos con animaciones
        document.querySelectorAll('[data-animation]').forEach(element => {
            observer.observe(element);
        });
    }

    handleSmoothScroll(e, anchor) {
        e.preventDefault();
        const targetId = anchor.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    handleFloatingButton(fab) {
        const scrollPosition = window.scrollY;
        const triggerPosition = window.innerHeight * 0.5;
        
        if (scrollPosition > triggerPosition) {
            fab.classList.add('show');
        } else {
            fab.classList.remove('show');
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new ClientHome();
});