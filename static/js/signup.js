$(function () {
    const $signupCont = $('#signup-container');
    const $otpCont = $('#otp-verification');
    let email = undefined;
    $otpCont.hide();

    $('#signup-form').on('submit', function (event) {
        event.preventDefault();
        const formData = {
            fullname: $('#fullname').val(),
            email: $('#email').val(),
            password: $('#password').val(),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        }
        $.ajax({
            url: '/api/user-profile/',
            method: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': formData.csrfmiddlewaretoken
            },
            success: function (response) {
                alert('sign up successful opt send');
                console.log(response);
                $signupCont.hide();
                $otpCont.show();
                email = formData.email;
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

    $('#otp-form').on('submit', function (event) {
        event.preventDefault();
        const formData = {
            email: email,
            otp: $('#otp').val(),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
        }
        $.ajax({
            url: '/api/sign-up-otp/',
            method: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': formData.csrfmiddlewaretoken
            },
            success: function (response) {
                alert('otp verification successful');
                console.log(response);
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