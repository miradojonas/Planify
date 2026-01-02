// Gestion du chat en temps réel
class ChatManager {
    constructor(chatId) {
        this.chatId = chatId;
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendMessage');
        this.isTyping = false;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.scrollToBottom();
        this.startPolling();
    }
    
    bindEvents() {
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        if (this.messageInput) {
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
            
            this.messageInput.addEventListener('input', () => {
                this.handleTyping();
            });
        }
    }
    
    async sendMessage() {
        const content = this.messageInput?.value.trim();
        if (!content || !this.chatId) return;
        
        // Ajouter le message immédiatement pour un meilleur UX
        this.addMessage(content, true);
        this.messageInput.value = '';
        
        try {
            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    chat_id: this.chatId,
                    content: content
                })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                console.error('Failed to send message');
                // Optionnel: retirer le message en cas d'erreur
            }
        } catch (error) {
            console.error('Error sending message:', error);
            Plinify.showNotification('Erreur lors de l\'envoi du message', 'error');
        }
    }
    
    addMessage(content, isSent = false, timestamp = null) {
        if (!this.messagesContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isSent ? 'message-sent' : 'message-received'}`;
        
        const messageTime = timestamp || new Date().toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(content)}</div>
                <div class="message-time">${messageTime}</div>
            </div>
        `;
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    async loadMessages() {
        if (!this.chatId) return;
        
        try {
            const response = await fetch(`/api/chat/${this.chatId}/messages`);
            const messages = await response.json();
            
            if (this.messagesContainer) {
                this.messagesContainer.innerHTML = '';
                messages.forEach(msg => {
                    this.addMessage(
                        msg.content, 
                        msg.is_me, 
                        msg.created_at
                    );
                });
            }
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }
    
    startPolling() {
        // Polling simple pour les nouveaux messages
        setInterval(() => {
            this.checkNewMessages();
        }, 3000); // Vérifier toutes les 3 secondes
    }
    
    async checkNewMessages() {
        if (!this.chatId) return;
        
        try {
            const response = await fetch(`/api/chat/${this.chatId}/messages`);
            const messages = await response.json();
            
            // Dans une vraie app, on comparerait avec les messages existants
            // Pour cette version simplifiée, on recharge tout
            const currentMessageCount = this.messagesContainer?.children.length || 0;
            if (messages.length > currentMessageCount) {
                this.loadMessages();
            }
        } catch (error) {
            console.error('Error checking new messages:', error);
        }
    }
    
    handleTyping() {
        // Implémentation basique de l'indicateur de frappe
        // Dans une vraie app, on enverrait un événement WebSocket
        if (!this.isTyping && this.messageInput.value.length > 0) {
            this.isTyping = true;
            // Envoyer un événement "user is typing"
        } else if (this.isTyping && this.messageInput.value.length === 0) {
            this.isTyping = false;
            // Envoyer un événement "user stopped typing"
        }
    }
    
    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }
    
    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Gestion de la boîte de réception
class InboxManager {
    constructor() {
        this.conversations = [];
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.startPolling();
    }
    
    bindEvents() {
        // Gestion de la recherche
        const searchInput = document.getElementById('conversationSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterConversations(e.target.value);
            });
        }
        
        // Gestion des clics sur les conversations
        document.addEventListener('click', (e) => {
            const conversationItem = e.target.closest('.conversation-item');
            if (conversationItem) {
                const chatId = conversationItem.dataset.chatId;
                if (chatId) {
                    this.openConversation(chatId);
                }
            }
        });
    }
    
    filterConversations(searchTerm) {
        const conversationItems = document.querySelectorAll('.conversation-item');
        conversationItems.forEach(item => {
            const name = item.querySelector('.conversation-name').textContent.toLowerCase();
            const preview = item.querySelector('.conversation-preview').textContent.toLowerCase();
            const search = searchTerm.toLowerCase();
            
            if (name.includes(search) || preview.includes(search)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    openConversation(chatId) {
        window.location.href = `/chat/${chatId}`;
    }
    
    async markAsRead(chatId) {
        try {
            await fetch(`/api/chat/${chatId}/read`, {
                method: 'POST'
            });
        } catch (error) {
            console.error('Error marking as read:', error);
        }
    }
    
    startPolling() {
        // Polling pour les nouvelles conversations et messages
        setInterval(() => {
            this.checkUpdates();
        }, 5000);
    }
    
    async checkUpdates() {
        // Recharger la page pour les mises à jour simples
        // Dans une vraie app, on mettrait à jour via WebSocket
        const unreadCount = document.querySelectorAll('.unread-badge').length;
        if (unreadCount > 0) {
            // Actualiser l'indicateur de notifications
            this.updateNotificationBadge(unreadCount);
        }
    }
    
    updateNotificationBadge(count) {
        let badge = document.querySelector('.nav-notification-badge');
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'nav-notification-badge';
            const chatLink = document.querySelector('a[href*="chat"]');
            if (chatLink) {
                chatLink.appendChild(badge);
            }
        }
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le gestionnaire de chat si on est dans une conversation
    const chatId = document.body.dataset.chatId;
    if (chatId) {
        window.chatManager = new ChatManager(parseInt(chatId));
    }
    
    // Initialiser la boîte de réception si on est sur la page des messages
    if (window.location.pathname.includes('/chat') && !chatId) {
        window.inboxManager = new InboxManager();
    }
    
    // Gestion du modal nouveau chat
    const newChatModal = document.getElementById('newChatModal');
    if (newChatModal) {
        newChatModal.addEventListener('click', function(e) {
            if (e.target === this) {
                Plinify.closeModal('newChatModal');
            }
        });
    }
});

// Fonctions globales pour les templates
function openNewChatModal() {
    Plinify.openModal('newChatModal');
}

function closeNewChatModal() {
    Plinify.closeModal('newChatModal');
}

async function startNewChat() {
    const recipientSelect = document.getElementById('recipientSelect');
    const recipientId = recipientSelect?.value;
    
    if (!recipientId) {
        Plinify.showNotification('Veuillez sélectionner un destinataire', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/chat/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: parseInt(recipientId) })
        });
        
        const data = await response.json();
        
        if (data.chat_id) {
            window.location.href = `/chat/${data.chat_id}`;
        } else {
            throw new Error('No chat ID returned');
        }
    } catch (error) {
        console.error('Error starting chat:', error);
        Plinify.showNotification('Erreur lors de la création de la conversation', 'error');
    }
}