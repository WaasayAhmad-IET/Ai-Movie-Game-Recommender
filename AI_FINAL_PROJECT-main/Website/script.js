document.addEventListener("DOMContentLoaded", () => {
    // Load movies and games
    function loadItems(items, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        items.forEach(item => {
            const div = document.createElement('div');
            div.classList.add('grid-item');
            div.innerHTML = `<img src="${item.img}" alt="${item.title}"><h3>${item.title}</h3>`;
            container.appendChild(div);
        });
    }
    loadItems(movies, 'movie-list');
    loadItems(games, 'game-list');

    // Search
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase();
        const filteredMovies = movies.filter(m => m.title.toLowerCase().includes(query));
        const filteredGames = games.filter(g => g.title.toLowerCase().includes(query));
        loadItems(filteredMovies, 'movie-list');
        loadItems(filteredGames, 'game-list');
    });

    // Dark mode
    const toggleBtn = document.getElementById('toggle-mode');
    toggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        toggleBtn.textContent = document.body.classList.contains('dark') ? '☀️' : '🌙';
    });

    // Chatbot toggle
    const chatbotLogo = document.getElementById('chatbot-logo');
    const chatbotPopup = document.getElementById('chatbot-popup');
    const closeChat = document.getElementById('close-chat');

    chatbotLogo.addEventListener('click', () => { chatbotPopup.style.display = 'flex'; });
    closeChat.addEventListener('click', () => { chatbotPopup.style.display = 'none'; });

    // Chatbot messages
    const chatBox = document.getElementById('chat-box');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');

    function addMessage(sender, text) {
        const msg = document.createElement('div');
        msg.textContent = text;
        msg.classList.add(sender === 'You' ? 'user-msg' : 'bot-msg');
        chatBox.appendChild(msg);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Mood-based recommendations
    chatSend.addEventListener('click', async () => {
    const userText = chatInput.value.trim();
    if(!userText) return;

    // Show user's message
    addMessage("You", userText);

    // Call your FastAPI chatbot API
    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: userText })
        });

        if(!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        
        // Display bot response
        // Assuming your FastAPI returns: { "recommendations": [ {"title": "...", "genre": "..."}, ... ] }
        let botReply = "";
        if(data.recommendations && data.recommendations.length > 0){
            botReply = data.recommendations.map(r => `${r.title} (${r.genre})`).join(", ");
        } else {
            botReply = "Sorry, I couldn't find any recommendations.";
        }

        addMessage("Bot:", botReply);

    } catch (err) {
        console.error(err);
        addMessage("Bot", "Oops! Something went wrong while contacting the server.");
    }

    chatInput.value = '';
});

    
});
