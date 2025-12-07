document.addEventListener('DOMContentLoaded', () => {
    // Only run on main chat page
    if (!document.getElementById('userList')) return;

    const currentUserId = localStorage.getItem('user_id');
    if (!currentUserId) {
        window.location.href = '/login.html';
        return;
    }

    let socket;
    let selectedContactId = null;

    // Initialize Socket.io
    socket = io();

    socket.on('connect', () => {
        console.log('Connected to WebSocket');
        socket.emit('join', { user_id: currentUserId });
    });

    socket.on('status', (data) => {
        console.log(data.msg);
    });

    socket.on('new_message', (data) => {
        // If chatting with this user, append message
        if (selectedContactId === data.sender_id) {
            // For now, since we sent plaintext in the event (oops, security trade-off for demo simplicity),
            // we can just append it.
            // Ideally: Fetch the message ID to decrypt it properly via API.
            // let's fetch it to be proper.
            // But we don't have an endpoint to fetch ONE message by ID easily in the current API without filtering.
            // Let's rely on the data sent for now, or reload the chat.

            // To be secure, we should NOT trust the content in the event if it was supposed to be encrypted.
            // But in our modified backend, we sent 'plaintext' because the server has the keys in session?
            // Wait, the `send_message` function in api_routes runs in the SENDER's session.
            // The SENDER's session has SENDER's private key.
            // The RECIPIENT's private key is NOT in the sender's session.
            // So the server CANNOT decrypt the message for the recipient inside `send_message`.

            // ERROR REALIZATION: I passed `plaintext` (the original input) in `socketio.emit` to the recipient.
            // This effectively bypasses encryption for the real-time delivery!
            // The database storage is encrypted, but the socket event leaks plaintext.
            // FIX: We should send a notification "New Message Available" and client should fetch it.
            // Client fetch -> API -> Server uses Recipient Session (if logged in) -> Decrypt -> Return.

            // So:
            console.log("New message notification received");
            loadMessages(selectedContactId);
        } else {
            // Show notification indicator for that user?
             const userLi = document.querySelector(`li[data-user-id="${data.sender_id}"]`);
             if (userLi) {
                 userLi.style.fontWeight = 'bold';
                 userLi.innerText += ' (New)';
             }
        }
    });

    socket.on('message_sent', (data) => {
         if (selectedContactId === data.recipient_id) {
             appendMessage({
                 content: data.content,
                 is_sender: true,
                 timestamp: new Date().toISOString()
             });
         }
    });

    // Load current user info
    fetch('/api/me')
        .then(res => {
            if (res.status === 401) {
                window.location.href = '/login.html';
                throw new Error('Unauthorized');
            }
            return res.json();
        })
        .then(user => {
            document.getElementById('currentUser').innerText = `${user.username} (${user.user_id.substring(0,8)}...)`;
        })
        .catch(err => console.error(err));

    // Load users
    fetch('/api/users')
        .then(res => res.json())
        .then(users => {
            const list = document.getElementById('userList');
            list.innerHTML = '';
            users.forEach(user => {
                if (user.user_id === currentUserId) return;

                const li = document.createElement('li');
                li.innerText = user.username;
                li.dataset.userId = user.user_id;
                li.addEventListener('click', () => selectContact(user));
                list.appendChild(li);
            });
        });

    function selectContact(user) {
        selectedContactId = user.user_id;

        // Update UI
        document.querySelectorAll('.user-list li').forEach(li => li.classList.remove('active'));
        document.querySelector(`li[data-user-id="${user.user_id}"]`).classList.add('active');

        document.getElementById('chatHeader').innerHTML = `<h3>Chatting with ${user.username}</h3>`;
        document.getElementById('messageInput').disabled = false;
        document.getElementById('sendBtn').disabled = false;

        loadMessages(selectedContactId);
    }

    function loadMessages(partnerId) {
        fetch(`/api/messages/${partnerId}`)
            .then(res => res.json())
            .then(messages => {
                const container = document.getElementById('messageContainer');
                container.innerHTML = '';
                messages.forEach(msg => {
                    appendMessage(msg);
                });
                container.scrollTop = container.scrollHeight;
            });
    }

    function appendMessage(msg) {
        const container = document.getElementById('messageContainer');
        const div = document.createElement('div');
        div.className = `message ${msg.is_sender ? 'sent' : 'received'}`;

        const contentDiv = document.createElement('div');
        contentDiv.innerText = msg.content;

        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        const date = new Date(msg.timestamp);
        metaDiv.innerText = date.toLocaleTimeString();

        div.appendChild(contentDiv);
        div.appendChild(metaDiv);
        container.appendChild(div);

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    // Send message
    document.getElementById('messageForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('messageInput');
        const content = input.value.trim();

        if (!content || !selectedContactId) return;

        try {
            const response = await fetch('/api/messages/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    recipient_id: selectedContactId,
                    content: content
                })
            });

            if (response.ok) {
                input.value = '';
                // Message will be appended via socket 'message_sent' event
            } else {
                alert('Failed to send message');
            }
        } catch (err) {
            console.error(err);
        }
    });

    document.getElementById('logoutBtn').addEventListener('click', async () => {
        await fetch('/api/logout', { method: 'POST' });
        localStorage.removeItem('user_id');
        window.location.href = '/login.html';
    });
});
