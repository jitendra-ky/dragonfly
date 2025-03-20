import { getCookie } from './assets.js'
import * as app_states from './app_states.js'

function rerender_msg_view() {
  // reads the app_state and rerenders the message view

  // check if user is logged in
  if (!app_states.isLoggedin) {
    window.location.href = '/signin/'
    return
  }

  // check other validation
  if (
    app_states.selectedContactId === -1 || // check if a contact is selected
    app_states.sessionId === '' || // check if session id is present
    app_states.userId === -1 || // check if user id is present
    app_states.selectedContactId === -1 || // check if a contact is selected
    app_states.contacts.length === 0 // check if contacts are present
  ) {
    return
  }

  // update the contact name
  const selectedContact = app_states.contacts.find(
    (contact) => contact.id.toString() === app_states.selectedContactId
  )
  console.log('Selected contact:', selectedContact)
  $('.mainbox .chat-header h4').text(selectedContact.fullname)
  $('.mainbox .chat-header p').text(selectedContact.email)

  // get the messages
  $.ajax({
    url: 'api/messages/',
    method: 'GET',
    headers: {
      'session-id': app_states.sessionId,
      receiver: app_states.selectedContactId,
    },
    success: function (response) {
      console.log('Messages:', response)
      app_states.setMessages(response)
      // render the messages
      const chatBody = $('.chat-body')
      chatBody.empty()
      response.forEach((message) => {
        const messageElement = $('<div>').addClass(
          message.sender === app_states.userId
            ? 'chat-message chat-message-sent'
            : 'chat-message chat-message-received'
        )
        const profile = $('<div>').addClass('chat-message-profile')
        const content = $('<div>').addClass('chat-message-content')
        content.append($('<p>').text(message.content))
        messageElement.append(profile, content)
        chatBody.append(messageElement)
        // scroll to bottom
        chatBody.scrollTop(chatBody[0].scrollHeight)
      })
    },
    error: function (response) {
      console.log('Error:', response)
    },
  })
}

function rerender_contacts_view() {
  // reads the app_state and rerenders the contacts view

  // check if user is logged in
  if (!app_states.isLoggedin) {
    window.location.href = '/signin/'
    return
  }

  // check other validation
  if (app_states.sessionId === '' || app_states.userId === -1) {
    return
  }

  // get the contacts
  $.ajax({
    url: 'api/contacts/',
    method: 'GET',
    headers: {
      'session-id': app_states.sessionId,
    },
    success: function (response) {
      console.log('Contacts:', response)
      app_states.setContacts(response)
      const chatList = $('.chat-list ul')
      chatList.empty()
      response.forEach((contact) => {
        const contactElement = $('<li>')
          .addClass('chat-item renders-chat-view')
          .attr('id', contact.id)
          .on('click', onClickContact)
        const contactContent = $('<div>').addClass('chat-item-content')
        const profile = $('<div>').addClass('chat-item-profile')
        const details = $('<div>').addClass('chat-item-details')
        details.append($('<h4>').text(contact.email))
        details.append($('<p>').text('Hey, how are you?'))
        contactContent.append(profile, details)
        contactElement.append(contactContent)
        chatList.append(contactElement)
      })
    },
    error: function (response) {
      console.log('Error:', response)
    },
  })
}

function onClickContact() {
  // on click of a contact, set the selectedContactId and rerender the message view
  const contactId = $(this).attr('id')
  app_states.setSelectedContactId(contactId)
  rerender_msg_view()
}

function onClickSend() {
  // on click of send button, send the message and rerender the message view
  const message = $('#message-box').val()
  console.log('Sending message:', message)
  $.ajax({
    url: 'api/messages/',
    method: 'POST',
    headers: {
      'session-id': app_states.sessionId,
      'X-CSRFToken': getCookie('csrftoken'),
    },
    data: {
      content: message,
      receiver: app_states.selectedContactId,
    },
    success: function (response) {
      console.log('Message sent:', response)
      app_states.messages.push(response)
      rerender_msg_view()
      $('#message-box').val('')
      // scroll to bottom
      $('.chat-body').scrollTop($('.chat-body')[0].scrollHeight)
    },
    error: function (response) {
      console.log('Error:', response)
    },
  })
}

