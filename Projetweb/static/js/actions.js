document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("click", function (e) {
        // DELETE MESSAGE
        if (e.target.classList.contains("delete-msg-btn")) {
            const messageId = e.target.dataset.messageId;
            deleteMessage(messageId);
        }

        // BAN USER
        if (e.target.classList.contains("ban-btn")) {
            const userId = e.target.dataset.userId;
            const roomId = document.getElementById("messages-container").dataset.roomId;
            banUser(userId, roomId);
        }
    });
    // ===== VARIABLES =====
    let lastMessagesCount = 0;
    const emojiBtn = document.getElementById("emoji-btn");
    const emojiPicker = document.getElementById("emoji-picker");
    const messageInput = document.getElementById("message-input");

    // ===== EMOJI PICKER =====
    if (emojiBtn && emojiPicker && messageInput) {
        emojiBtn.addEventListener("click", e => {
            e.stopPropagation();
            console.log("Emoji button clicked");
            emojiPicker.classList.toggle("show");
        });

        emojiPicker.addEventListener("click", e => e.stopPropagation());

        document.querySelectorAll(".emoji").forEach(emoji => {
            emoji.addEventListener("click", () => {
                messageInput.value += emoji.textContent;
                messageInput.focus();
                emojiPicker.classList.remove("show");
            });
        });

        document.addEventListener("click", () => emojiPicker.classList.remove("show"));
    }

    // ===== SEND MESSAGE =====
    const sendForm = document.getElementById('send-message-form');
    if (sendForm) {
        sendForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const input = document.getElementById('message-input');
            const messageText = input.value;
            if (!messageText.trim()) return;

            fetch(sendForm.action, {
                method: 'POST',
                body: new FormData(sendForm),
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const messagesContainer = document.getElementById('messages-container');
                    if (!messagesContainer) return;
                    messagesContainer.innerHTML += `
                        <div class="message message-sent">
                            <div class="message-header">
                                <strong class="message-author">${data.author}</strong>
                                <span class="message-time">${data.timestamp}</span>
                            </div>
                            <div class="message-content">${data.content}</div>
                        </div>
                    `;
                    input.value = '';
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            })
            .catch(err => { console.error("Erreur:", err); sendForm.submit(); });
        });
    }

    // ===== FETCH NEW MESSAGES =====
    function checkNewMessages() {
        const container = document.getElementById('messages-container');
        const roomId = container?.dataset.roomId;
        if (!roomId) return;

        fetch(`/chat/api/messages/${roomId}/`)
            .then(res => res.json())
            .then(data => {
                if (!container) return;
                if (data.messages.length === lastMessagesCount) return;
                container.innerHTML = '';
                data.messages.forEach(msg => {
                    const messageClass = msg.author === container.dataset.currentUser ? 'message-sent' : 'message-received';
                    container.innerHTML += `
                        <div class="message ${messageClass}">
                            <div class="message-header">
                                <strong class="message-author">${msg.author}</strong>
                                <span class="message-time">${msg.time}</span>
                            </div>
                            <div class="message-content">${msg.content}</div>
                        </div>
                    `;
                });
                container.scrollTop = container.scrollHeight;
                lastMessagesCount = data.messages.length;
            });
    }
    setInterval(checkNewMessages, 3000);
    checkNewMessages();

    // ===== ADMIN FUNCTIONS =====
    window.deleteMessage = function(messageId) {
        if (!confirm("Supprimer ce message ?")) return;
        fetch(`/chat/delete-message/${messageId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": window.CSRF_TOKEN,
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) location.reload();
            else alert("Erreur : permission refusée");
        });
    };

    document.addEventListener("click", function(e) {
        if (e.target.classList.contains("ban-btn")) {
            const userId = e.target.dataset.userId;
            banUser(userId, currentRoomId); // <-- roomId depuis variable JS
        }
    });

    window.banUser = function(userId, roomId) {
        if (!confirm("Bannir cet utilisateur du salon ?")) return;
        fetch(`/chat/ban-user/${roomId}/${userId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": window.CSRF_TOKEN,
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) { alert("Utilisateur banni"); location.reload(); }
            else { alert("Erreur : permission refusée"); }
        });
    };
});
