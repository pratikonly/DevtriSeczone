document.addEventListener('DOMContentLoaded', function() {
    // Slideshow functionality
    let slideIndex = 0;
    const slides = document.querySelectorAll('.slide');

    function showSlides() {
        for (let i = 0; i < slides.length; i++) {
            slides[i].classList.remove('active');
        }
        slideIndex++;
        if (slideIndex > slides.length) {
            slideIndex = 1;
        }
        slides[slideIndex - 1].classList.add('active');
        setTimeout(showSlides, 3000); // Change slide every 3 seconds
    }

    if (slides.length > 0) {
        slides[0].classList.add('active');
        setTimeout(showSlides, 3000);
    }

    // Contact toggle functionality
    const contactToggle = document.querySelector('.contact-toggle');
    const contactOptions = document.querySelector('.contact-options');

    if (contactToggle) {
        contactToggle.addEventListener('mouseenter', function() {
            contactOptions.classList.add('show');
        });

        contactToggle.addEventListener('mouseleave', function() {
            contactOptions.classList.remove('show');
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 75,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Form validation
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const message = document.getElementById('message').value.trim();

            if (!name || !email || !message) {
                e.preventDefault();
                alert('Please fill in all fields');
                return false;
            }

            if (!isValidEmail(email)) {
                e.preventDefault();
                alert('Please enter a valid email address');
                return false;
            }
        });
    }

    // Email validation helper
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // Navbar background change on scroll
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('bg-white');
            navbar.classList.add('shadow');
        } else {
            navbar.classList.remove('shadow');
        }
    });

    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});