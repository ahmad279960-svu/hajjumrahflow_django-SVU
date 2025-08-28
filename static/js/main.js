// static/js/main.js

document.addEventListener("DOMContentLoaded", function() {

    // Initialize Feather Icons
    feather.replace();

    // --- Animate cards on scroll view, excluding those with 'no-animation' class ---
    const cards = document.querySelectorAll('.card:not(.no-animation)');
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = `fadeInUp 0.6s ${entry.target.dataset.delay || '0s'} forwards`;
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.dataset.delay = `${index * 100}ms`;
        observer.observe(card);
    });
    
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);

    // --- AI Assistant Chat Logic ---
    const chatForm = document.getElementById('ai-chat-form');
    const chatInput = document.getElementById('ai-chat-input');
    const chatHistory = document.getElementById('ai-chat-history');
    // FIX: Read the URL dynamically from the body data attribute
    const aiAskUrl = document.body.dataset.aiAskUrl;

    if (chatForm && aiAskUrl) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const question = chatInput.value.trim();
            if (!question) return;

            appendMessage(question, 'user');
            chatInput.value = '';
            chatInput.focus();

            const thinkingDiv = appendMessage('', 'ai', true);

            fetch(aiAskUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // FIX: Ensure the CSRF token is correctly sent for security
                    'X-CSRFToken': getCookie('csrftoken') 
                },
                body: JSON.stringify({ question: question })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => Promise.reject(err));
                }
                return response.json();
            })
            .then(data => {
                const messageContentDiv = thinkingDiv.querySelector('.message-content');
                const indicator = thinkingDiv.querySelector('.thinking-indicator');
                messageContentDiv.textContent = data.answer || 'No answer received.';
                if (indicator) indicator.remove();
            })
            .catch(error => {
                console.error('Error:', error);
                const messageContentDiv = thinkingDiv.querySelector('.message-content');
                const indicator = thinkingDiv.querySelector('.thinking-indicator');
                messageContentDiv.textContent = error.error || 'An unexpected error occurred. Please check the browser console.';
                if (indicator) indicator.remove();
            });
        });
    }

    function appendMessage(text, sender, isThinking = false) {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add(sender === 'user' ? 'user-message' : 'ai-message');
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        
        if (isThinking) {
            messageContent.innerHTML = `
                <div class="thinking-indicator">
                    <div class="spinner-grow spinner-grow-sm" role="status"></div>
                    <div class="spinner-grow spinner-grow-sm" style="animation-delay: 0.1s;" role="status"></div>
                    <div class="spinner-grow spinner-grow-sm" style="animation-delay: 0.2s;" role="status"></div>
                </div>`;
        } else {
            messageContent.textContent = text;
        }

        messageWrapper.appendChild(messageContent);
        chatHistory.appendChild(messageWrapper);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return messageWrapper;
    }
    
    // Helper function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});