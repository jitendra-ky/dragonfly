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
                alert('Sign in successful');
                console.log(response);
            },
            error: function (response) {
                alert('Sign in failed. Please try again.');
                console.log(response);
            }
        })
    })
})