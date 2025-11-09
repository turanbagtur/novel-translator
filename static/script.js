// Novel Translator - Frontend JavaScript

let currentProjectId = null;
let currentGlossaryProjectId = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadProjects();
    loadAIProviders();
    loadProjectSelectors();
    updateSidebarStats();
});

// Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const view = item.dataset.view;
            switchView(view);
            
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function switchView(viewName) {
    const views = document.querySelectorAll('.view');
    views.forEach(view => view.classList.remove('active'));
    
    const targetView = document.getElementById(`${viewName}-view`);
    if (targetView) {
        targetView.classList.add('active');
        
        // Load data when switching to specific views
        if (viewName === 'projects') {
            loadProjects();
        } else if (viewName === 'settings') {
            loadAIConfigs();
        }
    }
}

// Modal Management
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        // Reset form if exists
        const form = modal.querySelector('form');
        if (form) form.reset();
    }
}

// Toast Notifications
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ============= PROJECTS =============

async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        const projects = await response.json();
        
        const projectsList = document.getElementById('projects-list');
        
        // Update sidebar stats
        updateSidebarStats();
        
        if (projects.length === 0) {
            projectsList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open icon"></i>
                    <h3>Henüz proje yok</h3>
                    <p>Yeni bir proje oluşturarak başlayın</p>
                </div>
            `;
            return;
        }
        
        projectsList.innerHTML = projects.map(project => `
            <div class="project-card" onclick="viewProject(${project.id})">
                <div class="project-card-header">
                    <div>
                        <h3>${escapeHtml(project.name)}</h3>
                        <p>${escapeHtml(project.description || 'Açıklama yok')}</p>
                    </div>
                </div>
                <div class="project-stats">
                    <div class="stat">
                        <span class="stat-label">Bölüm</span>
                        <span class="stat-value">${project.chapter_count}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Dil</span>
                        <span class="stat-value">${project.source_language} → ${project.target_language}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">AI</span>
                        <span class="stat-value">${project.ai_provider}</span>
                    </div>
                </div>
                <div class="project-actions" onclick="event.stopPropagation()">
                    <button class="btn btn-small btn-danger" onclick="deleteProject(${project.id})">🗑️ Sil</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading projects:', error);
        showToast('Projeler yüklenirken hata oluştu', 'error');
    }
}

function showCreateProjectModal() {
    showModal('create-project-modal');
}

async function createProject(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = {
        name: formData.get('name'),
        description: formData.get('description'),
        source_language: formData.get('source_language'),
        target_language: formData.get('target_language'),
        ai_provider: formData.get('ai_provider'),
        ai_model: formData.get('ai_model') || null
    };
    
    try {
        const response = await fetch('/api/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showToast('Proje başarıyla oluşturuldu!');
            closeModal('create-project-modal');
            loadProjects();
            loadProjectSelectors();
        } else {
            showToast('Proje oluşturulurken hata oluştu', 'error');
        }
    } catch (error) {
        console.error('Error creating project:', error);
        showToast('Proje oluşturulurken hata oluştu', 'error');
    }
}

async function viewProject(projectId) {
    currentProjectId = projectId;
    
    try {
        const response = await fetch(`/api/projects/${projectId}`);
        const project = await response.json();
        
        // Switch to translation view and load chapters
        switchView('translate');
        document.querySelector('[data-view="translate"]').click();
        
        const projectSelect = document.getElementById('project-select');
        projectSelect.value = projectId;
        await loadProjectChapters();
    } catch (error) {
        console.error('Error viewing project:', error);
        showToast('Proje yüklenirken hata oluştu', 'error');
    }
}

async function deleteProject(projectId) {
    if (!confirm('Bu projeyi silmek istediğinizden emin misiniz? Tüm bölümler ve sözlük kayıtları silinecektir.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/projects/${projectId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Proje silindi');
            loadProjects();
            loadProjectSelectors();
        } else {
            showToast('Proje silinirken hata oluştu', 'error');
        }
    } catch (error) {
        console.error('Error deleting project:', error);
        showToast('Proje silinirken hata oluştu', 'error');
    }
}

// ============= CHAPTERS =============

async function loadProjectSelectors() {
    try {
        const response = await fetch('/api/projects');
        const projects = await response.json();
        
        const projectSelect = document.getElementById('project-select');
        const glossarySelect = document.getElementById('glossary-project-select');
        const exportSelect = document.getElementById('export-project-select');
        const glossaryExportSelect = document.getElementById('glossary-export-project-select');
        const backupSelect = document.getElementById('backup-project-select');
        
        const options = projects.map(p => 
            `<option value="${p.id}">${escapeHtml(p.name)}</option>`
        ).join('');
        
        const optionsHTML = '<option value="">Proje seçiniz...</option>' + options;
        
        if (projectSelect) projectSelect.innerHTML = optionsHTML;
        if (glossarySelect) glossarySelect.innerHTML = optionsHTML;
        if (exportSelect) exportSelect.innerHTML = optionsHTML;
        if (glossaryExportSelect) glossaryExportSelect.innerHTML = optionsHTML;
        if (backupSelect) backupSelect.innerHTML = optionsHTML;
    } catch (error) {
        console.error('Error loading project selectors:', error);
    }
}

