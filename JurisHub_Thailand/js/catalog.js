document.addEventListener('DOMContentLoaded', () => {

    // --- State ---
    let currentFilter = {
        search: '',
        categories: [],
        universities: [],
        sort: 'name_th_asc' // name_th_asc, code_asc
    };

    // --- DOM Elements ---
    const searchInput = document.getElementById('search-input');
    const sortSelect = document.getElementById('sort-select');
    const catContainer = document.getElementById('category-filters');
    const uniContainer = document.getElementById('university-filters');
    const gridContainer = document.getElementById('subject-grid');
    const resultsCount = document.getElementById('results-count');
    const noResultsBlock = document.getElementById('no-results');
    const resetBtn = document.getElementById('reset-filters');
    const emptyResetBtn = document.getElementById('empty-reset-btn');

    // Mobile specific
    const filterBtn = document.getElementById('mobile-filter-btn');
    const closeFilterBtn = document.getElementById('close-filter-btn');
    const sidebar = document.getElementById('filter-sidebar');
    const overlay = document.getElementById('filter-overlay');

    // Modal
    const modal = document.getElementById('subject-modal');
    const cloaseModalBtn = document.getElementById('close-modal-btn');
    const modalContent = modal.querySelector('.modal-content');

    // --- Initialize ---
    const init = () => {
        parseUrlParams();
        renderFilters();
        setupEventListeners();
        renderGrid();
    };

    // --- URL Params Helper ---
    const parseUrlParams = () => {
        const params = new URLSearchParams(window.location.search);
        const searchQ = params.get('search');
        if (searchQ) currentFilter.search = decodeURIComponent(searchQ);
        
        const catQ = params.get('cat');
        if (catQ) currentFilter.categories.push(decodeURIComponent(catQ));

        searchInput.value = currentFilter.search;
    };

    // --- Render Filter UI ---
    const renderFilters = () => {
        // Categories
        catContainer.innerHTML = categories.map(cat => `
            <label class="flex items-center space-x-3 cursor-pointer group">
                <input type="checkbox" value="${cat.name}" class="custom-checkbox filter-checkbox-cat w-5 h-5 rounded border-slate-300 text-primary focus:ring-primary" ${currentFilter.categories.includes(cat.name) ? 'checked' : ''}>
                <span class="text-sm text-secondary group-hover:text-primary transition-colors">${cat.icon} ${cat.name}</span>
            </label>
        `).join('');

        // Universities
        uniContainer.innerHTML = universities.map(uni => `
            <label class="flex items-center space-x-3 cursor-pointer group">
                <input type="checkbox" value="${uni.name}" class="custom-checkbox filter-checkbox-uni w-5 h-5 rounded border-slate-300 text-primary focus:ring-primary" ${currentFilter.universities.includes(uni.name) ? 'checked' : ''}>
                <span class="text-sm text-secondary group-hover:text-primary transition-colors">${uni.name}</span>
            </label>
        `).join('');
    };

    // --- Render Subject Cards ---
    const renderGrid = () => {
        // 1. Filter
        let filtered = subjectsData.filter(sub => {
            const matchSearch = !currentFilter.search || 
                sub.name_th.includes(currentFilter.search) || 
                sub.code.toLowerCase().includes(currentFilter.search.toLowerCase()) ||
                (sub.name_en && sub.name_en.toLowerCase().includes(currentFilter.search.toLowerCase()));
            
            const matchCat = currentFilter.categories.length === 0 || currentFilter.categories.includes(sub.category);
            
            const matchUni = currentFilter.universities.length === 0 || 
                sub.universities.some(u => currentFilter.universities.includes(u));

            return matchSearch && matchCat && matchUni;
        });

        // 2. Sort
        filtered.sort((a, b) => {
            if (currentFilter.sort === 'name_th_asc') {
                return a.name_th.localeCompare(b.name_th, 'th');
            } else if (currentFilter.sort === 'code_asc') {
                return a.code.localeCompare(b.code);
            }
            return 0;
        });

        // 3. Update UI
        resultsCount.innerText = `พบ ${filtered.length} รายวิชา`;

        if (filtered.length === 0) {
            gridContainer.classList.add('hidden');
            noResultsBlock.classList.remove('hidden');
        } else {
            gridContainer.classList.remove('hidden');
            noResultsBlock.classList.add('hidden');
            
            gridContainer.innerHTML = filtered.map(sub => {
                
                // Set Badge Color based on category
                let badgeClass = 'badge-gray';
                if(sub.category === 'แพ่ง') badgeClass = 'badge-blue';
                if(sub.category === 'อาญา') badgeClass = 'badge-red';
                if(sub.category === 'มหาชน') badgeClass = 'badge-purple';
                if(sub.category === 'วิธีพิจารณา') badgeClass = 'badge-green';
                if(sub.category === 'ระหว่างประเทศ') badgeClass = 'badge-orange';

                const unis = sub.universities.slice(0, 3).map(u => 
                    `<span class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-md border border-slate-200">${u}</span>`
                ).join('');
                const plusUni = sub.universities.length > 3 ? `<span class="text-xs text-secondary ml-1">+${sub.universities.length - 3}</span>` : '';

                return `
                <div class="glass-card rounded-2xl p-6 cursor-pointer flex flex-col h-full bg-white hover:border-primary/20" onclick="openSubjectModal('${sub.id}')">
                    <div class="flex justify-between items-start mb-4">
                        <span class="badge ${badgeClass}">${sub.category}</span>
                        <div class="flex flex-wrap gap-1 items-center justify-end">
                            ${unis} ${plusUni}
                        </div>
                    </div>
                    
                    <div class="mb-1 text-sm font-bold text-accent tracking-wider font-mono">${sub.code}</div>
                    <h3 class="text-xl font-bold font-serif text-primary mb-1 line-clamp-2">${sub.name_th}</h3>
                    <div class="text-sm text-secondary mb-4 line-clamp-1">${sub.name_en || ''}</div>
                    
                    <div class="mt-auto pt-4 border-t border-slate-100 flex items-center justify-between text-sm text-slate-500">
                        <span>หน่วยกิต: ${sub.credits}</span>
                        <span class="text-primary font-medium flex items-center gap-1 group-hover:text-accent transition-colors">
                            ดูรายละเอียด
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                        </span>
                    </div>
                </div>
                `;
            }).join('');
        }
    };

    // --- Modal Logic ---
    window.openSubjectModal = (id) => {
        const sub = subjectsData.find(s => s.id === id);
        if (!sub) return;

        // Set data
        document.getElementById('modal-title-th').innerText = sub.name_th;
        document.getElementById('modal-title-en').innerText = sub.name_en || '';
        document.getElementById('modal-desc').innerText = sub.description;
        
        document.getElementById('modal-badges').innerHTML = `
            <span class="bg-white/20 text-white border border-white/30 badge">${sub.code}</span>
            <span class="bg-accent text-white border border-accent badge">${sub.category}</span>
            <span class="bg-white text-primary badge font-bold">${sub.credits} หน่วยกิต</span>
        `;

        const studyBtn = document.getElementById('modal-btn-study');
        if (studyBtn) {
            studyBtn.onclick = () => {
                window.location.href = `viewer.html?id=${sub.id}`;
            };
        }

        document.getElementById('modal-universities').innerHTML = sub.universities.map(u => 
            `<div class="px-4 py-2 bg-white border border-slate-200 rounded-xl shadow-sm text-sm font-medium text-slate-700 flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-primary"></div>${u}
            </div>`
        ).join('');

        // Show modal
        modal.classList.remove('hidden');
        // Small delay to allow display block to apply before animating opacity
        setTimeout(() => {
            modal.classList.add('active');
        }, 10);
        document.body.style.overflow = 'hidden'; // prevent background scrolling
    };

    const closeModal = () => {
        modal.classList.remove('active');
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 300); // match css transition
        document.body.style.overflow = '';
    };

    // --- Event Listeners Setup ---
    const setupEventListeners = () => {
        // Search
        let debounceTimer;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                currentFilter.search = e.target.value.trim();
                renderGrid();
                updateUrl();
            }, 300);
        });

        // Sort
        sortSelect.addEventListener('change', (e) => {
            currentFilter.sort = e.target.value;
            renderGrid();
        });

        // Checkboxes delegation
        catContainer.addEventListener('change', (e) => {
            if(e.target.classList.contains('filter-checkbox-cat')) {
                const val = e.target.value;
                if(e.target.checked) currentFilter.categories.push(val);
                else currentFilter.categories = currentFilter.categories.filter(c => c !== val);
                renderGrid();
                updateUrl();
            }
        });

        uniContainer.addEventListener('change', (e) => {
            if(e.target.classList.contains('filter-checkbox-uni')) {
                const val = e.target.value;
                if(e.target.checked) currentFilter.universities.push(val);
                else currentFilter.universities = currentFilter.universities.filter(u => u !== val);
                renderGrid();
            }
        });

        // Resets
        const doReset = () => {
            currentFilter.search = '';
            currentFilter.categories = [];
            currentFilter.universities = [];
            searchInput.value = '';
            
            document.querySelectorAll('.filter-checkbox-cat').forEach(cb => cb.checked = false);
            document.querySelectorAll('.filter-checkbox-uni').forEach(cb => cb.checked = false);
            
            renderGrid();
            updateUrl();
        };

        resetBtn.addEventListener('click', doReset);
        emptyResetBtn.addEventListener('click', doReset);

        // Mobile Drawer
        const toggleDrawer = () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('hidden');
            if(sidebar.classList.contains('open')){
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        };

        filterBtn.addEventListener('click', toggleDrawer);
        closeFilterBtn.addEventListener('click', toggleDrawer);
        overlay.addEventListener('click', toggleDrawer);

        // Modal close
        cloaseModalBtn.addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            // Close if clicking outside the modal content
            if (e.target === modal) {
                closeModal();
            }
        });

        // Navbar mobile
        const navMenuBtn = document.getElementById('mobile-menu-btn');
        const closeMenuBtn = document.getElementById('close-menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (navMenuBtn && mobileMenu) {
            navMenuBtn.addEventListener('click', () => {
                mobileMenu.classList.remove('translate-x-full');
            });
        }
        if (closeMenuBtn && mobileMenu) {
            closeMenuBtn.addEventListener('click', () => {
                mobileMenu.classList.add('translate-x-full');
            });
        }
    };

    // Update URL history without reload
    const updateUrl = () => {
        const url = new URL(window.location);
        if(currentFilter.search) url.searchParams.set('search', currentFilter.search);
        else url.searchParams.delete('search');

        if(currentFilter.categories.length > 0) url.searchParams.set('cat', currentFilter.categories[0]); // only support one in url for now for simplicity
        else url.searchParams.delete('cat');

        window.history.replaceState({}, '', url);
    };

    // Run
    init();
});
