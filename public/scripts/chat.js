async function getFirstMessages() {
    const [firstChat,] = document.querySelectorAll('.single_chat');
    const isReadIcon = firstChat.querySelector('i');
    isReadIcon ? isReadIcon.style.display = 'none' : null;
    const chatRoomId = firstChat.dataset.chatroomid;
    await fetchChatMessages(chatRoomId);
    firstChat.classList.add('current-chat');
}

async function fetchChatMessages(chatRoomId) {
    try {
        const response = await fetch(`/user/offermessages/${chatRoomId}`);
        const data = await response.json(); 
        console.log(data);
        renderMessages(data.messages, data.user_id);
    }catch (err) {
        console.error(err.message);
    }
}

async function updateChatroomStatus(chatRoomId) {
    try {
        const response = await fetch(`/user/chatroom/${chatRoomId}`, {
            method: 'PATCH'
        });
    }catch (err) {
        console.error(err.message);
    }
}

function otherChatsHandler() {
    const otherChats = document.querySelectorAll('.single_chat');
    otherChats.forEach((chat) => {
        const isReadIcon = chat.querySelector('i');
        chat.addEventListener('click', async (event) => {
            otherChats.forEach((chat) => chat.classList.remove('current-chat'));
            isReadIcon ? isReadIcon.style.display = 'none' : null;
            const chatRoomId = event.currentTarget.dataset.chatroomid;
            updateChatroomStatus(chatRoomId);
            event.currentTarget.classList.add('current-chat');
            await fetchChatMessages(chatRoomId);
        });   
    });
}

function renderMessages(messages, currentUserId) {
    const chatContainer = document.querySelector('.inbox_massage_wrapper');
    chatContainer.innerHTML = '';

    messages.forEach((message) => {
        const messageContainer = document.createElement('div');
        messageContainer.style.wordBreak = 'break-word';
        if (message.receiver_user_id !== currentUserId){
            messageContainer.classList.add('outgoing_msg', 'clearfix');
            const messageElement = document.createElement('div');
            messageElement.classList.add('outgoing_msg_content');
            const messageText = document.createElement('p');
            messageText.textContent = message.text_message;
            const messageTime = document.createElement('span');
            messageTime.textContent = prettyDate(message.send_at);
            messageElement.append(messageText, messageTime);
            messageContainer.appendChild(messageElement);

            chatContainer.appendChild(messageContainer);
            return;
        }
        messageContainer.classList.add('incoming_msg', 'd-flex');
        const messageImage = document.createElement('div');
        messageImage.classList.add('incoming_msg_img');
        const image = document.createElement('img');
        image.src = message.sender_user.profile_image_url ?
                    message.sender_user.profile_image_url :
                    `/public/assets/images/author-2.jpg`;
        messageImage.appendChild(image);
        const messageElement = document.createElement('div');
        messageElement.classList.add('incoming_msg_content', 'media-body');
        const messageText = document.createElement('p');
        messageText.textContent = message.text_message;
        const messageTime = document.createElement('span');
        messageTime.textContent = prettyDate(message.send_at);
        messageElement.append(messageText, messageTime);
        messageContainer.append(messageImage, messageElement);

        chatContainer.appendChild(messageContainer);
    });
}

function prettyDate(date) {
    const defaultDate = new Date(date);
    const time = defaultDate.toLocaleTimeString('en-GB', {hour: '2-digit', minute: '2-digit'});
    return time;
} 

function buildOnGoingMessage({text_message: textMessage, send_at: sendAt}) {
    const chatContainer = document.querySelector('.inbox_massage_wrapper');
    const messageContainer = document.createElement('div');
    messageContainer.style.wordBreak = 'break-word';
    messageContainer.classList.add('outgoing_msg', 'clearfix');
    const messageElement = document.createElement('div');
    messageElement.classList.add('outgoing_msg_content');
    const messageText = document.createElement('p');
    messageText.textContent = textMessage;
    const messageTime = document.createElement('span');
    messageTime.textContent = prettyDate(sendAt);
    messageElement.append(messageText, messageTime);
    messageContainer.appendChild(messageElement);

    chatContainer.appendChild(messageContainer);
}

async function sendNewMessage(event) {
    event.preventDefault();
    const currentChat = document.querySelector('.single_chat.current-chat');
    const chatRoomId = currentChat.dataset.chatroomid;
    const receiverUserId = currentChat.dataset.userid;
    const textMessage = document.querySelector('textarea[name="text_message"]'); 
    try {
        const response = await fetch(`/user/chatroom/${chatRoomId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text_message: textMessage.value,
                receiver_id: receiverUserId
                })
        });
        const data = await response.json();
        buildOnGoingMessage(data);
        console.log(data);
        textMessage.value = '';
    }catch (err) {
        console.error(err.message);
    }

    console.log(currentChat);
}

async function main() {
    const chatForm = document.getElementById('message_form');
    chatForm.addEventListener('submit', sendNewMessage)
    await getFirstMessages();
    otherChatsHandler();
}

window.addEventListener('load', main);