$(function () {
  const $forgotPasswordForm = $('#forgot-password-form')
  const $resetPasswordForm = $('#reset-password-form')
  const $errorMessage = $('.error-message')
  const $successDropDown = $('.success-drop-down')

  $forgotPasswordForm.on('submit', function (event) {
    event.preventDefault()
    const formData = {
      email: $('#email').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
    }
    $.ajax({
      url: '/api/forgot-password/',
      method: 'POST',
      data: JSON.stringify(formData),
      contentType: 'application/json',
      headers: {
        'X-CSRFToken': formData.csrfmiddlewaretoken,
      },
      success: function (response) {
        $successDropDown.text('OTP sent successfully. Please check your email.')
        $successDropDown.css('display', 'flex')
        setTimeout(() => {
          $successDropDown.css('display', 'none')
          $forgotPasswordForm.hide()
          $resetPasswordForm.show()
        }, 1000)
      },
      error: function (response) {
        let error_message = ''
        if (response.responseJSON) {
          for (const key in response.responseJSON) {
            error_message += `${key}: ${response.responseJSON[key] + '\n'}`
          }
        } else {
          error_message = 'An unexpected error occurred.'
        }
        $errorMessage.text(error_message)
      },
    })
  })

  $resetPasswordForm.on('submit', function (event) {
    event.preventDefault()
    const formData = {
      email: $('#email').val(),
      otp: $('#otp').val(),
      new_password: $('#new-password').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
    }
    $.ajax({
      url: '/api/reset-password/',
      method: 'POST',
      data: JSON.stringify(formData),
      contentType: 'application/json',
      headers: {
        'X-CSRFToken': formData.csrfmiddlewaretoken,
      },
      success: function (response) {
        $successDropDown.text(
          'Password reset successful. Redirecting to sign-in page.'
        )
        $successDropDown.css('display', 'flex')
        setTimeout(() => {
          $successDropDown.css('display', 'none')
          window.location.href = '/signin/'
        }, 1000)
      },
      error: function (response) {
        let error_message = ''
        if (response.responseJSON) {
          for (const key in response.responseJSON) {
            error_message += `${key}: ${response.responseJSON[key] + '\n'}`
          }
        } else {
          error_message = 'An unexpected error occurred.'
        }
        $errorMessage.text(error_message)
      },
    })
  })
})
