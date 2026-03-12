const topicInput = document.getElementById('topicInput');
const submitBtn = document.getElementById('submitBtn');
const logs = document.getElementById('logs');
const paperContent = document.getElementById('paperContent');
const downloadArea = document.getElementById('downloadArea');

let currentSessionId = null;

// WebSocket Setup
let ws;
function connectWS() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onopen = () => {
        console.log("WebSocket connected to agent swarm.");
        addLog('System', 'Connected', 'Ready for research tasks.', false);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Agent Message:", data);
        
        // Remove existing spinners
        stopSpinners();

        // Check if this is an "In Progress" action
        const inProgress = ["Planning", "Researching", "Drafting", "Refining", "Formatting", "Initialization"].some(word => 
            data.action.includes(word)
        );
        
        const isComplete = data.action === "Complete" || data.action === "Early Exit" || data.action === "Error";
        
        // Show spinner only if in progress and not final complete
        addLog(data.agent, data.action, data.content, inProgress && !isComplete);
        
        if (isComplete) {
            fetchPaper(data.session_id);
        }
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        addLog('System', 'Connection Error', 'Control channel failed. Retrying...', false);
    };

    ws.onclose = () => {
        console.log("WebSocket closed. Reconnecting...");
        setTimeout(connectWS, 5000);
    };
}

connectWS();

submitBtn.addEventListener('click', async () => {
    const topic = topicInput.value.trim();
    if (!topic) {
        alert("PLEASE ENTER A TOPIC.");
        return;
    }

    // Reset UI
    logs.innerHTML = '';
    addLog('System', 'Initialization', 'Spawning agent collective...', true);
    paperContent.innerHTML = '<p class="placeholder">PROCESSING... MONITOR LOGS FOR REAL-TIME FEEDBACK.</p>';
    downloadArea.style.display = 'none';
    submitBtn.disabled = true;

    try {
        const response = await fetch('/research', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic })
        });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Failed');
        }
    } catch (err) {
        addLog('System', 'Error', `Critical Failure: ${err.message}`, false);
        submitBtn.disabled = false;
    }
});

function addLog(agent, action, content, showSpinner) {
    const div = document.createElement('div');
    div.className = 'agent-step';
    if (showSpinner) div.classList.add('active-step');
    
    const header = document.createElement('div');
    header.className = 'agent-header';
    header.innerHTML = `
        ${showSpinner ? '<div class="spinner"></div>' : ''}
        <span class="agent-name"></span>
        <span class="agent-action"></span>
    `;
    header.querySelector('.agent-name').textContent = agent;
    header.querySelector('.agent-action').textContent = action;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'agent-content';
    contentDiv.textContent = content; // Safe from XSS
    
    div.appendChild(header);
    div.appendChild(contentDiv);
    logs.prepend(div);
}

function stopSpinners() {
    const activeSteps = document.querySelectorAll('.active-step');
    activeSteps.forEach(set => {
        set.classList.remove('active-step');
        const spinner = set.querySelector('.spinner');
        if (spinner) spinner.remove();
    });
}

async function fetchPaper(sessionId) {
    currentSessionId = sessionId;
    const response = await fetch(`/sessions/${sessionId}`);
    const data = await response.json();
    
    if (data.final_paper_md) {
        // Just the paper, no agent history
        paperContent.innerHTML = DOMPurify.sanitize(marked.parse(data.final_paper_md));
        downloadArea.style.display = 'flex';
        submitBtn.disabled = false;
        stopSpinners();
        addLog('System', 'Success', 'Final report synthesized and verified.', false);
    }
}

function download(format) {
    if (!currentSessionId) return;
    window.location.href = `/download/${currentSessionId}/${format}`;
}
