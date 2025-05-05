// Authentication JavaScript for CyberShield IDS

document.addEventListener('DOMContentLoaded', function() {
    // Toggle password visibility
    const toggleBtns = document.querySelectorAll('.toggle-password');
    
    toggleBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const input = this.closest('.input-group').querySelector('input');
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
    
    // Password strength meter
    const passwordInput = document.getElementById('password');
    const strengthMeter = document.querySelector('.password-strength');
    const progressBar = document.querySelector('.password-strength .progress-bar');
    
    if (passwordInput && strengthMeter && progressBar) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            let feedback = '';
            
            // Show strength meter only if password has content
            if (password.length > 0) {
                strengthMeter.classList.add('active');
                
                // Calculate password strength
                if (password.length >= 8) strength += 20;
                if (password.match(/[a-z]+/)) strength += 20;
                if (password.match(/[A-Z]+/)) strength += 20;
                if (password.match(/[0-9]+/)) strength += 20;
                if (password.match(/[^a-zA-Z0-9]+/)) strength += 20;
                
                // Update progress bar
                progressBar.style.width = strength + '%';
                
                // Update progress bar color
                if (strength < 40) {
                    progressBar.className = 'progress-bar weak';
                } else if (strength < 80) {
                    progressBar.className = 'progress-bar medium';
                } else {
                    progressBar.className = 'progress-bar strong';
                }
            } else {
                strengthMeter.classList.remove('active');
            }
        });
    }
    
    // Form validation for signup
    const signupForm = document.querySelector('form[action="/signup"]');
    
    if (signupForm) {
        const confirmPasswordInput = document.getElementById('confirm-password');
        
        signupForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Password length validation
            if (passwordInput && passwordInput.value.length < 8) {
                createErrorMessage(passwordInput, 'Password must be at least 8 characters long');
                isValid = false;
            }
            
            // Password match validation
            if (passwordInput && confirmPasswordInput && passwordInput.value !== confirmPasswordInput.value) {
                createErrorMessage(confirmPasswordInput, 'Passwords do not match');
                isValid = false;
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
    
    // Function to create error message
    function createErrorMessage(input, message) {
        // Remove any existing error message
        const existingError = input.parentNode.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Create new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message text-danger mt-1';
        errorDiv.textContent = message;
        
        // Insert error message after input group
        input.parentNode.parentNode.appendChild(errorDiv);
        
        // Highlight input
        input.classList.add('is-invalid');
        
        // Remove error when input changes
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
            const error = this.parentNode.parentNode.querySelector('.error-message');
            if (error) {
                error.remove();
            }
        });
    }
    
    // Animation for form submission
    const authForms = document.querySelectorAll('.auth-body form');
    
    authForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Only animate if form is valid
            if (form.checkValidity() && !e.defaultPrevented) {
                const submitBtn = form.querySelector('[type="submit"]');
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });
    });
});