async function loadProjectChapters() {
    const projectId = document.getElementById('project-select').value;
    const chaptersSection = document.getElementById('chapters-section');
    
    if (!projectId) {
        chaptersSection.style.display = 'none';
        return;
    }
    
    currentProjectId = projectId;
    chaptersSection.style.display = 'block';
    
    try {
        const response = await fetch(`/api/projects/${projectId}`);
        const project = await response.json();
        
        const chaptersList = document.getElementById('chapters-list');
        
        if (project.chapters.length === 0) {
            chaptersList.innerHTML = `
                <div class="empty-state">
                    <div class="icon">📄</div>
                    <h3>Henüz bölüm yok</h3>
                    <p>Yeni bölüm ekleyerek başlayın</p>
                </div>
            `;
            return;
        }
        
        chaptersList.innerHTML = project.chapters.map(chapter => `
            <div class="chapter-item">
                <div class="chapter-info">
                    <h4>Bölüm ${chapter.chapter_number}${chapter.title ? ': ' + escapeHtml(chapter.title) : ''}</h4>
                    <div class="chapter-meta">
                        <span class="status-badge status-${chapter.status}">${getStatusText(chapter.status)}</span>
                        <span>${new Date(chapter.created_at).toLocaleDateString('tr-TR')}</span>
                    </div>
                </div>
                <div class="chapter-actions">
                    ${chapter.status === 'pending' || chapter.status === 'error' ? 
                        `<button class="btn btn-small btn-success" onclick="translateChapter(${chapter.id})">
                            🌐 Çevir
                        </button>` : ''}
                    <button class="btn btn-small btn-primary" onclick="viewChapter(${chapter.id})">
                        👁️ Görüntüle
                    </button>
                    <button class="btn btn-small btn-danger" onclick="deleteChapter(${chapter.id})">
                        🗑️ Sil
                    </button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading chapters:', error);
        showToast('Bölümler yüklenirken hata oluştu', 'error');
    }
}

function showAddChapterModal() {
    if (!currentProjectId) {
        showToast('Lütfen önce bir proje seçin', 'warning');
        return;
    }
    showModal('add-chapter-modal');
}

async function addChapter(event) {
    event.preventDefault();
    
    if (!currentProjectId) {
        showToast('Lütfen önce bir proje seçin', 'warning');
        return;
    }
    
    const formData = new FormData(event.target);
    const action = event.submitter.value;
    
    const data = {
        chapter_number: parseInt(formData.get('chapter_number')),
        title: formData.get('title') || null,
        original_text: formData.get('original_text')
    };
    
    try {
        const response = await fetch(`/api/projects/${currentProjectId}/chapters`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Bölüm eklendi!');
            closeModal('add-chapter-modal');
            loadProjectChapters();
            
            // If action is translate, start translation
            if (action === 'translate') {
                setTimeout(() => translateChapter(result.id), 500);
            }
        } else {
            showToast('Bölüm eklenirken hata oluştu', 'error');
        }
    } catch (error) {
        console.error('Error adding chapter:', error);
        showToast('Bölüm eklenirken hata oluştu', 'error');
    }
}

async function viewChapter(chapterId) {
    try {
        const response = await fetch(`/api/chapters/${chapterId}`);
        const chapter = await response.json();
        
        const modalTitle = document.getElementById('chapter-modal-title');
        modalTitle.textContent = `Bölüm ${chapter.chapter_number}${chapter.title ? ': ' + chapter.title : ''}`;
        
        const content = document.getElementById('chapter-detail-content');
        content.innerHTML = `
            <div class="chapter-detail-split">
                <div class="text-panel">
                    <h4>📄 Orijinal Metin</h4>
                    <div class="text-content">${escapeHtml(chapter.original_text)}</div>
                </div>
                <div class="text-panel">
                    <h4>🌐 Çeviri</h4>
                    <div class="text-content">
                        ${chapter.translated_text ? escapeHtml(chapter.translated_text) : 
                          '<p style="color: var(--text-secondary);">Henüz çevrilmedi</p>'}
                    </div>
                </div>
            </div>
            ${chapter.translation_stats && Object.keys(chapter.translation_stats).length > 0 ? `
                <div style="padding: 1.5rem; border-top: 1px solid var(--border-color);">
                    <h4 style="margin-bottom: 1rem;">📊 Çeviri İstatistikleri</h4>
                    <pre style="background: var(--dark-bg); padding: 1rem; border-radius: 0.5rem; overflow: auto;">
${JSON.stringify(chapter.translation_stats, null, 2)}
                    </pre>
                </div>
            ` : ''}
        `;
        
        showModal('chapter-detail-modal');
    } catch (error) {
        console.error('Error viewing chapter:', error);
        showToast('Bölüm yüklenirken hata oluştu', 'error');
    }
}

async function translateChapter(chapterId) {
    if (!confirm('Bu bölümü çevirmek istediğinizden emin misiniz?')) {
        return;
    }
    
    showToast('Çeviri başlatıldı... Bu işlem birkaç dakika sürebilir.', 'warning');
    showLoading(true);
    
    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chapter_id: chapterId,
                extract_terms: true
            })
        });
        
        showLoading(false);
        
        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                showToast('Çeviri başarıyla tamamlandı!', 'success');
                loadProjectChapters();
            } else {
                showToast(`Çeviri hatası: ${result.error}`, 'error');
            }
        } else {
            const error = await response.json();
            showToast(`Çeviri hatası: ${error.detail || 'Bilinmeyen hata'}`, 'error');
        }
    } catch (error) {
        showLoading(false);
        console.error('Error translating chapter:', error);
        showToast('Çeviri sırasında hata oluştu: ' + error.message, 'error');
    }
}

async function deleteChapter(chapterId) {
    if (!confirm('Bu bölümü silmek istediğinizden emin misiniz?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/chapters/${chapterId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Bölüm silindi');
            loadProjectChapters();
        } else {
            showToast('Bölüm silinirken hata oluştu', 'error');
        }
    } catch (error) {
        console.error('Error deleting chapter:', error);
        showToast('Bölüm silinirken hata oluştu', 'error');
    }
}

// ============= GLOSSARY =============

let bulkModeActive = false;
let selectedTerms = new Set();

async function loadGlossary() {
    const projectId = document.getElementById('glossary-project-select').value;
    
    if (!projectId) {
        document.getElementById('glossary-list').innerHTML = '';
        document.getElementById('glossary-controls').style.display = 'none';
        return;
    }
    
    currentGlossaryProjectId = projectId;
    document.getElementById('glossary-controls').style.display = 'block';
    
    try {
        const response = await fetch(`/api/projects/${projectId}/glossary`);
        const entries = await response.json();
        
        const glossaryList = document.getElementById('glossary-list');
        
        if (entries.length === 0) {
            glossaryList.innerHTML = `
                <div class="empty-state">
                    <div class="icon">📖</div>
                    <h3>Sözlük boş</h3>
                    <p>Terim ekleyerek başlayın</p>
                </div>
            `;
            return;
        }
        
        glossaryList.innerHTML = `
            <table>
                <thead>
                    <tr>
                        ${bulkModeActive ? '<th><input type="checkbox" onclick="selectAllTerms(this)"></th>' : ''}
                        <th>Orijinal</th>
                        <th>Çeviri</th>
                        <th>Tür</th>
                        <th>Durum</th>
                        <th>Kullanım</th>
                        ${!bulkModeActive ? '<th>İşlemler</th>' : ''}
                    </tr>
                </thead>
                <tbody>
                    ${entries.map(entry => `
                        <tr ${entry.confirmed ? '' : 'style="background: rgba(245, 158, 11, 0.05);"'} 
                            data-term-id="${entry.id}" 
                            onclick="bulkModeActive && toggleTermSelection(${entry.id})">
                            ${bulkModeActive ? `
                                <td>
                                    <input type="checkbox" class="term-checkbox" data-term-id="${entry.id}" 
                                           ${selectedTerms.has(entry.id) ? 'checked' : ''} 
                                           onclick="event.stopPropagation(); toggleTermSelection(${entry.id})">
                                </td>
                            ` : ''}
                            <td>
                                <strong>${escapeHtml(entry.original_term)}</strong>
                                ${!entry.confirmed ? '<span style="color: var(--warning-color); margin-left: 0.5rem;"><i class="fas fa-robot"></i></span>' : ''}
                            </td>
                            <td>${escapeHtml(entry.translated_term)}</td>
                            <td>
                                <span class="term-type-badge type-${entry.term_type}">
                                    ${getTermTypeText(entry.term_type)}
                                </span>
                            </td>
                            <td>
                                ${entry.confirmed 
                                    ? '<span style="color: var(--success-color);"><i class="fas fa-check-circle"></i> Onaylı</span>'
                                    : '<span style="color: var(--warning-color);"><i class="fas fa-robot"></i> Otomatik</span>'}
                            </td>
                            <td>${entry.usage_count}x</td>
                            ${!bulkModeActive ? `
                                <td>
                                    ${!entry.confirmed ? `
                                        <button class="btn btn-small btn-success" onclick="event.stopPropagation(); confirmGlossaryEntry(${entry.id})" title="Onayla">
                                            <i class="fas fa-check"></i>
                                        </button>
                                    ` : ''}
                                    <button class="btn btn-small btn-danger" onclick="event.stopPropagation(); deleteGlossaryEntry(${entry.id})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            ` : ''}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Error loading glossary:', error);
        showToast('Sözlük yüklenirken hata oluştu', 'error');
    }
}

function showAddGlossaryModal() {
    if (!currentGlossaryProjectId) {
        showToast('Lütfen önce bir proje seçin', 'warning');
        return;
    }
    showModal('add-glossary-modal');
}

async function addGlossaryEntry(event) {
    event.preventDefault();
    
    if (!currentGlossaryProjectId) {
        showToast('Lütfen önce bir proje seçin', 'warning');
        return;
    }
    
    const formData = new FormData(event.target);
    const data = {
        original_term: formData.get('original_term'),
        translated_term: formData.get('translated_term'),
        term_type: formData.get('term_type'),
        context: formData.get('context') || null
    };
    
    try {
        const response = await fetch(`/api/projects/${currentGlossaryProjectId}/glossary`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showToast('Terim eklendi!');
            closeModal('add-glossary-modal');
            loadGlossary();
        } else {
            showToast('Terim eklenirken hata oluştu', 'error');
        }
    } catch (error) {
        console.error('Error adding glossary entry:', error);
        showToast('Terim eklenirken hata oluştu', 'error');
    }
}

async function confirmGlossaryEntry(entryId) {
    try {
        // Get entry details first - FIX: Correct endpoint
        const response = await fetch(`/api/projects/${currentGlossaryProjectId}/glossary`);
        const entries = await response.json();
        const entry = entries.find(e => e.id === entryId);
        
        if (!entry) {
            showToast('Entry not found', 'error');
            return;
        }
        
        // Update as confirmed
        const updateResponse = await fetch(`/api/glossary/${entryId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                original_term: entry.original_term,
                translated_term: entry.translated_term,
                term_type: entry.term_type,
                context: entry.context
            })
        });
        
        if (updateResponse.ok) {
            showToast('Term confirmed successfully!', 'success');
            loadGlossary();
        } else {
            showToast('Confirmation failed', 'error');
        }
    } catch (error) {
        console.error('Error confirming glossary entry:', error);
        showToast('Error confirming term', 'error');
    }
}

async function deleteGlossaryEntry(entryId) {
    if (!confirm('Bu terimi silmek istediğinizden emin misiniz?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/glossary/${entryId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Terim silindi', 'success');
            loadGlossary();
        } else {
            showToast('Terim silinirken hata oluştu', 'error');
        }
    } catch (error) {
        console.error('Error deleting glossary entry:', error);
        showToast('Terim silinirken hata oluştu', 'error');
    }
}

// ============= ADVANCED GLOSSARY FEATURES =============

// Search glossary
let searchTimeout;
async function searchGlossary() {
    clearTimeout(searchTimeout);
    
    searchTimeout = setTimeout(async () => {
        const query = document.getElementById('glossary-search').value;
        const termType = document.getElementById('glossary-filter-type').value;
        const confirmedOnly = document.getElementById('glossary-filter-confirmed').checked;
        
        if (!currentGlossaryProjectId) return;
        
        try {
            const params = new URLSearchParams();
            if (query) params.append('query', query);
            if (termType) params.append('term_type', termType);
            if (confirmedOnly) params.append('confirmed_only', 'true');
            
            const response = await fetch(`/api/glossary/${currentGlossaryProjectId}/search?${params}`);
            const entries = await response.json();
            
            // Update table with search results
            displayGlossaryEntries(entries);
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 300);
}

function displayGlossaryEntries(entries) {
    const glossaryList = document.getElementById('glossary-list');
    
    if (!entries || entries.length === 0) {
        glossaryList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search icon"></i>
                <h3>Sonuç bulunamadı</h3>
                <p>Arama kriterlerini değiştirin</p>
            </div>
        `;
        return;
    }
    
    // Reuse the table generation from loadGlossary
    const table = document.querySelector('.glossary-table table');
    if (table) {
        const tbody = table.querySelector('tbody');
        tbody.innerHTML = entries.map(entry => generateGlossaryRow(entry)).join('');
    }
}

function generateGlossaryRow(entry) {
    return `
        <tr ${entry.confirmed ? '' : 'style="background: rgba(245, 158, 11, 0.05);"'} 
            data-term-id="${entry.id}" 
            onclick="bulkModeActive && toggleTermSelection(${entry.id})">
            ${bulkModeActive ? `
                <td>
                    <input type="checkbox" class="term-checkbox" data-term-id="${entry.id}" 
                           ${selectedTerms.has(entry.id) ? 'checked' : ''} 
                           onclick="event.stopPropagation(); toggleTermSelection(${entry.id})">
                </td>
            ` : ''}
            <td>
                <strong>${escapeHtml(entry.original_term)}</strong>
                ${!entry.confirmed ? '<span style="color: var(--warning-color); margin-left: 0.5rem;"><i class="fas fa-robot"></i></span>' : ''}
            </td>
            <td>${escapeHtml(entry.translated_term)}</td>
            <td>
                <span class="term-type-badge type-${entry.term_type}">
                    ${getTermTypeText(entry.term_type)}
                </span>
            </td>
            <td>
                ${entry.confirmed 
                    ? '<span style="color: var(--success-color);"><i class="fas fa-check-circle"></i> Onaylı</span>'
                    : '<span style="color: var(--warning-color);"><i class="fas fa-robot"></i> Otomatik</span>'}
            </td>
            <td>${entry.usage_count}x</td>
            ${!bulkModeActive ? `
                <td>
                    ${!entry.confirmed ? `
                        <button class="btn btn-small btn-success" onclick="event.stopPropagation(); confirmGlossaryEntry(${entry.id})" title="Onayla">
                            <i class="fas fa-check"></i>
                        </button>
                    ` : ''}
                    <button class="btn btn-small btn-danger" onclick="event.stopPropagation(); deleteGlossaryEntry(${entry.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            ` : ''}
        </tr>
    `;
}

// Select all terms
function selectAllTerms(checkbox) {
    const checkboxes = document.querySelectorAll('.term-checkbox');
    checkboxes.forEach(cb => {
        const termId = parseInt(cb.dataset.termId);
        if (checkbox.checked) {
            selectedTerms.add(termId);
            cb.checked = true;
            cb.closest('tr').classList.add('selected');
        } else {
            selectedTerms.delete(termId);
            cb.checked = false;
            cb.closest('tr').classList.remove('selected');
        }
    });
    
    document.getElementById('selected-count').textContent = `${selectedTerms.size} seçili`;
}

// Bulk mode toggle
function toggleBulkMode() {
    bulkModeActive = !bulkModeActive;
    selectedTerms.clear();
    
    const table = document.querySelector('.glossary-table');
    const bulkBar = document.getElementById('bulk-action-bar');
    
    if (bulkModeActive) {
        table.classList.add('bulk-mode');
        bulkBar.style.display = 'flex';
    } else {
        table.classList.remove('bulk-mode');
        bulkBar.style.display = 'none';
    }
    
    loadGlossary();
}

function toggleTermSelection(termId) {
    if (selectedTerms.has(termId)) {
        selectedTerms.delete(termId);
    } else {
        selectedTerms.add(termId);
    }
    
    // Update UI
    const row = document.querySelector(`tr[data-term-id="${termId}"]`);
    if (row) {
        row.classList.toggle('selected');
        const checkbox = row.querySelector('.term-checkbox');
        if (checkbox) checkbox.checked = selectedTerms.has(termId);
    }
    
    // Update count
    document.getElementById('selected-count').textContent = `${selectedTerms.size} seçili`;
}

function cancelBulkMode() {
    toggleBulkMode();
}

// Bulk operations
async function bulkConfirmSelected() {
    if (selectedTerms.size === 0) {
        showToast('Lütfen terim seçin', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/api/glossary/${currentGlossaryProjectId}/bulk-confirm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(Array.from(selectedTerms))
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast(result.message, 'success');
            selectedTerms.clear();
            loadGlossary();
            cancelBulkMode();
        }
    } catch (error) {
        console.error('Bulk confirm error:', error);
        showToast('Toplu onaylama başarısız', 'error');
    }
}

async function bulkDeleteSelected() {
    if (selectedTerms.size === 0) {
        showToast('Lütfen terim seçin', 'warning');
        return;
    }
    
    if (!confirm(`${selectedTerms.size} terimi silmek istediğinizden emin misiniz?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/glossary/${currentGlossaryProjectId}/bulk-delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(Array.from(selectedTerms))
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast(result.message, 'success');
            selectedTerms.clear();
            loadGlossary();
            cancelBulkMode();
        }
    } catch (error) {
        console.error('Bulk delete error:', error);
        showToast('Toplu silme başarısız', 'error');
    }
}

function showBulkTypeModal() {
    if (selectedTerms.size === 0) {
        showToast('Lütfen terim seçin', 'warning');
        return;
    }
    showModal('bulk-type-modal');
}

async function applyBulkTypeChange() {
    const newType = document.getElementById('bulk-new-type').value;
    
    try {
        const response = await fetch(`/api/glossary/${currentGlossaryProjectId}/bulk-update-type`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                term_ids: Array.from(selectedTerms),
                new_type: newType
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast(result.message, 'success');
            closeModal('bulk-type-modal');
            selectedTerms.clear();
            loadGlossary();
            cancelBulkMode();
        }
    } catch (error) {
        console.error('Bulk type change error:', error);
        showToast('Tür değiştirme başarısız', 'error');
    }
}

// Show glossary statistics
async function showGlossaryStats() {
    if (!currentGlossaryProjectId) {
        showToast('Lütfen bir proje seçin', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/api/glossary/${currentGlossaryProjectId}/stats`);
        const stats = await response.json();
        
        const content = `
            <div class="stats-grid">
                <div class="stat-box">
                    <h4>${stats.total_terms}</h4>
                    <p>Toplam Terim</p>
                </div>
                <div class="stat-box">
                    <h4>${stats.by_status.confirmed || 0}</h4>
                    <p>Onaylı</p>
                </div>
                <div class="stat-box">
                    <h4>${stats.by_status.unconfirmed || 0}</h4>
                    <p>Otomatik</p>
                </div>
            </div>
            
            <h4 style="margin: 1.5rem 0 1rem;"><i class="fas fa-chart-pie"></i> Türlere Göre Dağılım</h4>
            <div class="stats-grid">
                ${Object.entries(stats.by_type || {}).map(([type, count]) => `
                    <div class="stat-box">
                        <h4>${count}</h4>
                        <p>${getTermTypeText(type)}</p>
                    </div>
                `).join('')}
            </div>
            
            <h4 style="margin: 1.5rem 0 1rem;"><i class="fas fa-fire"></i> En Çok Kullanılanlar</h4>
            <div class="top-terms-list">
                ${stats.most_used.map((term, idx) => `
                    <div class="top-term-item">
                        <div>
                            <strong>${idx + 1}. ${escapeHtml(term.original)}</strong>
                            <br>
                            <small>${escapeHtml(term.translated)}</small>
                        </div>
                        <div style="text-align: right;">
                            <span class="term-type-badge type-${term.type}">${getTermTypeText(term.type)}</span>
                            <br>
                            <small>${term.count}x kullanım</small>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        document.getElementById('glossary-stats-content').innerHTML = content;
        showModal('glossary-stats-modal');
    } catch (error) {
        console.error('Stats error:', error);
        showToast('İstatistikler yüklenemedi', 'error');
    }
}

// Merge duplicates
async function mergeDuplicates() {
    if (!confirm('Aynı orijinal terime sahip duplikalar birleştirilecek. Devam edilsin mi?')) {
        return;
    }
    
    try {
        showLoading(true);
        const response = await fetch(`/api/glossary/${currentGlossaryProjectId}/merge-duplicates`, {
            method: 'POST'
        });
        
        showLoading(false);
        
        if (response.ok) {
            const result = await response.json();
            showToast(result.message, 'success');
            loadGlossary();
        }
    } catch (error) {
        showLoading(false);
        console.error('Merge error:', error);
        showToast('Birleştirme başarısız', 'error');
    }
}

// ============= GLOSSARY IMPORT =============

function showImportGlossaryModal() {
    if (!currentGlossaryProjectId) {
        showToast('Lütfen önce bir proje seçin', 'warning');
        return;
    }
    showModal('import-glossary-modal');
}

async function importGlossary() {
    const fileInput = document.getElementById('import-glossary-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showToast('Lütfen bir dosya seçin', 'warning');
        return;
    }
    
    if (!currentGlossaryProjectId) {
        showToast('Lütfen önce bir proje seçin', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`/api/glossary/${currentGlossaryProjectId}/import`, {
            method: 'POST',
            body: formData
        });
        
        showLoading(false);
        
        if (response.ok) {
            const result = await response.json();
            showToast(result.message, 'success');
            closeModal('import-glossary-modal');
            fileInput.value = '';
            await loadGlossary();
        } else {
            const error = await response.json();
            showToast(`Import hatası: ${error.detail}`, 'error');
        }
    } catch (error) {
        showLoading(false);
        console.error('Import error:', error);
        showToast('İçe aktarma sırasında hata oluştu', 'error');
    }
}

// ============= AI PROVIDERS =============

async function loadAIProviders() {
    try {
        const response = await fetch('/api/ai-providers');
        const data = await response.json();
        // Store for later use
        window.availableProviders = data.providers;
    } catch (error) {
        console.error('Error loading AI providers:', error);
    }
}

let currentAIConfigs = {};

async function loadAIConfigs() {
    try {
        const response = await fetch('/api/ai-configs');
        const configs = await response.json();
        
        const providersList = document.getElementById('ai-providers-list');
        
        // Create a map of existing configs
        const configMap = {};
        configs.forEach(config => {
            configMap[config.provider_name] = config;
        });
        
        // Store configs globally
        currentAIConfigs = configMap;
        
        // Get all available providers
        const allProviders = [
            // AI Models
            'gemini', 'openai', 'claude', 'groq', 'deepseek', 'perplexity',
            // Professional Translation APIs
            'deepl', 'google-translate', 'microsoft-translator', 'yandex',
            // Free/Open Source
            'libretranslate', 'mymemory'
        ];
        
        providersList.innerHTML = allProviders.map(provider => {
            const config = configMap[provider];
            const isConfigured = config && config.has_api_key;
            const isEnabled = config && config.enabled;
            
            return `
                <div class="ai-provider-card">
                    <div class="provider-info">
                        <h4><i class="${getProviderIcon(provider)}"></i> ${getProviderName(provider)}</h4>
                        <p>${isConfigured ? 'Yapılandırılmış ✓' : 'Yapılandırılmamış'}</p>
                    </div>
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div class="provider-status">
                            <span class="status-indicator ${isEnabled ? 'active' : 'inactive'}"></span>
                            <span>${isEnabled ? 'Aktif' : 'Pasif'}</span>
                        </div>
                        <button class="btn btn-small btn-primary btn-icon" onclick="configureAIProvider('${provider}')">
                            <i class="fas fa-cog"></i> Yapılandır
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading AI configs:', error);
        showToast('AI yapılandırmaları yüklenirken hata oluştu', 'error');
    }
}

async function configureAIProvider(providerName) {
    // Get existing config if available
    const existingConfig = currentAIConfigs[providerName];
    
    // Set form values
    document.getElementById('config-provider-name').value = providerName;
    document.getElementById('ai-config-modal-title').innerHTML = 
        `<i class="fas fa-robot"></i> ${getProviderName(providerName)} Yapılandır`;
    
    // Fill form with existing values or defaults
    document.getElementById('config-api-key').value = '';  // Never show existing key
    document.getElementById('config-api-key').placeholder = existingConfig && existingConfig.has_api_key ? 
        'API anahtarı kayıtlı (yeni girmezseniz değişmez)' : 'API anahtarınızı buraya girin';
    document.getElementById('config-api-key').required = !existingConfig || !existingConfig.has_api_key;
    
    document.getElementById('config-model').value = existingConfig?.model || '';
    document.getElementById('config-max-tokens').value = existingConfig?.max_tokens || 4000;
    document.getElementById('config-temperature').value = existingConfig?.temperature || 0.7;
    document.getElementById('config-enabled').checked = existingConfig?.enabled !== false;
    
    showModal('ai-config-modal');
}

async function saveAIConfig(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const apiKey = formData.get('api_key');
    const providerName = formData.get('provider_name');
    const existingConfig = currentAIConfigs[providerName];
    
    // Only include api_key if it was entered
    const data = {
        provider_name: providerName,
        model: formData.get('model') || null,
        max_tokens: parseInt(formData.get('max_tokens')),
        temperature: parseFloat(formData.get('temperature')),
        enabled: formData.get('enabled') === 'on'
    };
    
    // Add api_key only if provided
    if (apiKey && apiKey.trim()) {
        data.api_key = apiKey;
    } else if (existingConfig && existingConfig.has_api_key) {
        // Keep existing key (backend will handle this)
        data.api_key = null;
    }
    
    try {
        showLoading(true);
        const response = await fetch('/api/ai-configs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        showLoading(false);
        
        if (response.ok) {
            showToast('AI sağlayıcı yapılandırması kaydedildi!', 'success');
            closeModal('ai-config-modal');
            await loadAIConfigs();
        } else {
            showToast('Yapılandırma kaydedilirken hata oluştu', 'error');
        }
    } catch (error) {
        showLoading(false);
        console.error('Error saving AI config:', error);
        showToast('Yapılandırma kaydedilirken hata oluştu', 'error');
    }
}

// ============= UTILITY FUNCTIONS =============

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getStatusText(status) {
    const statusMap = {
        'pending': 'Bekliyor',
        'processing': 'İşleniyor',
        'completed': 'Tamamlandı',
        'error': 'Hata'
    };
    return statusMap[status] || status;
}

function getTermTypeText(type) {
    const typeMap = {
        'general': 'Genel',
        'character': 'Karakter',
        'location': 'Yer',
        'skill': 'Yetenek',
        'item': 'Eşya'
    };
    return typeMap[type] || type;
}

function getProviderName(provider) {
    const nameMap = {
        // AI Models
        'gemini': 'Google Gemini',
        'openai': 'OpenAI (ChatGPT)',
        'claude': 'Anthropic Claude',
        'groq': 'Groq',
        'deepseek': 'DeepSeek',
        'perplexity': 'Perplexity',
        // Professional Translation
        'deepl': 'DeepL',
        'google-translate': 'Google Cloud Translate',
        'microsoft-translator': 'Microsoft Translator',
        'yandex': 'Yandex Translate',
        // Free/Open Source
        'libretranslate': 'LibreTranslate',
        'mymemory': 'MyMemory'
    };
    return nameMap[provider] || provider;
}

function getProviderIcon(provider) {
    const iconMap = {
        // AI Models
        'gemini': 'fas fa-gem',
        'openai': 'fas fa-brain',
        'claude': 'fas fa-robot',
        'groq': 'fas fa-bolt',
        'deepseek': 'fas fa-search',
        'perplexity': 'fas fa-infinity',
        // Professional Translation
        'deepl': 'fas fa-language',
        'google-translate': 'fas fa-globe',
        'microsoft-translator': 'fab fa-microsoft',
        'yandex': 'fas fa-y',
        // Free/Open Source
        'libretranslate': 'fas fa-code',
        'mymemory': 'fas fa-database'
    };
    return iconMap[provider] || 'fas fa-robot';
}

function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.classList.add('show');
    } else {
        overlay.classList.remove('show');
    }
}

// Update chapter count in sidebar
async function updateSidebarStats() {
    try {
        const projectsResponse = await fetch('/api/projects');
        const projects = await projectsResponse.json();
        
        let totalChapters = 0;
        for (const project of projects) {
            totalChapters += project.chapter_count || 0;
        }
        
        document.getElementById('total-projects').textContent = projects.length;
        document.getElementById('total-chapters').textContent = totalChapters;
    } catch (error) {
        console.error('Error updating sidebar stats:', error);
    }
}

// ============= DASHBOARD FUNCTIONS =============

async function loadDashboard() {
    try {
        const response = await fetch('/api/stats/dashboard');
        const stats = await response.json();
        
        // Update stat cards
        document.getElementById('dash-total-projects').textContent = stats.projects.total;
        document.getElementById('dash-total-chapters').textContent = stats.chapters.total;
        document.getElementById('dash-completed-chapters').textContent = stats.chapters.completed;
        document.getElementById('dash-glossary-terms').textContent = stats.glossary.total_terms;
        
        // Update costs
        document.getElementById('dash-total-cost').textContent = `$${stats.costs.total_cost.toFixed(4)}`;
        document.getElementById('dash-total-tokens').textContent = stats.costs.total_tokens.toLocaleString();
        
        // Update completion progress
        const completionRate = stats.chapters.completion_rate;
        document.getElementById('completion-progress').style.width = `${completionRate}%`;
        document.getElementById('completion-text').textContent = `${completionRate}%`;
        
        // Update provider costs
        const providerCostsHTML = Object.entries(stats.costs.by_provider || {}).map(([provider, data]) => `
            <div class="provider-cost-item">
                <div>
                    <strong>${getProviderName(provider)}</strong>
                    <br>
                    <small>${data.count} çeviri</small>
                </div>
                <div style="text-align: right;">
                    <strong style="color: var(--primary-color);">$${data.total_cost.toFixed(4)}</strong>
                    <br>
                    <small>${data.total_tokens.toLocaleString()} token</small>
                </div>
            </div>
        `).join('');
        
        document.getElementById('cost-by-provider').innerHTML = providerCostsHTML ||
            '<p style="color: var(--text-secondary); text-align: center;">Henüz maliyet verisi yok</p>';
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Dashboard yüklenirken hata oluştu', 'error');
    }
}

// ============= EXPORT FUNCTIONS =============

async function loadExportSelectors() {
    try {
        const response = await fetch('/api/projects');
        const projects = await response.json();
        
        const options = projects.map(p => 
            `<option value="${p.id}">${escapeHtml(p.name)}</option>`
        ).join('');
        
        const exportSelect = document.getElementById('export-project-select');
        const glossaryExportSelect = document.getElementById('glossary-export-project-select');
        
        if (exportSelect) {
            exportSelect.innerHTML = '<option value="">Proje seçiniz...</option>' + options;
        }
        if (glossaryExportSelect) {
            glossaryExportSelect.innerHTML = '<option value="">Proje seçiniz...</option>' + options;
        }
    } catch (error) {
        console.error('Error loading export selectors:', error);
    }
}

async function exportProject(format) {
    const projectId = document.getElementById('export-project-select').value;
    
    if (!projectId) {
        showToast('Lütfen bir proje seçin', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`/api/export/project/${projectId}/${format}`);
        
        showLoading(false);
        
        if (response.ok) {
            // Download file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `export_${projectId}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showToast(`${format.toUpperCase()} export başarılı!`, 'success');
        } else {
            const error = await response.json();
            showToast(`Export hatası: ${error.detail}`, 'error');
        }
    } catch (error) {
        showLoading(false);
        console.error('Export error:', error);
        showToast('Export sırasında hata oluştu', 'error');
    }
}

async function exportGlossary(format) {
    const projectId = document.getElementById('glossary-export-project-select').value;
    
    if (!projectId) {
        showToast('Lütfen bir proje seçin', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`/api/glossary/${projectId}/export?format=${format}`);
        
        showLoading(false);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `glossary_${projectId}.${format === 'csv' ? 'csv' : 'xlsx'}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showToast('Sözlük export başarılı!', 'success');
        } else {
            const error = await response.json();
            showToast(`Export hatası: ${error.detail}`, 'error');
        }
    } catch (error) {
        showLoading(false);
        console.error('Glossary export error:', error);
        showToast('Export sırasında hata oluştu', 'error');
    }
}

// ============= BACKUP FUNCTIONS =============

async function loadBackupSelectors() {
    try {
        const response = await fetch('/api/projects');
        const projects = await response.json();
        
        const options = projects.map(p => 
            `<option value="${p.id}">${escapeHtml(p.name)}</option>`
        ).join('');
        
        const backupSelect = document.getElementById('backup-project-select');
        if (backupSelect) {
            backupSelect.innerHTML = '<option value="">Proje seçiniz...</option>' + options;
        }
    } catch (error) {
        console.error('Error loading backup selectors:', error);
    }
}

async function createBackup() {
    const projectId = document.getElementById('backup-project-select').value;
    
    if (!projectId) {
        showToast('Lütfen bir proje seçin', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`/api/backup/create/${projectId}`, {
            method: 'POST'
        });
        
        showLoading(false);
        
        if (response.ok) {
            const result = await response.json();
            showToast('Yedek başarıyla oluşturuldu!', 'success');
            await loadBackups();
        } else {
            const error = await response.json();
            showToast(`Yedekleme hatası: ${error.detail}`, 'error');
        }
    } catch (error) {
        showLoading(false);
        console.error('Backup error:', error);
        showToast('Yedekleme sırasında hata oluştu', 'error');
    }
}

async function restoreBackup() {
    const fileInput = document.getElementById('restore-backup-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showToast('Lütfen bir yedek dosyası seçin', 'warning');
        return;
    }
    
    if (!confirm('Yedek geri yüklenecek. Devam etmek istiyor musunuz?')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/backup/restore', {
            method: 'POST',
            body: formData
        });
        
        showLoading(false);
        
        if (response.ok) {
            const result = await response.json();
            showToast('Yedek başarıyla geri yüklendi!', 'success');
            fileInput.value = '';
            await loadProjects();
        } else {
            const error = await response.json();
            showToast(`Geri yükleme hatası: ${error.detail}`, 'error');
        }
    } catch (error) {
        showLoading(false);
        console.error('Restore error:', error);
        showToast('Geri yükleme sırasında hata oluştu', 'error');
    }
}

async function loadBackups() {
    try {
        const response = await fetch('/api/backup/list');
        const backups = await response.json();
        
        const backupsList = document.getElementById('backups-list');
        
        if (!backups || backups.length === 0) {
            backupsList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox icon"></i>
                    <h3>Henüz yedek yok</h3>
                    <p>İlk yedeğinizi oluşturun</p>
                </div>
            `;
            return;
        }
        
        backupsList.innerHTML = backups.map(backup => `
            <div class="backup-item">
                <div class="backup-info">
                    <h4><i class="fas fa-file-archive"></i> Yedek #${backup.id}</h4>
                    <p>
                        <i class="fas fa-calendar"></i> ${new Date(backup.created_at).toLocaleString('tr-TR')}
                        | <i class="fas fa-hdd"></i> ${(backup.backup_size / 1024).toFixed(2)} KB
                        | <i class="fas fa-tag"></i> ${backup.backup_type}
                    </p>
                </div>
                <div class="backup-actions">
                    <button class="btn btn-small btn-danger" onclick="deleteBackupItem(${backup.id})">
                        <i class="fas fa-trash"></i> Sil
                    </button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading backups:', error);
        showToast('Yedekler yüklenirken hata oluştu', 'error');
    }
}

async function deleteBackupItem(backupId) {
    if (!confirm('Bu yedeği silmek istediğinizden emin misiniz?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/backup/${backupId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Yedek silindi', 'success');
            await loadBackups();
        } else {
            showToast('Yedek silinirken hata oluştu', 'error');
        }
    } catch (error) {
        console.error('Delete backup error:', error);
        showToast('Silme işlemi başarısız', 'error');
    }
}

// ============= THEME FUNCTIONS =============

function setTheme(theme) {
    // Update active button
    document.querySelectorAll('.theme-option').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-theme="${theme}"]`).classList.add('active');
    
    // Apply theme
    if (theme === 'light') {
        document.body.classList.add('light-theme');
    } else if (theme === 'dark') {
        document.body.classList.remove('light-theme');
    } else { // auto
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) {
            document.body.classList.remove('light-theme');
        } else {
            document.body.classList.add('light-theme');
        }
    }
    
    // Save preference
    localStorage.setItem('theme', theme);
    showToast('Tema değiştirildi', 'success');
}

// Load theme on startup
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
}

// ============= KEYBOARD SHORTCUTS =============

document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N: New Project
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        showCreateProjectModal();
    }
    
    // Ctrl/Cmd + D: Dashboard
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        switchView('dashboard');
        document.querySelector('[data-view="dashboard"]').click();
    }
    
    // Ctrl/Cmd + F: Focus search (if implemented)
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        // Implement search focus
    }
});

// Initialize new features on load
document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    loadExportSelectors();
    loadBackupSelectors();
    
    // Load dashboard if it's the active view
    const dashboardView = document.getElementById('dashboard-view');
    if (dashboardView && dashboardView.classList.contains('active')) {
        loadDashboard();
    }
});

// Update view switching to load data
const originalSwitchView = switchView;
switchView = function(viewName) {
    originalSwitchView(viewName);
    
    // Load data for specific views
    if (viewName === 'dashboard') {
        loadDashboard();
    } else if (viewName === 'export') {
        loadExportSelectors();
    } else if (viewName === 'backup') {
        loadBackups();
        loadBackupSelectors();
    }
};

