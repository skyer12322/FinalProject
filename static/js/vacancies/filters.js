function load_data() {
    const payload = {
        specialization: specialization_input,
        occupancy: occupancy_input,
        position: position_input,
        tech: tech_input,
        industry: industry_input,
        min_salary: min_salary_input,
    };

    const request = new XMLHttpRequest();
    request.open('POST', '/api/filters', true);
    
    // Set headers for JSON
    request.setRequestHeader("Content-Type", "application/json");
    request.setRequestHeader("X-CSRFToken", getCookie("csrftoken")); // CSRF protection

    request.onload = function() {
        try {
            const data = JSON.parse(request.response);
            
            if (data.status === "ok") {
                // Clear results
                result_words.innerHTML = "";
                result_digits.innerHTML = "";

                // Populate lists
                data.data.words.forEach(word => {
                    result_words.innerHTML += `<li>${word}</li>`;
                });
                
                data.data.digits.forEach(digit => {
                    result_digits.innerHTML += `<li>${digit}</li>`;
                });
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