function onLogoutClick() {
  // on click of logout button, logout the user
  document.cookie = 'session_id=; Max-Age=0; path=/;'
  window.location.href = '/signin/'
}

function sendMessage(contactId, messageContent, callback) {
  // send message to a contact
  console.log('Sending message:', messageContent)
  $.ajax({
    url: 'api/messages/',
    method: 'POST',
    headers: {
      'session-id': app_states.sessionId,
      'X-CSRFToken': getCookie('csrftoken'),
    },
    data: {
      content: messageContent,
      receiver: contactId,
    },
    success: function (response) {
      console.log('Message sent:', response)
      callback(true, response)
    },
    error: function (response) {
      console.log('Error:', response)
      callback(false, response)
    },
  })
}

function populateNewContactList() {
  // fetch all users and populate the select box
  $.ajax({
    url: 'api/all-users/',
    method: 'GET',
    success: function (response) {
      const userSelect = $('#user-select')
      response.forEach((user) => {
        const option = $('<option>').val(user.id).text(user.email)
        userSelect.append(option)
      })
    },
    error: function (response) {
      console.log('Error:', response)
    },
  })
}

function onsendMessageToNewUserClick() {
  const userId = $('#user-select').val()
  const messageContent = $('#new-message-content').val()
  if (!userId || !messageContent) {
    alert('Please select a user and type a message.')
    return
  }

  sendMessage(userId, messageContent, function (success, response) {
    if (success) {
      alert('Message sent successfully!')
      $('#new-message-modal').hide()
      // add this new contact in contacts list
      rerender_contacts_view()
    } else {
      console.log('Error sending message')
    }
  })
}
/*
function onSidebarToggleClick() {
  const sidebar = $('.sidebar')
  const screenWidth = $(window).width()
  console.log('sidebar:', sidebar)
  console.log('screenWidth:', screenWidth)
  const currentClass = sidebar.attr('class')
  console.log('currentClass:', currentClass)

  if (screenWidth < 600) {
    if (currentClass.includes('sidebar-float')) {
      sidebar.removeClass('sidebar-float')
      sidebar.addClass('sidebar sidebar-collapse')
    } else if (currentClass.includes('sidebar-collapse')) {
      sidebar.removeClass('sidebar-collapse')
      sidebar.addClass('sidebar sidebar-float')
    } else {
      sidebar.addClass('sidebar-collapse')
    }
  } else {
    if (currentClass.includes('sidebar')) {
      sidebar.removeClass('sidebar')
      sidebar.addClass('sidebar sidebar-collapse')
    } else if (currentClass.includes('sidebar-collapse')) {
      sidebar.removeClass('sidebar-collapse')
      sidebar.addClass('sidebar')
    } else {
      sidebar.addClass('sidebar sidebar-collapse')
    }
  }
}
*/
$(function () {
  console.log('home.js loaded')

  app_states.updateLoggedInUserState(() => {
    console.log('app_states:', app_states)
    const sessionId = app_states.sessionId
    if (!sessionId) {
      window.location.href = '/signin/'
      return
    }
    console.log(app_states.sessionId)
    console.log(app_states.userEmail)
    const $userDetails = $('<p>')
      .attr('id', 'user-details')
      .text(`${app_states.userEmail}`)
    const $logoutButton = $('<button>')
      .attr('id', 'logout-button')
      .text('Logout')
      .on('click', onLogoutClick)
    $('.right-list ul').prepend($userDetails, $logoutButton)
    console.log('add user details and logout button')

    rerender_contacts_view()

    $('#chat-msg-send-btn').on('click', onClickSend)

    $('#new-message-btn').click(function () {
      populateNewContactList()
      $('#new-message-modal').show()
    })

    $('.close').click(function () {
      $('#new-message-modal').hide()
    })

    $('#send-new-message-btn').click(function () {
      onsendMessageToNewUserClick()
    })

    // $('#sidebar-toggle').on('click', onSidebarToggleClick)
  })
})
