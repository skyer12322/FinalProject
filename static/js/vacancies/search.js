function search() {
    vacanciesList.innerHTML = `
    <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>`;
    let request = new XMLHttpRequest()
    request.open('GET',
        'search?data=' + searchInput.value,
        true)
    request.onload = function() {
        try {
            let data = JSON.parse(request.response)
            if (data.status === "ok") {
                if (data.data.vacancies.length > 0){
                    vacanciesList.innerHTML = ''
                    data.data.vacancies.forEach((item, index) => {
                        let vacancyHtml = `
                            <div class="col-12">
                                <a href="/vacancy/${item.id}" style="text-decoration: none;">
                                    <div class="job-card vacancy">
                                        <div class="job-header">
                                            <h3>${item.title}</h3>
                                            <span class="ai-rating">AIR: ${item.ai_rating}</span>
                                        </div>
                                        <div class="job-meta">
                                            <span class="company">${item.company}</span>
                                            <span class="location">${item.geography}</span>
                                            <span class="salary">${item.min_salary} - ${item.max_salary} 
                                                <span class="currency-badge">${item.currency}</span>
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

    request.send()
}