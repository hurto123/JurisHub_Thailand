document.addEventListener('DOMContentLoaded', () => {

    // --- State ---
    let currentFilter = {
        search: '',
        type: 'all' // Matches codeTypes ID
    };

    // --- DOM Elements ---
    const searchInput = document.getElementById('article-search');
    const filterContainer = document.getElementById('code-type-filters');
    const feedContainer = document.getElementById('articles-feed');
    const resultsCount = document.getElementById('articles-count');
    const noResultsBlock = document.getElementById('no-articles');
    const resetBtn = document.getElementById('reset-articles-btn');

    // --- Initialize ---
    const init = () => {
        renderFilters();
        setupEventListeners();
        renderFeed();
    };

    // --- Render Filter UI ---
    const renderFilters = () => {
        filterContainer.innerHTML = codeTypes.map(type => `
            <button class="w-full text-left px-4 py-3 rounded-lg text-sm font-medium transition-all filter-btn ${type.id === currentFilter.type ? 'bg-primary text-white shadow-md' : 'text-secondary hover:bg-slate-50'}" data-type="${type.id}">
                ${type.name}
            </button>
        `).join('');
    };

    // --- Render Articles Feed ---
    const renderFeed = () => {
        // 1. Filter
        let filtered = articlesData.filter(art => {
            const matchSearch = !currentFilter.search || 
                art.article_no.toLowerCase().includes(currentFilter.search.toLowerCase()) || 
                art.original_text.toLowerCase().includes(currentFilter.search.toLowerCase()) ||
                art.summary_by_ai.toLowerCase().includes(currentFilter.search.toLowerCase());
            
            const matchType = currentFilter.type === 'all' || art.code_type === currentFilter.type;

            return matchSearch && matchType;
        });

        // 2. Update UI
        resultsCount.innerText = filtered.length;

        if (filtered.length === 0) {
            feedContainer.classList.add('hidden');
            noResultsBlock.classList.remove('hidden');
        } else {
            feedContainer.classList.remove('hidden');
            noResultsBlock.classList.add('hidden');
            
            feedContainer.innerHTML = filtered.map(art => {
                
                // Color coding for Code Type badges
                let badgeClass = 'bg-slate-100 text-slate-700'; // Default
                if(art.code_type === 'ป.พ.พ.') badgeClass = 'bg-blue-100 text-blue-700';
                if(art.code_type === 'ป.อ.') badgeClass = 'bg-red-100 text-red-700';
                if(art.code_type === 'รัฐธรรมนูญฯ') badgeClass = 'bg-amber-100 text-amber-700';

                return `
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden transition-all hover:shadow-md">
                    
                    <!-- Header -->
                    <div class="px-6 py-4 bg-slate-50 border-b border-slate-100 flex justify-between items-center">
                        <div class="flex items-center gap-3">
                            <span class="px-3 py-1 text-xs font-bold rounded-md ${badgeClass}">${art.code_type}</span>
                            <span class="text-lg font-bold font-serif text-primary">${art.article_no}</span>
                        </div>
                        <a href="viewer.html?id=${art.related_subject_id}" class="text-sm text-accent hover:underline font-medium items-center gap-1 hidden sm:flex">
                            ไปที่บทเรียนวิชานี้ 
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                        </a>
                    </div>

                    <div class="p-6 md:p-8 flex flex-col md:flex-row gap-6">
                        
                        <!-- ซ้าย: ตัวบทดั้งเดิม -->
                        <div class="flex-1">
                            <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                                ตัวบทต้นฉบับ
                            </h4>
                            <p class="text-slate-700 leading-relaxed text-sm md:text-base border-l-4 border-slate-200 pl-4 py-1 italic">
                                "${art.original_text}"
                            </p>
                        </div>

                        <!-- Divider for mobile -->
                        <div class="md:hidden border-t border-slate-100 my-2"></div>

                        <!-- ขวา: บทสรุป AI -->
                        <div class="flex-1 bg-green-50/50 rounded-xl p-5 border border-green-100 relative">
                            <h4 class="text-xs font-bold text-green-600 uppercase tracking-wider mb-2 flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                                คำอธิบายสรุป
                            </h4>
                            <p class="text-primary font-medium leading-relaxed">
                                ${art.summary_by_ai}
                            </p>
                            
                            <!-- Tags -->
                            <div class="mt-4 flex flex-wrap gap-2">
                                ${art.tags.map(tag => `<span class="text-xs px-2 py-1 bg-white border border-green-200 text-green-700 rounded-md">#${tag}</span>`).join('')}
                            </div>
                        </div>

                    </div>
                </div>
                `;
            }).join('');
        }
    };

    // --- Event Listeners Setup ---
    const setupEventListeners = () => {
        // Search
        let debounceTimer;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                currentFilter.search = e.target.value.trim();
                renderFeed();
            }, 300);
        });

        // Filter Click
        filterContainer.addEventListener('click', (e) => {
            const btn = e.target.closest('.filter-btn');
            if(btn) {
                currentFilter.type = btn.getAttribute('data-type');
                renderFilters(); // Re-render to update active styling
                renderFeed();
            }
        });

        // Reset
        resetBtn.addEventListener('click', () => {
            currentFilter.search = '';
            currentFilter.type = 'all';
            searchInput.value = '';
            renderFilters();
            renderFeed();
        });
    };

    // Run
    init();
});
