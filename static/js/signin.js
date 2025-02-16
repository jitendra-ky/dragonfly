$(function () {
    $('#signin-form').on('submit', function (event) {
        event.preventDefault();
        const formData = {
            email: $('#email').val(),
            password: $('#password').val(),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        }
        $.ajax({
            url: '/api/sign-in/',
            method: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': formData.csrfmiddlewaretoken
            },
            success: function (response) {
                $('.success-drop-down').text('You have successfully signed in.');
                $('.success-drop-down').css('display', 'flex');
                setTimeout(() => {
                    $('.success-drop-down').css('display', 'none');
                    // redirect to home page
                    window.location.href = '/';
                }, 1000);

            },
            error: function (response) {
                error_message = "";
                if (response.responseJSON) {
                    // as responseJSON contain errors of different fields in field: array(string);
                    for (const key in response.responseJSON) {
                        error_message += `${key}: ${response.responseJSON[key] + '\n'}`;
                    }
                } else {
                    error_message = 'An unexpected error occurred.';
                }
                $('.error-message').text(error_message);
            }
        })
    })
})