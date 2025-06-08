import { getCookie } from './assets.js'

export var selectedContactId = -1
export var selectedContactName = ''
export var userName = ''
export var userId = -1
export var userEmail = ''
export var ve = ''
export var sessionId = ''
export var isLoggedin = false
export var contacts = []
export var messages = []

export function updateLoggedInUserState(callback) {
  console.log('updateLoggedInUserState')
  const tempSessionId = getCookie('session_id')
  console.log('tempSessionId', tempSessionId)
  if (!tempSessionId) {
    sessionId = ''
    userId = -1
    userName = ''
    userEmail = ''
    if (callback) callback()
  } else {
    sessionId = tempSessionId
    isLoggedin = true

    // now get the other user details from the server
    $.ajax({
      url: '/api/sign-in/',
      method: 'GET',
      headers: {
        'session-id': sessionId,
      },
      success: function (response) {
        console.log('user details', response)
        userId = response.id
        userName = response.name
        userEmail = response.email
        ve = response.email
        if (callback) callback()
      },
      error: function (error) {
        console.log('error', error)
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

export function setSessionId(id) {
  sessionId = id
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
