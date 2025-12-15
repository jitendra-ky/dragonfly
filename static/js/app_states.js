import { getCookie } from './assets.js'

export var selectedContactId = -1
export var selectedContactName = ''
export var userName = ''
export var userId = -1
export var userEmail = ''
export var ve = ''
export var accessToken = ''
export var refreshToken = ''
export var isLoggedin = false
export var contacts = []
export var messages = []

export function updateLoggedInUserState(callback) {
  console.log('updateLoggedInUserState')
  const tempAccessToken = localStorage.getItem('access_token')
  console.log('tempAccessToken', tempAccessToken)
  if (!tempAccessToken) {
    accessToken = ''
    refreshToken = ''
    userId = -1
    userName = ''
    userEmail = ''
    if (callback) callback()
  } else {
    accessToken = tempAccessToken
    refreshToken = localStorage.getItem('refresh_token') || ''
    isLoggedin = true

    // Check if user data is already stored in localStorage
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser)
        userId = user.id
        userName = user.contact
        userEmail = user.email
        ve = user.email
        if (callback) callback()
        return
      } catch (e) {
        console.log('Error parsing stored user', e)
      }
    }

    // Fetch user details from the server if not in localStorage
    $.ajax({
      url: '/api/sign-in/',
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      success: function (response) {
        console.log('user details', response)
        userId = response.id
        userName = response.contact
        userEmail = response.email
        ve = response.email
        // Store user data for future use
        localStorage.setItem('user', JSON.stringify(response))
        if (callback) callback()
      },
      error: function (error) {
        console.log('error', error)
        // If token is invalid, clear it
        if (error.status === 401) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          accessToken = ''
          refreshToken = ''
          isLoggedin = false
        }
        if (callback) callback()
      },
    })
  }
}

export function setSelectedContactId(id) {
  selectedContactId = id
}

export function setSelectedContactName(name) {
  selectedContactName = name
}

export function setUserName(name) {
  userName = name
}

export function setUserId(id) {
  userId = id
}

export function setUserEmail(email) {
  userEmail = email
}

export function setVe(value) {
  ve = value
}

export function setAccessToken(token) {
  accessToken = token
}

export function setRefreshToken(token) {
  refreshToken = token
}

export function setIsLoggedin(status) {
  isLoggedin = status
}

export function setContacts(contactList) {
  contacts = contactList
}

export function setMessages(messageList) {
  messages = messageList
}
