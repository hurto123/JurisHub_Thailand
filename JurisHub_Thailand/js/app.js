document.addEventListener('DOMContentLoaded', () => {

    // --- Mobile Menu Toggle ---
    const mobileBtn = document.getElementById('mobile-menu-btn');
    const closeMenuBtn = document.getElementById('close-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileBtn && mobileMenu && closeMenuBtn) {
        mobileBtn.addEventListener('click', () => {
            mobileMenu.classList.remove('translate-x-full');
        });
        
        closeMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.add('translate-x-full');
        });
    }

    // --- Stats Counter Animation ---
    const counters = document.querySelectorAll('.stat-counter');
    const speed = 200; // lower is faster

    const animateCounters = () => {
        counters.forEach(counter => {
            const updateCount = () => {
                const target = +counter.getAttribute('data-target');
                const count = +counter.innerText;
                
                const inc = target / speed;
                
                if (count < target) {
                    counter.innerText = Math.ceil(count + inc);
                    setTimeout(updateCount, 15);
                } else {
                    counter.innerText = target.toLocaleString();
                    if(target > 3000) counter.innerText += '+'; // Add plus for large numbers
                }
            };
            updateCount();
        });
    };

    // Use Intersection Observer to trigger counter when in view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounters();
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    const statsSection = document.querySelector('.grid-cols-3');
    if (statsSection) {
        observer.observe(statsSection);
    }

    // --- Search Logic ---
    const searchInput = document.getElementById('hero-search');
    const searchBtn = document.getElementById('hero-search-btn');

    const handleSearch = () => {
        const query = searchInput.value.trim();
        if (query) {
            // Redirect to catalog page with search query
            window.location.href = `catalog.html?search=${encodeURIComponent(query)}`;
        }
    };

    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', handleSearch);
        
        // Handle Enter key
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }
});
