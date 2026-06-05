const conversationsEl = document.getElementById('seller-conversations-data');
let conversations = [];
try {
  conversations = conversationsEl ? JSON.parse(conversationsEl.textContent || '[]') : [];
} catch (e) {
  conversations = [];
}

let currentCustomer = null;

function renderConversations() {
  const list = document.getElementById('conversationsList');
  if (!list) return;
  list.innerHTML = '';

  let totalUnread = 0;

  conversations.forEach(conv => {
    totalUnread += conv.customer.unread;

    const item = document.createElement('div');
    item.className = `p-4 border-b hover:bg-gray-50 cursor-pointer transition ${conv.customer.unread > 0 ? 'bg-blue-50' : ''}`;
    item.onclick = () => openChat(conv);

    item.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-blue-900 text-white rounded-full flex items-center justify-center font-bold text-lg">
            ${conv.customer.avatar}
          </div>
          <div>
            <h4 class="font-bold text-gray-800">${conv.customer.name}</h4>
            <p class="text-sm text-gray-600 truncate w-40">${conv.customer.lastMsg}</p>
          </div>
        </div>
        <div class="text-right">
          <p class="text-xs text-gray-500">${conv.customer.time}</p>
          ${conv.customer.unread > 0 ? `<span class="bg-red-600 text-white text-xs rounded-full px-2 py-1 mt-1 inline-block">${conv.customer.unread}</span>` : ''}
        </div>
      </div>
    `;
    list.appendChild(item);
  });

  const badge = document.getElementById('totalBadge');
  if (badge) {
    if (totalUnread > 0) {
      badge.textContent = totalUnread;
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }
  }
}

function openChat(conv) {
  currentCustomer = conv;

  if (!document.getElementById('chatWith') || !document.getElementById('messagesContainer')) {
    return;
  }

  // Desktop
  document.getElementById('chatWith').textContent = conv.customer.name;
  renderMessages(conv.messages);
  document.getElementById('chatArea').classList.remove('hidden');

  // Mobile
  document.getElementById('mobileChatName').textContent = conv.customer.name;
  document.getElementById('mobileMessages').innerHTML = document.getElementById('messagesContainer').innerHTML;
  document.getElementById('mobileChat').classList.remove('hidden');

  // Mark as read
  conv.customer.unread = 0;
  renderConversations();
}

function backToList() {
  document.getElementById('mobileChat')?.classList.add('hidden');
}

function renderMessages(messages) {
  const container = document.getElementById('messagesContainer');
  const mobileContainer = document.getElementById('mobileMessages');
  if (!container) return;
  const html = messages.map(msg => `
    <div class="mb-4 flex ${msg.sender === 'seller' ? 'justify-end' : 'justify-start'}">
      <div class="${msg.sender === 'seller' ? 'bg-blue-900 text-white' : 'bg-gray-200 text-gray-800'} px-5 py-3 rounded-2xl max-w-xs">
        <p>${msg.text}</p>
        <p class="text-xs opacity-70 mt-1">${msg.time}</p>
      </div>
    </div>
  `).join('');

  container.innerHTML = html || '<p class="text-center text-gray-500">Start the conversation...</p>';
  if (mobileContainer) mobileContainer.innerHTML = container.innerHTML;
  container.scrollTop = container.scrollHeight;
}

function sendMessage() {
  const input = document.getElementById('messageInput');
  const mobileInput = document.getElementById('mobileInput');
  if (!input && !mobileInput) return;
  const text = (input?.value || '').trim() || (mobileInput?.value || '').trim();
  if (!text || !currentCustomer) return;

  const newMsg = {
    text: text,
    sender: "seller",
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };

  currentCustomer.messages.push(newMsg);
  currentCustomer.customer.lastMsg = "You: " + text;
  currentCustomer.customer.time = "Just now";

  renderMessages(currentCustomer.messages);
  renderConversations();

  if (input) input.value = '';
  if (mobileInput) mobileInput.value = '';
}

// Enter key to send
document.getElementById('messageInput')?.addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });
document.getElementById('mobileInput')?.addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });

// Start
renderConversations();