import { getCookie } from './assets.js'
import * as app_states from './app_states.js'

let ws

function connectWebSocket() {
  // Create a new WebSocket connection to the Tornado server with user ID
  const userId = app_states.userId

  // Create WebSocket connection
  const wsHost = env_var.TORNADO_HOSTNAME
  ws = new WebSocket(`${wsHost}/ws/chat?user_id=${userId}`)

  ws.onopen = function () {
    console.log('WebSocket connection opened')
  }

  ws.onmessage = function (event) {
    // Handle incoming messages from the WebSocket server
    const message = JSON.parse(event.data)
    console.log('Received message:', message)
    // Update the chat UI with the new message
    if (
      message.sender.toString() === app_states.selectedContactId.toString() &&
      message.receiver.toString() === app_states.userId.toString()
    ) {
      console.log('Received message:', message)
      app_states.messages.push(message)
      rerender_msg_view()
    }
  }

  ws.onclose = function () {
    console.log('WebSocket connection closed')
  }

  ws.onerror = function (error) {
    console.log('WebSocket error:', error)
  }
}

function sendMessageToWebSocket(message) {
  // Send a message to the WebSocket server
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message))
  } else {
    console.log('WebSocket is not open')
  }
}

function rerender_msg_view() {
  // rerender the mes_view using the app_state message list
  const msgList = app_states.messages
  const chatBody = $('.chat-body')
  chatBody.empty()
  msgList.forEach((message) => {
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
  })
  // scroll to bottom
  $('.chat-body').scrollTop($('.chat-body')[0].scrollHeight)
}

function render_msg_view() {
  // reads the app_state and rerenders the message view

  // check if user is logged in
  if (!app_states.isLoggedin) {
    window.location.href = '/signin/'
    return
  }

  // check if selected contact id is -1 and screen width is less than 600
  const screenWidth = $(window).width()
  const isSmallScreen = screenWidth < 600
  if (isSmallScreen) {
    if (app_states.selectedContactId === -1) {
      $('.mainbox').removeClass('mainbox-fullscreen')
      $('.sidebar').addClass('sidebar-fullscreen')
    } else {
      $('.sidebar').removeClass('sidebar-fullscreen')
      $('.mainbox').addClass('mainbox-fullscreen')
    }
  } else {
    $('.mainbox').removeClass('mainbox-fullscreen')
    $('.sidebar').removeClass('sidebar-fullscreen')
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
      rerender_msg_view()
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
        // Append the actual last message from the contact if available
        if (contact.last_message) {
          details.append($('<p>').text(contact.last_message))
        }
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
  $('.mainbox .welcome-page').hide()
  const contactId = $(this).attr('id')
  app_states.setSelectedContactId(contactId)
  render_msg_view()
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
      // Create a message object and send it to the WebSocket server
      const wsMessage = {
        sender: app_states.userId,
        receiver: app_states.selectedContactId,
        content: message,
      }
      sendMessageToWebSocket(wsMessage)
      app_states.messages.push(response)
      render_msg_view()
      $('#message-box').val('')
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

function onSidebarToggleClick() {
  const sidebar = $('.sidebar')
  const screenWidth = $(window).width()
  const isSmallScreen = screenWidth < 600

  const SIDEBAR_DEFAULT = 'sidebar'
  const SIDEBAR_FLOAT = 'sidebar sidebar-float'
  const SIDEBAR_COLLAPSE = 'sidebar sidebar-collapse'

  const currentClass = sidebar.attr('class')

  if (isSmallScreen) {
    // Toggle between float and collapse for small screens
    if (currentClass.includes('sidebar-float')) {
      sidebar.attr('class', SIDEBAR_COLLAPSE)
    } else if (currentClass.includes('sidebar-collapse')) {
      sidebar.attr('class', SIDEBAR_DEFAULT)
    } else {
      sidebar.attr('class', SIDEBAR_COLLAPSE)
    }
  } else {
    // Toggle between default and collapse for larger screens
    if (currentClass.includes('sidebar-collapse')) {
      sidebar.attr('class', SIDEBAR_DEFAULT)
    } else {
      sidebar.attr('class', SIDEBAR_COLLAPSE)
    }
  }
}

function onToggleMagicSidebar() {
  const $magicSidebar = $('.magic-sidebar')
  if ($magicSidebar.css('display') === 'none') {
    $magicSidebar.css('display', 'flex')
    $('.mask').show()
  } else {
    $magicSidebar.css('display', 'none')
    $('.mask').hide()
  }
}

function onClickBackToContacts() {
  app_states.setSelectedContactId(-1)
  render_msg_view()
}

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

    const username = app_states.userEmail.split('@')[0]
    $('#username').text(username)

    rerender_contacts_view()
    render_msg_view()

    connectWebSocket()

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

    $('.left-list .one').on('click', onSidebarToggleClick)

    $('.toggle-magic-sidebar').on('click', onToggleMagicSidebar)

    $('.logout').on('click', onLogoutClick)

    $('.back-to-contact-list').on('click', onClickBackToContacts)

    // An event listener that will triger of change of widge of body
    $(window).on('resize', function () {
      render_msg_view()
    })
  })
})
