import api from './api';
import { API_CONFIG } from '../constants';

export const chatService = {
  async getContacts() {
    const { data } = await api.get(API_CONFIG.ENDPOINTS.CONTACTS);
    return data;
  },

  async getMessages(otherUserId) {
    console.log('Fetching messages with otherUserId:', otherUserId);
    const { data } = await api.get(API_CONFIG.ENDPOINTS.MESSAGES, {
      headers: {
        'receiver': String(otherUserId)
      }
    });
    console.log('Fetched messages:', data);
    return data;
  },

  async sendMessage(receiverId, content) {
    const messageData = { receiver: receiverId, content };
    console.log('Sending message with data:', messageData);
    const { data } = await api.post(API_CONFIG.ENDPOINTS.MESSAGES, messageData);
    console.log('Message sent successfully:', data);
    return data;
  },

  async getAllUsers() {
    const { data } = await api.get(API_CONFIG.ENDPOINTS.ALL_USERS);
    return data;
  },
};