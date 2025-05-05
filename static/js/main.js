// Main JavaScript for CyberShield IDS

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    if (flashMessages.length > 0) {
        setTimeout(function() {
            flashMessages.forEach(function(message) {
                const closeBtn = message.querySelector('.btn-close');
                if (closeBtn) {
                    closeBtn.click();
                }
            });
        }, 5000);
    }

    // Add active class to current nav item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(function(link) {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        }
    });

    // Initialize any dropdowns
    const dropdownToggleList = document.querySelectorAll('.dropdown-toggle');
    if (dropdownToggleList.length > 0) {
        const dropdownList = [...dropdownToggleList].map(dropdownToggleEl => {
            return new bootstrap.Dropdown(dropdownToggleEl);
        });
    }

    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length > 0) {
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    // Animate elements on scroll
    function animateOnScroll() {
        const animateItems = document.querySelectorAll('.animate-on-scroll');
        
        animateItems.forEach(function(item) {
            const itemPosition = item.getBoundingClientRect().top;
            const screenPosition = window.innerHeight;
            
            if (itemPosition < screenPosition * 0.8) {
                item.classList.add('animated');
            }
        });
    }

    // Add animate-on-scroll class to feature cards, workflow items, and CTA
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(function(card) {
        card.classList.add('animate-on-scroll');
    });

    const workflowItems = document.querySelectorAll('.workflow-item');
    workflowItems.forEach(function(item) {
        item.classList.add('animate-on-scroll');
    });

    const ctaSection = document.querySelector('.cta-section');
    if (ctaSection) {
        ctaSection.classList.add('animate-on-scroll');
    }

    // Listen for scroll events
    window.addEventListener('scroll', animateOnScroll);
    
    // Trigger once on load
    animateOnScroll();

    // Shield animation for landing page
    const shieldContainer = document.querySelector('.cyber-shield-animation');
    if (shieldContainer) {
        const createParticle = () => {
            const particle = document.createElement('div');
            particle.className = 'data-particle';
            particle.style.position = 'absolute';
            particle.style.width = '5px';
            particle.style.height = '5px';
            particle.style.backgroundColor = 'rgba(255, 255, 255, 0.7)';
            particle.style.borderRadius = '50%';
            
            // Random position around the shield
            const angle = Math.random() * Math.PI * 2;
            const distance = 100 + Math.random() * 50;
            const x = Math.cos(angle) * distance;
            const y = Math.sin(angle) * distance;
            
            particle.style.left = '50%';
            particle.style.top = '50%';
            particle.style.transform = `translate(${x}px, ${y}px)`;
            
            // Animation properties
            particle.style.animation = `particle ${1 + Math.random() * 2}s linear forwards`;
            
            shieldContainer.appendChild(particle);
            
            // Remove particle after animation completes
            setTimeout(() => {
                shieldContainer.removeChild(particle);
            }, 3000);
        };
        
        // Create particles periodically
        setInterval(createParticle, 200);
    }
});