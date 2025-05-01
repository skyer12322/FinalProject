const urlParts = window.location.pathname.split('/');
const chat_id = urlParts[urlParts.length - 1];  // Extract chat_id from the URL path

const chatSocket = new WebSocket(
    `ws://${window.location.host}/ws/chat/${chat_id}/`  // Use the extracted chat_id
);
chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const chatLog = document.getElementById('chat-log');
    
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `
        <div class="message">
            <div class="sender">${data.user.main_name}</div>
            <div class="content">${data.content}</div>
            <div class="time">${new Date(data.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })}</div>
        </div>
        <hr>
    `;
    chatLog.appendChild(messageElement);
};

function sendMessage() {
    const input = document.getElementById('chat-input');
    chatSocket.send(JSON.stringify({
        'content': input.value
    }));
    input.value = '';
}