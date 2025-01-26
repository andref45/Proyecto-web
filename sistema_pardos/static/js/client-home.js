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
        // Manejo de las listas desplegables
        const collapseElements = document.querySelectorAll('[data-bs-toggle="collapse"]');
        collapseElements.forEach(element => {
            const targetId = element.getAttribute('data-bs-target');
            const icon = element.querySelector('.collapse-icon');
            
            if (targetId && icon) {
                const collapse = document.querySelector(targetId);
                
                if (collapse) {
                    collapse.addEventListener('show.bs.collapse', () => {
                        icon.style.transform = 'rotate(0deg)';
                    });
                    
                    collapse.addEventListener('hide.bs.collapse', () => {
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