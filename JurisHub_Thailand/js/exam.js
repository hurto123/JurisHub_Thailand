document.addEventListener('DOMContentLoaded', () => {

    // --- DOM ---
    const examListEl = document.getElementById('exam-list');
    const noExamsEl = document.getElementById('no-exams');
    const filterSubject = document.getElementById('filter-subject');
    const filterUniversity = document.getElementById('filter-university');
    const filterType = document.getElementById('filter-type');
    const revealAllBtn = document.getElementById('reveal-all-btn');

    // --- Populate filter dropdowns ---
    const uniqueSubjects = [...new Map(examsData.map(e => [e.subject_id, { id: e.subject_id, name: e.subject_name }])).values()];
    uniqueSubjects.forEach(s => {
        filterSubject.innerHTML += `<option value="${s.id}">${s.name}</option>`;
    });

    const uniqueUnis = [...new Set(examsData.map(e => e.university))];
    uniqueUnis.forEach(u => {
        filterUniversity.innerHTML += `<option value="${u}">${u}</option>`;
    });

    // --- Rendering ---
    const renderExams = () => {
        const fSubject = filterSubject.value;
        const fUni = filterUniversity.value;
        const fType = filterType.value;

        let filtered = examsData.filter(exam => {
            if (fSubject && exam.subject_id !== fSubject) return false;
            if (fUni && exam.university !== fUni) return false;
            if (fType && exam.exam_type !== fType) return false;
            return true;
        });

        if (filtered.length === 0) {
            examListEl.classList.add('hidden');
            noExamsEl.classList.remove('hidden');
            return;
        }

        examListEl.classList.remove('hidden');
        noExamsEl.classList.add('hidden');

        examListEl.innerHTML = filtered.map((exam, ei) => {
            const typeLabel = exam.exam_type === 'midterm' ? 'สอบกลางภาค' : 'สอบปลายภาค';
            const typeBadge = exam.exam_type === 'midterm' ? 'badge-blue' : 'badge-red';

            const questionsHtml = exam.questions.map((q, qi) => `
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden exam-card-enter" style="animation-delay: ${qi * 0.1}s">
                    <!-- Question -->
                    <div class="p-6">
                        <div class="flex items-start gap-4">
                            <div class="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold font-serif flex-shrink-0">${q.number}</div>
                            <div class="flex-1">
                                <div class="flex items-center gap-2 mb-3">
                                    <span class="text-xs font-bold text-secondary">คะแนน ${q.points} คะแนน</span>
                                </div>
                                <p class="text-slate-800 leading-relaxed font-medium">${q.text}</p>
                            </div>
                        </div>
                    </div>
                    <!-- Answer -->
                    <div class="border-t border-slate-100 bg-slate-50/50 relative">
                        <button class="toggle-answer-btn w-full px-6 py-3 flex items-center gap-2 text-sm font-medium text-accent hover:text-amber-700 transition-colors" data-exam="${ei}" data-q="${qi}">
                            <svg class="w-4 h-4 eye-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L6.11 6.11m3.768 3.768l4.242 4.242M3 3l3.111 3.111m0 0A9.935 9.935 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path></svg>
                            <span class="toggle-text">ดูธงคำตอบ</span>
                        </button>
                        <div class="px-6 pb-6 relative">
                            <div class="answer-blur answer-content-${ei}-${qi}">
                                <div class="bg-white rounded-xl p-5 border border-slate-200 text-sm text-slate-700 leading-relaxed whitespace-pre-line">${q.answer}</div>
                            </div>
                            <div class="answer-overlay answer-overlay-${ei}-${qi}">
                                <span class="bg-primary/80 text-white px-4 py-2 rounded-full text-sm font-medium backdrop-blur-sm pointer-events-auto cursor-pointer hover:bg-primary transition-colors" onclick="this.closest('.border-t').querySelector('.toggle-answer-btn').click()">
                                    🔒 คลิกเพื่อดูคำตอบ
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

            return `
            <section class="exam-section">
                <!-- Exam Header Card -->
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 mb-4">
                    <div class="flex flex-wrap items-center gap-3 mb-3">
                        <span class="badge font-mono bg-primary text-white">${exam.subject_code}</span>
                        <span class="badge ${typeBadge}">${typeLabel}</span>
                        <span class="badge badge-gray">${exam.university}</span>
                        <span class="text-xs text-secondary ml-auto">ปีการศึกษา ${exam.year} ภาค ${exam.semester}</span>
                    </div>
                    <h2 class="text-xl font-bold font-serif text-primary">${exam.subject_name}</h2>
                    <p class="text-sm text-secondary mt-1">${exam.questions.length} ข้อ · ${exam.questions.reduce((s, q) => s + q.points, 0)} คะแนนรวม</p>
                </div>
                <!-- Questions -->
                <div class="space-y-4 ml-0 md:ml-4">
                    ${questionsHtml}
                </div>
            </section>`;
        }).join('');

        // Attach toggle listeners
        document.querySelectorAll('.toggle-answer-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const { exam: e, q } = btn.dataset;
                const answerEl = document.querySelector(`.answer-content-${e}-${q}`);
                const overlayEl = document.querySelector(`.answer-overlay-${e}-${q}`);
                const textEl = btn.querySelector('.toggle-text');
                const isRevealed = answerEl.classList.toggle('revealed');
                
                if (isRevealed) {
                    textEl.textContent = 'ซ่อนคำตอบ';
                    overlayEl.style.opacity = '0';
                } else {
                    textEl.textContent = 'ดูธงคำตอบ';
                    overlayEl.style.opacity = '1';
                }
            });
        });
    };

    // --- Reveal All ---
    let allRevealed = false;
    revealAllBtn.addEventListener('click', () => {
        allRevealed = !allRevealed;
        document.querySelectorAll('[class*="answer-content-"]').forEach(el => {
            if (allRevealed) el.classList.add('revealed');
            else el.classList.remove('revealed');
        });
        document.querySelectorAll('[class*="answer-overlay-"]').forEach(el => {
            el.style.opacity = allRevealed ? '0' : '1';
        });
        document.querySelectorAll('.toggle-text').forEach(el => {
            el.textContent = allRevealed ? 'ซ่อนคำตอบ' : 'ดูธงคำตอบ';
        });
        revealAllBtn.innerHTML = allRevealed
            ? `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M3 3l18 18"></path></svg> ซ่อนทั้งหมด`
            : `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg> เปิดคำตอบทั้งหมด`;
    });

    // --- Filters ---
    filterSubject.addEventListener('change', renderExams);
    filterUniversity.addEventListener('change', renderExams);
    filterType.addEventListener('change', renderExams);

    // --- Mobile Nav ---
    const mobileBtn = document.getElementById('mobile-menu-btn');
    const closeMenuBtn = document.getElementById('close-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileBtn && mobileMenu) {
        mobileBtn.addEventListener('click', () => mobileMenu.classList.remove('translate-x-full'));
        closeMenuBtn.addEventListener('click', () => mobileMenu.classList.add('translate-x-full'));
    }

    // --- Init ---
    renderExams();
});
