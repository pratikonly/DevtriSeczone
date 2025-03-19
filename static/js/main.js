document.addEventListener('DOMContentLoaded', function() {
    // Visitor tracking and statistics
    class VisitorTracker {
        constructor() {
            this.visitors = JSON.parse(localStorage.getItem('visitors') || '[]');
            this.initializeVisitor();
        }

        async initializeVisitor() {
            try {
                // Get visitor's IP and location data
                const response = await fetch('https://api.ipapi.com/api/check?access_key=YOUR_IPAPI_KEY');
                const data = await response.json();

                const visitor = {
                    ip: data.ip,
                    country: data.country_name,
                    region: data.region_name,
                    city: data.city,
                    visit_time: new Date().toISOString()
                };

                this.visitors.push(visitor);
                localStorage.setItem('visitors', JSON.stringify(this.visitors));
                this.updateVisitorCount();
                this.updateVisitorStats();
            } catch (error) {
                console.error('Error tracking visitor:', error);
            }
        }

        updateVisitorCount() {
            const counterElement = document.querySelector('.visitor-counter span');
            if (counterElement) {
                counterElement.textContent = `${this.visitors.length} Visitors`;
            }
        }

        updateVisitorStats() {
            const statsTable = document.querySelector('#visitorStatsModal .table tbody');
            if (statsTable) {
                statsTable.innerHTML = this.visitors.map(visitor => `
                    <tr>
                        <td>${visitor.ip}</td>
                        <td>${visitor.country}</td>
                        <td>${visitor.region}</td>
                        <td>${visitor.city}</td>
                        <td>${new Date(visitor.visit_time).toLocaleString()}</td>
                    </tr>
                `).join('');
            }
        }
    }

    // Contact form handling
    class ContactForm {
        constructor() {
            this.form = document.getElementById('contactForm');
            this.submissions = JSON.parse(localStorage.getItem('contactSubmissions') || '[]');
            this.initializeForm();
        }

        initializeForm() {
            if (this.form) {
                this.form.addEventListener('submit', (e) => this.handleSubmit(e));
            }
        }

        async handleSubmit(e) {
            e.preventDefault();

            const formData = {
                name: this.form.querySelector('#name').value,
                email: this.form.querySelector('#email').value,
                message: this.form.querySelector('#message').value,
                timestamp: new Date().toISOString()
            };

            if (this.validateForm(formData)) {
                this.submissions.push(formData);
                localStorage.setItem('contactSubmissions', JSON.stringify(this.submissions));
                this.showNotification('Message sent successfully!', 'success');
                this.form.reset();
            }
        }

        validateForm(data) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!data.name.trim()) {
                this.showNotification('Please enter your name', 'error');
                return false;
            }
            if (!emailRegex.test(data.email)) {
                this.showNotification('Please enter a valid email', 'error');
                return false;
            }
            if (!data.message.trim()) {
                this.showNotification('Please enter a message', 'error');
                return false;
            }
            return true;
        }

        showNotification(message, type) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.querySelector('.container').insertBefore(alertDiv, this.form);
            setTimeout(() => alertDiv.remove(), 5000);
        }
    }

    // Flash News system
    class FlashNews {
        constructor() {
            this.news = [
                "Devtri Seczone is now offering Skilled Office Staff across ghaziabad region",
                "New job openings available",
                "Expanding our services to new regions"
            ];
            this.currentIndex = 0;
            this.initializeFlashNews();
        }

        initializeFlashNews() {
            const flashText = document.querySelector('.flash-text');
            if (flashText) {
                setInterval(() => {
                    this.currentIndex = (this.currentIndex + 1) % this.news.length;
                    flashText.textContent = this.news[this.currentIndex];
                }, 5000);
            }
        }
    }

    // Initialize all frontend features
    const visitorTracker = new VisitorTracker();
    const contactForm = new ContactForm();
    const flashNews = new FlashNews();

    // Navbar toggle behavior
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
                navbarCollapse.classList.remove('show');
            }
        });

        // Close menu when clicking a nav link
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
            link.addEventListener('click', function() {
                navbarCollapse.classList.remove('show');
            });
        });
    }

    // Navbar scroll behavior
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

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

    // Lazy loading images
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => {
            // Store original src in data-src
            if (!img.dataset.src) {
                img.dataset.src = img.src;
                img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'; // Transparent placeholder
            }
            imageObserver.observe(img);
        });
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

    // Form validation (original code, kept for completeness)
    const contactFormOriginal = document.getElementById('contactForm');
    if (contactFormOriginal) {
        contactFormOriginal.addEventListener('submit', function(e) {
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

    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});