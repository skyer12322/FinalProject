document.addEventListener('DOMContentLoaded', function() {
    const registerButton = document.getElementById('loginButton');
    const registrationForm = document.getElementById('loginForm');
    const alertsContainer = document.getElementById('form_alerts');
    const isCompanySwitch = document.getElementById('CompanyLoginCheckbox');

    registerButton.addEventListener('click', function() {
        
        let passwordValid = false;
        let passwordField;
        passwordField = document.getElementById('password');

        
        if (loginForm.checkValidity()) {
            loginForm.submit();
        } else {
            const submitButton = document.createElement('button');
            submitButton.type = 'submit';
            submitButton.style.display = 'none';
            loginForm.appendChild(submitButton);
            submitButton.click();
            loginForm.removeChild(submitButton);
        }
    });
});