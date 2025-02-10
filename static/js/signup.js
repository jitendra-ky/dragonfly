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
            password: $('#password').val()
        }
        $.ajax({
            url: '/api/user-profile/',
            method: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function (response) {
                alert('sign up successful opt send');
                console.log(response);
                $signupCont.hide();
                $otpCont.show();
                email = formData.email;
            },
            error: function (response) {
                alert('sign up failed. Please try again.');
                console.log(response);
            }
        })
    })

    $('#otp-form').on('submit', function (event) {
        event.preventDefault();
        const formData = {
            email: email,
            otp: $('#otp').val()
        }
        $.ajax({
            url: '/api/sign-up-otp/',
            method: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function (response) {
                alert('otp verification successful');
                console.log(response);
            },
            error: function (response) {
                alert('otp verification failed. Please try again.');
                console.log(response);
            }
        })
    })
})