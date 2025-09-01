// Telegram-style Chat Interface JavaScript
// This file is now integrated into the chat_interface.html template
// All functionality has been moved to the template for better integration

// Legacy support for old chat interface
if (window.location.pathname.includes('/chat/')) {
    const urlParts = window.location.pathname.split('/');
    const chat_id = urlParts[urlParts.length - 1];
    
    if (chat_id && !isNaN(chat_id)) {
        // Redirect to new chat interface
        window.location.href = '/profile/chats/';
    }
}