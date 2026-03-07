/**
 * @typedef {Object} User
 * @property {number} id - User ID
 * @property {string} email - User email
 * @property {string} full_name - User full name
 * @property {string} [avatar] - User avatar URL
 */

/**
 * @typedef {Object} Contact
 * @property {number} id - Contact ID
 * @property {string} email - Contact email
 * @property {string} full_name - Contact full name
 * @property {string} [avatar] - Contact avatar URL
 * @property {string} [last_message] - Last message content
 * @property {string} [last_message_time] - Last message timestamp
 */

/**
 * @typedef {Object} Message
 * @property {number} id - Message ID
 * @property {string} content - Message content
 * @property {number} sender_id - Sender user ID
 * @property {number} receiver_id - Receiver user ID
 * @property {string} timestamp - Message timestamp
 * @property {boolean} is_read - Whether the message is read
 */

/**
 * @typedef {Object} AuthResponseData
 * @property {User} user - User information
 * @property {string} access - Access token
 * @property {string} refresh - Refresh token
 */

/**
 * @typedef {Object} SignInCredentials
 * @property {string} email - User email
 * @property {string} password - User password
 */

/**
 * @typedef {Object} SignUpData
 * @property {string} full_name - User full name
 * @property {string} email - User email
 * @property {string} password - User password
 */

/**
 * @typedef {Object} MessageData
 * @property {number} receiver_id - Receiver user ID
 * @property {string} content - Message content
 */

export {};