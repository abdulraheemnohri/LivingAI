document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const navBtns = document.querySelectorAll('.nav-btn');
    const views = document.querySelectorAll('.view');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            navBtns.forEach(b => b.classList.remove('active'));
            views.forEach(v => v.classList.remove('active'));
            btn.classList.add('active');
            const target = btn.getAttribute('data-target');
            document.getElementById(`view-${target}`).classList.add('active');
            if (target === 'memory') fetchMemories();
            if (target === 'goals') fetchGoals();
            if (target === 'skills') fetchSkills();
        });
    });

    // Chat
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');

    function appendMessage(text, type) {
        const msg = document.createElement('div');
        msg.className = `msg ${type}`;
        msg.textContent = text;
        chatMessages.appendChild(msg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;
        appendMessage(text, 'user');
        chatInput.value = '';

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: text })
            });
            const data = await res.json();
            appendMessage(data.response || data.error || 'No response', 'ai');
        } catch (err) {
            appendMessage(`Error: ${err.message}`, 'ai');
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Status Fetching
    async function fetchStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            document.getElementById('status-badge').textContent = '● Online';
            document.getElementById('status-badge').classList.add('online');
            document.getElementById('stat-memories').textContent = data.memory ? data.memory.total_memories : 0;
            document.getElementById('stat-goals').textContent = data.goals ? data.goals.length : 0;
            document.getElementById('stat-skills').textContent = data.skills || 0;
        } catch (err) {
            document.getElementById('status-badge').textContent = '● Offline';
            document.getElementById('status-badge').classList.remove('online');
        }
    }

    async function fetchDiagnostics() {
        try {
            const res = await fetch('/api/doctor');
            const data = await res.json();
            document.getElementById('diag-output').textContent = JSON.stringify(data, null, 2);
        } catch (err) {
            document.getElementById('diag-output').textContent = 'Error fetching diagnostics.';
        }
    }

    async function fetchMemories() {
        const container = document.getElementById('memory-list');
        try {
            const res = await fetch('/api/memory');
            const data = await res.json();
            container.innerHTML = data.memories.map(m => `
                <div class="item">
                    <strong>[${m.type}]</strong> ${m.content}
                </div>
            `).join('') || 'No memories saved.';
        } catch (err) {
            container.textContent = 'Failed to load memories.';
        }
    }

    async function fetchGoals() {
        const container = document.getElementById('goals-list');
        try {
            const res = await fetch('/api/goals');
            const data = await res.json();
            container.innerHTML = data.goals.map(g => `
                <div class="item">
                    <strong>${g.title}</strong> - Status: ${g.status}
                </div>
            `).join('') || 'No active goals.';
        } catch (err) {
            container.textContent = 'Failed to load goals.';
        }
    }

    async function fetchSkills() {
        const container = document.getElementById('skills-list');
        try {
            const res = await fetch('/api/skills');
            const data = await res.json();
            container.innerHTML = data.skills.map(s => `
                <div class="item">
                    <strong>${s.name}</strong> - ${s.description}
                </div>
            `).join('') || 'No skills registered.';
        } catch (err) {
            container.textContent = 'Failed to load skills.';
        }
    }

    fetchStatus();
    fetchDiagnostics();
});
