function toggleChat() {
    const chatBox = document.getElementById('chat-box');
    chatBox.classList.toggle('chat-box-visible');
    chatBox.classList.toggle('chat-box-hidden');
}

const chatIcon = document.getElementById('chat-icon');
const message1 = document.getElementById('message-1');
const message2 = document.getElementById('message-2');

chatIcon.addEventListener('mouseenter', () => {
    const randomMessage = Math.random() < 0.5 ? message1 : message2; // Randomly choose one of the messages

    // Show the selected message
    randomMessage.style.display = 'block';
    randomMessage.style.opacity = '1'; // Fade in effect

    // Keep it visible for 1.5 seconds
    setTimeout(() => {
        randomMessage.style.opacity = '0'; // Fade out effect
        setTimeout(() => {
            randomMessage.style.display = 'none'; // Hide after fade out
        }, 300); // Time for fade out
    }, 1500); // Time to keep the message visible
});

chatIcon.addEventListener('mouseleave', () => {
    // Hide both messages immediately when leaving hover
    message1.style.opacity = '0';
    message2.style.opacity = '0';

    setTimeout(() => {
        message1.style.display = 'none';
        message2.style.display = 'none';
    }, 300);  // Give time for fade out
});

// Function to handle sending messages
function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    const messagesDiv = document.getElementById('messages');

    if (userInput.trim()) {
        // Append user's message
        const userMessage = document.createElement('div');
        userMessage.textContent = userInput;
        userMessage.className = 'user-message';
        messagesDiv.appendChild(userMessage);

        // Simulate bot response (replace this with actual bot logic)
        const botResponse = document.createElement('div');
        botResponse.textContent = "Bot: " + userInput;  // Temporary bot response
        botResponse.className = 'bot-message';
        messagesDiv.appendChild(botResponse);

        // Clear the input field
        document.getElementById('user-input').value = '';
    }
}
