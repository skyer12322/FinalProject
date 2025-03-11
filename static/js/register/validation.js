document.addEventListener('DOMContentLoaded', function() {
    const registerButton = document.getElementById('registerButton');
    const registrationForm = document.getElementById('registrationForm');
    const alertsContainer = document.getElementById('form_alerts');
    const alertsContainer2 = document.getElementById('form_alerts_password');
    const alertsContainer3 = document.getElementById('form_alerts_password_company');
    const isCompanySwitch = document.getElementById('flexSwitchCheckDefault');
    
    // Toggle between user and company fields
    isCompanySwitch.addEventListener('change', function () {
        const userFields = document.getElementById('userFields');
        const companyFields = document.getElementById('companyFields');
        
        if (this.checked) {
            userFields.style.display = 'none';
            companyFields.style.display = 'block';
            
            // Для полей компании
            const companyInputs = ['companyName', 'companyPhone', 'companyEmail', 'companyPassword'];
            companyInputs.forEach(id => {
                const field = document.getElementById(id);
                if (field) {
                    field.required = true;
                    field.value = ''; // Сброс значений
                }
            });
            
            // Для полей пользователя
            const userInputs = ['firstName', 'lastName', 'username', 'phone', 'email', 'password'];
            userInputs.forEach(id => {
                const field = document.getElementById(id);
                if (field) field.required = false;
            });
        } else {
            userFields.style.display = 'block';
            companyFields.style.display = 'none';
            
            // Для полей пользователя
            const userInputs = ['firstName', 'lastName', 'username', 'phone', 'email', 'password'];
            userInputs.forEach(id => {
                const field = document.getElementById(id);
                if (field) {
                    field.required = true;
                    field.value = ''; // Сброс значений
                }
            });
            
            // Для полей компании
            const companyInputs = ['companyName', 'companyPhone', 'companyEmail', 'companyPassword'];
            companyInputs.forEach(id => {
                const field = document.getElementById(id);
                if (field) field.required = false;
            });
        }
    });
    
    // Password validation function
    function validatePassword(password) {
        const minLength = password.length >= 8;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasDigit = /\d/.test(password);
        const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
        const noSpaces = !/\s/.test(password);
        
        return {
            valid: minLength && hasUpperCase && hasLowerCase && hasDigit && hasSpecialChar && noSpaces,
            errors: {
                minLength,
                hasUpperCase,
                hasLowerCase,
                hasDigit,
                hasSpecialChar,
                noSpaces
            }
        };
    }
    
    // Form submission handler
    registerButton.addEventListener('click', function() {
        alertsContainer.innerHTML = '';
        alertsContainer2.innerHTML = '';
        alertsContainer3.innerHTML ='';
        
        // Check terms and privacy checkboxes
        const termsAccepted = document.getElementById('termsCheckbox1').checked;
        const privacyAccepted = document.getElementById('termsCheckbox2').checked;
        
        if (!termsAccepted || !privacyAccepted) {
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger';
            alert.textContent = 'Вы должны согласиться с Условиями пользования и Политикой конфиденциальности';
            if (isCompanySwitch.checked){
                alertsContainer3.appendChild(alert);
            }
            else {
                alertsContainer2.appendChild(alert);
            }
            return;
        }
        
        // Validate password based on form type
        let passwordValid = false;
        let passwordField;

        if (isCompanySwitch.checked) {
            passwordField = document.getElementById('companyPassword');
        } else {
            passwordField = document.getElementById('password');
        }
        
        const passwordValidation = validatePassword(passwordField.value);

        if (!passwordValidation.valid) {
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger';
            alert.innerHTML = 'Пароль не соответствует требованиям:<ul>';
            
            if (!passwordValidation.errors.minLength) {
                alert.innerHTML += '<li>Должен содержать не менее 8 символов</li>';
            }
            if (!passwordValidation.errors.hasUpperCase) {
                alert.innerHTML += '<li>Должен содержать хотя бы одну заглавную букву</li>';
            }
            if (!passwordValidation.errors.hasLowerCase) {
                alert.innerHTML += '<li>Должен содержать хотя бы одну строчную букву</li>';
            }
            if (!passwordValidation.errors.hasDigit) {
                alert.innerHTML += '<li>Должен содержать хотя бы одну цифру</li>';
            }
            if (!passwordValidation.errors.hasSpecialChar) {
                alert.innerHTML += '<li>Должен содержать хотя бы один специальный символ</li>';
            }
            if (!passwordValidation.errors.noSpaces) {
                alert.innerHTML += '<li>Не должен содержать пробелы</li>';
            }
            
            alert.innerHTML += '</ul>';
            if (isCompanySwitch.checked){
                alertsContainer3.appendChild(alert);
            }
            else {
                alertsContainer2.appendChild(alert);
            }
            return;
        }
        
        // If form is valid, submit it
        if (registrationForm.checkValidity()) {
            registrationForm.submit();
        } else {
            // Trigger browser's native form validation
            const submitButton = document.createElement('button');
            submitButton.type = 'submit';
            submitButton.style.display = 'none';
            registrationForm.appendChild(submitButton);
            submitButton.click();
            registrationForm.removeChild(submitButton);
        }
    });
});