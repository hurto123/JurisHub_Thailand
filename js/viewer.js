document.addEventListener('DOMContentLoaded', () => {
    // --- Get subject ID from URL ---
    const params = new URLSearchParams(window.location.search);
    const subjectId = params.get('id') || 'law-civ-02'; // default to law-civ-02 for demo
    let currentChapterIndex = parseInt(params.get('ch') || '0');

    const subjectData = chaptersData[subjectId];

    if (!subjectData) {
        document.getElementById('content-loading').innerHTML = `
            <div class="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4 text-2xl">❌</div>
            <h3 class="text-xl font-bold font-serif text-primary mb-2">ไม่พบข้อมูลวิชา</h3>
            <p class="text-secondary mb-6">วิชานี้ยังไม่มีเนื้อหาในระบบ</p>
            <a href="catalog.html" class="px-6 py-2 btn-primary rounded-xl font-medium">กลับหน้าคลังวิชา</a>`;
        return;
    }

    const { subject, chapters } = subjectData;

    // --- Populate Header ---
    document.getElementById('viewer-code').textContent = subject.code;
    document.getElementById('viewer-category').textContent = subject.category;
    document.getElementById('viewer-title').textContent = subject.name_th;
    document.getElementById('viewer-subtitle').textContent = subject.name_en;
    document.title = `${subject.name_th} - JurisHub Thailand`;

    // --- Render Sidebar Chapter List ---
    const chapterListEl = document.getElementById('chapter-list');
    const renderSidebar = () => {
        chapterListEl.innerHTML = chapters.map((ch, i) => `
            <button data-index="${i}" class="sidebar-link w-full text-left px-4 py-3 rounded-xl text-sm font-medium flex items-center gap-3 ${i === currentChapterIndex ? 'active' : 'text-secondary'}">
                <span class="w-7 h-7 flex-shrink-0 rounded-full ${i === currentChapterIndex ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-500'} flex items-center justify-center text-xs font-bold">${ch.chapter_no}</span>
                <span class="line-clamp-2">${ch.title_th}</span>
            </button>
        `).join('');

        // Update progress
        const pct = Math.round(((currentChapterIndex + 1) / chapters.length) * 100);
        document.getElementById('progress-bar').style.width = pct + '%';
        document.getElementById('progress-text').textContent = pct + '%';

        // Attach clicks
        chapterListEl.querySelectorAll('.sidebar-link').forEach(btn => {
            btn.addEventListener('click', () => {
                currentChapterIndex = parseInt(btn.dataset.index);
                renderContent();
                renderSidebar();
                closeMobileSidebar();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        });
    };

    // --- Render Content ---
    const renderContent = () => {
        const ch = chapters[currentChapterIndex];
        const c = ch.content;
        const loadingEl = document.getElementById('content-loading');
        const bodyEl = document.getElementById('content-body');
        const navEl = document.getElementById('chapter-nav');

        loadingEl.classList.add('hidden');
        bodyEl.classList.remove('hidden');
        navEl.classList.remove('hidden');

        let html = '';

        // Header
        html += `<h2 class="text-3xl font-bold font-serif text-primary mb-8">${c.header}</h2>`;

        // Source attribution
        if (subject.source) {
            html += `<div class="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-8 text-sm text-amber-800 flex items-start gap-3">
                <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span><strong>แหล่งอ้างอิง:</strong> ${subject.source}</span>
            </div>`;
        }

        // Sections
        c.sections.forEach(sec => {
            html += `
            <div class="mb-8">
                <h3 class="text-xl font-bold font-serif text-primary mb-3 flex items-center gap-2">
                    <span class="w-1.5 h-6 bg-accent rounded-full"></span>
                    ${sec.title}
                </h3>
                <p class="text-slate-700 leading-relaxed pl-5">${sec.body}</p>
            </div>`;
        });

        // Legal Articles
        if (c.legal_articles && c.legal_articles.length > 0) {
            html += `<div class="my-10">
                <h3 class="text-lg font-bold font-serif text-primary mb-4 flex items-center gap-2">
                    <svg class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    ตัวบทกฎหมายที่เกี่ยวข้อง
                </h3>`;
            c.legal_articles.forEach(art => {
                html += `
                <div class="article-card bg-white rounded-xl p-5 mb-4 shadow-sm border border-slate-100">
                    <div class="flex items-center gap-2 mb-2">
                        <span class="badge bg-accent/10 text-accent font-bold">${art.article_no}</span>
                        <span class="text-xs text-secondary">${art.law_name}</span>
                    </div>
                    <p class="text-slate-700 text-sm leading-relaxed">${art.content}</p>
                </div>`;
            });
            html += `</div>`;
        }

        // Explanation
        if (c.explanation) {
            html += `
            <div class="bg-primary/5 rounded-2xl p-6 my-8 border border-primary/10">
                <h3 class="text-lg font-bold font-serif text-primary mb-3 flex items-center gap-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>
                    คำอธิบาย / สรุป
                </h3>
                <p class="text-slate-700 leading-relaxed">${c.explanation}</p>
            </div>`;
        }

        // Case References
        if (c.case_references && c.case_references.length > 0) {
            html += `
            <div class="mt-8">
                <h4 class="text-sm font-bold text-secondary mb-3">คำพิพากษาที่เกี่ยวข้อง</h4>
                <div class="flex flex-wrap gap-2">
                    ${c.case_references.map(ref => `<span class="case-ref px-3 py-1.5 rounded-lg text-sm font-medium text-amber-800">${ref}</span>`).join('')}
                </div>
            </div>`;
        }

        bodyEl.innerHTML = html;

        // Update nav buttons
        document.getElementById('prev-chapter').style.visibility = currentChapterIndex > 0 ? 'visible' : 'hidden';
        document.getElementById('next-chapter').style.visibility = currentChapterIndex < chapters.length - 1 ? 'visible' : 'hidden';

        // Update URL
        const url = new URL(window.location);
        url.searchParams.set('id', subjectId);
        url.searchParams.set('ch', currentChapterIndex);
        window.history.replaceState({}, '', url);
        renderRelatedArticles();
    };

    // --- Render Related Articles (Subject Specific) [NEW] ---
    const renderRelatedArticles = () => {
        const sectionEl = document.getElementById('related-articles-section');
        const listEl = document.getElementById('related-articles-list');
        
        // Filter articles tagged with this subjectId
        const filtered = articlesData.filter(art => art.related_subject_id === subjectId);

        if (filtered.length === 0) {
            sectionEl.classList.add('hidden');
            return;
        }

        sectionEl.classList.remove('hidden');
        listEl.innerHTML = filtered.map(art => {
            // Mapping code type to colors
            let colorClass = 'border-slate-300';
            if(art.code_type === 'ป.พ.พ.') colorClass = 'border-blue-400';
            if(art.code_type === 'ป.อ.') colorClass = 'border-red-400';

            return `
            <div class="bg-white rounded-2xl p-6 border-l-8 ${colorClass} shadow-sm transition-all hover:shadow-md">
                <div class="flex justify-between items-start mb-3">
                    <span class="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-xs font-bold uppercase">${art.code_type}</span>
                    <span class="text-primary font-bold font-serif">${art.article_no}</span>
                </div>
                <div class="space-y-3">
                    <div>
                        <p class="text-xs font-bold text-slate-400 uppercase tracking-tighter mb-1">ตัวบทกฎหมาย:</p>
                        <p class="text-slate-600 text-sm leading-relaxed italic border-l-2 border-slate-100 pl-3">"${art.original_text}"</p>
                    </div>
                    <div class="bg-green-50 p-3 rounded-lg border border-green-100">
                        <p class="text-xs font-bold text-green-600 uppercase tracking-tighter mb-1">AI สรุปใจความ:</p>
                        <p class="text-primary text-sm font-medium">${art.summary_by_ai}</p>
                    </div>
                </div>
            </div>`;
        }).join('');
    };

    // --- Navigation Buttons ---
    document.getElementById('prev-chapter').addEventListener('click', () => {
        if (currentChapterIndex > 0) {
            currentChapterIndex--;
            renderContent();
            renderSidebar();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });

    document.getElementById('next-chapter').addEventListener('click', () => {
        if (currentChapterIndex < chapters.length - 1) {
            currentChapterIndex++;
            renderContent();
            renderSidebar();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });

    // --- Mobile Sidebar ---
    const sidebar = document.getElementById('viewer-sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const toggleBtn = document.getElementById('toggle-sidebar-btn');
    const closeBtn = document.getElementById('close-sidebar-btn');

    const closeMobileSidebar = () => {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.add('hidden');
    };

    if (toggleBtn) toggleBtn.addEventListener('click', () => {
        sidebar.classList.add('open');
        sidebarOverlay.classList.remove('hidden');
    });
    if (closeBtn) closeBtn.addEventListener('click', closeMobileSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeMobileSidebar);

    // --- Mobile Nav Menu ---
    const mobileBtn = document.getElementById('mobile-menu-btn');
    const closeMenuBtn = document.getElementById('close-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileBtn && mobileMenu) {
        mobileBtn.addEventListener('click', () => mobileMenu.classList.remove('translate-x-full'));
        closeMenuBtn.addEventListener('click', () => mobileMenu.classList.add('translate-x-full'));
    }

    // --- Init ---
    renderSidebar();
    renderContent();
});
