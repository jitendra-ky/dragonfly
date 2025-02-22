import { getCookie } from './assets.js'

$(function () {
  // Check if session_id cookie exists
  const sessionId = getCookie('session_id')
  console.log(sessionId)
  if (sessionId) {
    window.location.href = '/'
    return
  }

  function redirectToGoogleOAuth() {
    // Your OAuth 2.0 Client ID
    const clientId = env_var.GOOGLE_CLIENT_ID

    // The redirect URI
    const redirectUri = env_var.GOOGLE_REDIRECT_URI // Replace with your actual redirect URI

    // The scopes you're requesting access to
    const scope = 'email profile openid'

    // Build the URL for Google's OAuth 2.0 authorization endpoint
    const authorizationUrl =
      `https://accounts.google.com/o/oauth2/v2/auth?` +
      `scope=${encodeURIComponent(scope)}&` +
      `response_type=code&` +
      `client_id=${clientId}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `state=state_parameter_passthrough_value`

    // Redirect the user to the Google authorization page
    window.location.href = authorizationUrl
  }

  function loginWithAuthCode(authorizationCode) {
    $.ajax({
      url: '/google-login/',
      method: 'POST',
      data: JSON.stringify({ code: authorizationCode }),
      contentType: 'application/json',
      success: function (response) {
        console.log(response)
        if (response.session_id) {
          console.log('Login successful!')
          // set session id to cookies
          document.cookie = `session_id=${response.session_id}; path=/`
          window.location.href = '/' // Redirect after login
        } else {
          alert('Login failed!')
        }
      },
      error: function (response) {
        console.log(response)
      },
    })
  }

  // Trigger Google login when the button is clicked
  $('#google-login-btn').on('click', function () {
    console.log('Google login clicked')
    console.log(window.location.origin)
    redirectToGoogleOAuth()
  })

  // Check if the URL contains an authorization code
  // If it does, log the user in
  const urlParams = new URLSearchParams(window.location.search)
  const authorizationCode = urlParams.get('code')
  if (authorizationCode) {
    loginWithAuthCode(authorizationCode)
    console.log(authorizationCode)
  }

  const $signupCont = $('#signup-container')
  const $otpCont = $('#otp-verification')
  let email = undefined
  $otpCont.hide()

  $('#signup-form').on('submit', function (event) {
    event.preventDefault()
    const formData = {
      fullname: $('#fullname').val(),
      email: $('#email').val(),
      password: $('#password').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
    }
    $.ajax({
      url: '/api/user-profile/',
      method: 'POST',
      data: JSON.stringify(formData),
      contentType: 'application/json',
      headers: {
        'X-CSRFToken': formData.csrfmiddlewaretoken,
      },
      success: function (response) {
        $('.success-drop-down').text('Success:) redireting to otp verification')
        $('.success-drop-down').css('display', 'flex')
        setTimeout(() => {
          $('.success-drop-down').css('display', 'none')
          $signupCont.hide()
          $otpCont.show()
          email = formData.email
          $('.otp-email').text(`OTP sent to ${email}`)
        }, 1000)
      },
      error: function (response) {
        let error_message = ''
        if (response.responseJSON) {
          // as responseJSON contain errors of different fields in field: array(string);
          for (const key in response.responseJSON) {
            error_message += `${key}: ${response.responseJSON[key] + '\n'}`
          }
        } else {
          error_message = 'An unexpected error occurred.'
        }
        $('.error-message').text(error_message)
      },
    })
  })

  $('#otp-form').on('submit', function (event) {
    event.preventDefault()
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
        'X-CSRFToken': formData.csrfmiddlewaretoken,
      },
      success: function (response) {
        $('.success-drop-down').text(
          'Email verified successfully. redirecting to sign-in page.'
        )
        $('.success-drop-down').css('display', 'flex')
        setTimeout(() => {
          $('.success-drop-down').css('display', 'none')
          // redirect to home page
          window.location.href = '/signin/'
        }, 1000)
      },
      error: function (response) {
        error_message = ''
        if (response.responseJSON) {
          // as responseJSON contain errors of different fields in field: array(string);
          for (const key in response.responseJSON) {
            error_message += `${key}: ${response.responseJSON[key] + '\n'}`
          }
        } else {
          error_message = 'An unexpected error occurred.'
        }
        $('.error-message').text(error_message)
      },
    })
  })
})
