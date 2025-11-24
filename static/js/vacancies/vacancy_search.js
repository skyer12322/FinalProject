function renderVacancies(vacancies) {
    if (vacancies.length > 0) {
        let html = '<div style="display: flex; flex-direction: column; gap: 16px;">';
        vacancies.forEach((item) => {
            html += `
                        <a href="/vacancies/${item.id}" class="vacancy-card">
                            <div class="vacancy-header">
                                <div style="flex: 1;">
                                    <h3 class="vacancy-title">${item.title}</h3>
                                    <div class="vacancy-meta">
                                        <span>🏢 ${item.company}</span>
                                        <span>💰 ${item.min_salary} - ${item.max_salary} ${item.currency}</span>
                                    </div>
                                </div>
                                <div class="ai-badge">AIR: ${item.ai_rating}</div>
                            </div>
                            <p style="color: var(--light-text); margin-top: 12px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
                                ${item.description || ''}
                            </p>
                        </a>`;
        });
        html += '</div>';
        vacanciesList.innerHTML = html;
    } else {
        vacanciesList.innerHTML = `<div class="text-center" style="padding: 60px 20px;">
                        <h2>Вакансии не найдены</h2>
                        <p style="color: var(--light-text); margin-top: 12px;">Попробуйте изменить параметры поиска</p>
                    </div>`;
    }
}

function search() {
    vacanciesList.innerHTML = `<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>`;
    
    fetch('search?data=' + searchInput.value)
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                renderVacancies(data.data.vacancies);
            } else {
                result_error.innerHTML = data.error;
            }
        })
        .catch(e => console.error("Search Error:", e));
}

function applyFilters() {
    const payload = {
        specialization: document.getElementById('specializationList').value,
        occupancy: document.getElementById('occupancyList').value,
        position: document.getElementById('positionList').value,
        tech: document.getElementById('techList').value,
        industry: document.getElementById('industryList').value,
        min_salary: document.getElementById('min_salary_input').value,
        max_salary: document.getElementById('max_salary_input').value,
    };
    
    vacanciesList.innerHTML = `<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>`;
    
    fetch('/api/filters?data=' + JSON.stringify(payload))
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                renderVacancies(data.data.vacancies);
            } else {
                result_error.innerHTML = data.error;
            }
        })
        .catch(e => console.error("Filter Error:", e));
}