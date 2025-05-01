// Toggle password visibility
function togglePassword(inputId) {
    const input = $('#' + inputId);
    const icon = $(`[onclick="togglePassword('${inputId}')"] i`);
    
    if (input.attr('type') === 'password') {
        input.attr('type', 'text');
        icon.removeClass('fa-eye').addClass('fa-eye-slash');
    } else {
        input.attr('type', 'password');
        icon.removeClass('fa-eye-slash').addClass('fa-eye');
    }
}

// Switch between login and register forms
function switchToRegister() {
    $('#login-form').addClass('hidden');
    $('#register-form').removeClass('hidden');
    $('#login-tab').removeClass('tab-active').addClass('text-gray-500');
    $('#register-tab').addClass('tab-active').removeClass('text-gray-500');
}

function switchToLogin() {
    $('#register-form').addClass('hidden');
    $('#login-form').removeClass('hidden');
    $('#register-tab').removeClass('tab-active').addClass('text-gray-500');
    $('#login-tab').addClass('tab-active').removeClass('text-gray-500');
}

// Document ready
$(document).ready(function() {
    // Tab click handlers
    $('#login-tab').on('click', switchToLogin);
    $('#register-tab').on('click', switchToRegister);
});