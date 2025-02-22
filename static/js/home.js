import { getCookie } from './assets.js'

$(function () {
  const sessionId = getCookie('session_id')
  if (!sessionId) {
    window.location.href = '/signin/'
    return
  }

  $.ajax({
    url: 'api/sign-in/',
    method: 'GET',
    headers: {
      'session-id': sessionId,
    },
    success: function (response) {
      console.log('User profile:', response)
      const userDetails = $('<p>')
        .attr('id', 'user-details')
        .text(`Logged in as: ${response.email}`)
      const logoutButton = $('<button>')
        .attr('id', 'logout-button')
        .text('Logout')
      $('.column-middle').append(userDetails, logoutButton)

      $('#logout-button').click(function () {
        document.cookie = 'session_id=; Max-Age=0; path=/;'
        window.location.href = '/signin/'
      })
    },
    error: function () {
      // Delete session ID from cookies
      document.cookie = 'session_id=; Max-Age=0; path=/;'
      window.location.href = '/signin/'
    },
  })
})
