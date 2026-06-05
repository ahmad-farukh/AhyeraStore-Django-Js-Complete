document.addEventListener('DOMContentLoaded', function () {
    const chatWindow = document.getElementById('chat-window');
    const chatBody = document.getElementById('chat-body');
    const input = document.getElementById('user-input');

    window.toggleChat = function () {
        if (!chatWindow) return;
        if (chatWindow.classList.contains('scale-0')) {
            chatWindow.classList.remove('scale-0');
        } else {
            chatWindow.classList.add('scale-0');
        }
    };

    function appendUserMessage(text) {
        if (!chatBody) return;
        const wrap = document.createElement('div');
        wrap.className = 'flex justify-end';
        wrap.innerHTML = `
      <div class="bg-blue-600 text-white rounded-2xl px-5 py-3 shadow-md max-w-xs">
        <p>${text}</p>
        <p class="text-xs opacity-80 mt-1 text-right">Just now</p>
      </div>
    `;
        chatBody.appendChild(wrap);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function appendBotMessage(text) {
        if (!chatBody) return;
        const wrap = document.createElement('div');
        wrap.className = 'flex items-start gap-3';
        wrap.innerHTML = `
      <div class="w-10 h-10 bg-gradient-to-r from-blue-600 to-pink-600 rounded-full flex items-center justify-center text-white flex-shrink-0">
        <i class="fas fa-robot"></i>
      </div>
      <div class="bg-white rounded-2xl px-5 py-3 shadow-md max-w-xs">
        <p class="text-gray-800">${text}</p>
        <p class="text-xs text-gray-500 mt-1">Just now</p>
      </div>
    `;
        chatBody.appendChild(wrap);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    window.sendQuick = function (key) {
        if (key === 'return') {
            appendUserMessage('Returns & Exchange');
            appendBotMessage('You can request returns from the order details page.');
            return;
        }

        if (key === 'help') {
            appendUserMessage('Help Center');
            appendBotMessage('For support, use the “Connect to Human” link below.');
            return;
        }

        appendUserMessage(String(key));
        appendBotMessage('How can I help you?');
    };

    window.sendMessage = function () {
        if (!input) return;
        const text = (input.value || '').trim();
        if (!text) return;
        input.value = '';
        appendUserMessage(text);

        appendBotMessage('Thanks! Please choose a quick action above or use the “Connect to Human” link below.');
    };
});
