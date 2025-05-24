function applyFilters() {
    const specialization_input = document.getElementById('specializationList').value;
    const occupancy_input = document.getElementById('occupancyList').value;
    const position_input = document.getElementById('positionList').value;
    const tech_input = document.getElementById('techList').value;
    const industry_input = document.getElementById('industryList').value;
    const min_salary_input = document.getElementById('min_salary_input').value;
    const max_salary_input = document.getElementById('max_salary_input').value;
    const payload = {
        specialization: specialization_input,
        occupancy: occupancy_input,
        position: position_input,
        tech: tech_input,
        industry: industry_input,
        min_salary: min_salary_input,
        max_salary: max_salary_input,
    };
    vacanciesList.innerHTML = `
    <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>`;

    const request = new XMLHttpRequest();
    request.open('GET', '/api/filters?data=' + JSON.stringify(payload), true);

    request.onload = function() {
        try {
            const data = JSON.parse(request.response);
            if (data.status === "ok") {
                if (data.data.vacancies.length > 0){
                    vacanciesList.innerHTML = ''
                    data.data.vacancies.forEach((item, index) => {
                        let vacancyHtml = `
                            <div class="col-12">
                                <a href="/vacancies/${item.id}" style="text-decoration: none;">
                                    <div class="job-card vacancy">
                                        <div class="job-header">
                                            <h3>${item.title}</h3>
                                            <span class="ai-rating">AIR: ${item.ai_rating}</span>
                                        </div>
                                        <div class="job-meta">
                                            <span class="company">${item.company}</span>
                                            <span class="location">${item.geography}</span>
                                            <span class="salary">${item.min_salary} - ${item.max_salary} 
                                                <!-- <span class="currency-badge">${item.currency}</span> -->
                                            </span>
                                        </div>
                                    </div>
                                </a>
                            </div>`;
                        vacanciesList.innerHTML += vacancyHtml
                    })
                    
                }
                else{
                    vacanciesList.innerHTML = '<div class="row g-4"><h1 class="no-vacancies">Пока что нет доступных вакансий</h1></div>'
                }
            } else {
                result_error.innerHTML = data.error;
            }
        } catch (e) {
            console.error("JSON Parse Error:", e);
        }
    };

    request.onerror = function() {
        result_error.innerHTML = "Network error occurred.";
    };

    // Send JSON string
    request.send(JSON.stringify(payload));
}