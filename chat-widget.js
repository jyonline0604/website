/**
 * kofhk.com AI Chat Widget — 小肥喵
 * Include this script on any page to add the chat widget.
 * Usage: <script src="chat-widget.js"></script>
 */
(function () {
  'use strict';

  const API = '/api/chat';
  const MAX_HISTORY = 30;

  // ── Styles ──
  const css = `
:root {
  --kofhk-chat-bg: #111118;
  --kofhk-chat-card: #1a1a24;
  --kofhk-chat-accent: #00d4ff;
  --kofhk-chat-accent2: #7c3aed;
  --kofhk-chat-text: #e0e0e0;
  --kofhk-chat-text2: #999;
  --kofhk-chat-border: rgba(255,255,255,0.08);
  --kofhk-chat-user-bubble: #1a3a5c;
  --kofhk-chat-ai-bubble: #1a1a28;
}

.kofhk-chat-fab {
  position: fixed; bottom: 24px; right: 24px; z-index: 9999;
  width: 56px; height: 56px; border-radius: 50%;
  background: var(--kofhk-chat-accent); border: none; cursor: pointer;
  box-shadow: 0 4px 16px rgba(0,212,255,0.3);
  display: flex; align-items: center; justify-content: center;
  font-size: 26px; transition: transform .2s, box-shadow .2s; color: #000;
}
.kofhk-chat-fab:hover { transform: scale(1.08); box-shadow: 0 6px 24px rgba(0,212,255,0.45); }
.kofhk-chat-fab.kofhk-chat-hidden { display: none; }

.kofhk-chat-panel {
  position: fixed; bottom: 96px; right: 24px; z-index: 9998;
  width: 380px; max-width: calc(100vw - 32px);
  height: 560px; max-height: calc(100vh - 160px);
  background: var(--kofhk-chat-bg);
  border: 1px solid var(--kofhk-chat-border); border-radius: 16px;
  display: flex; flex-direction: column;
  box-shadow: 0 8px 40px rgba(0,0,0,0.5); overflow: hidden;
  opacity: 0; transform: translateY(16px) scale(0.96);
  pointer-events: none; transition: opacity .25s, transform .25s;
}
.kofhk-chat-panel.kofhk-chat-open {
  opacity: 1; transform: translateY(0) scale(1); pointer-events: auto;
}

.kofhk-chat-header {
  background: var(--kofhk-chat-card); padding: 14px 18px;
  border-bottom: 1px solid var(--kofhk-chat-border);
  display: flex; align-items: center; justify-content: space-between;
  cursor: pointer; user-select: none;
}
.kofhk-chat-header-left { display: flex; align-items: center; gap: 10px; }
.kofhk-chat-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, var(--kofhk-chat-accent), var(--kofhk-chat-accent2));
  display: flex; align-items: center; justify-content: center; font-size: 18px;
}
.kofhk-chat-title { font-size: .95rem; font-weight: 600; color: #fff; font-family: sans-serif; }
.kofhk-chat-subtitle { font-size: .72rem; color: var(--kofhk-chat-text2); font-family: sans-serif; }
.kofhk-chat-close {
  width: 32px; height: 32px; border-radius: 50%;
  border: none; background: rgba(255,255,255,0.06);
  color: var(--kofhk-chat-text2); cursor: pointer; font-size: 18px;
  display: flex; align-items: center; justify-content: center; transition: background .2s;
}
.kofhk-chat-close:hover { background: rgba(255,255,255,0.12); color: #fff; }

.kofhk-chat-messages {
  flex: 1; overflow-y: auto; padding: 16px;
  display: flex; flex-direction: column; gap: 12px; scroll-behavior: smooth;
}
.kofhk-chat-msg {
  display: flex; gap: 8px; max-width: 90%;
  animation: kofhkMsgIn .25s ease;
}
@keyframes kofhkMsgIn { from { opacity: 0; transform: translateY(8px); } }
.kofhk-chat-msg.kofhk-chat-user { align-self: flex-end; flex-direction: row-reverse; }
.kofhk-chat-msg.kofhk-chat-ai { align-self: flex-start; }

.kofhk-chat-bubble {
  padding: 10px 14px; border-radius: 14px;
  font-size: .88rem; line-height: 1.5; color: #e0e0e0; word-break: break-word;
  font-family: sans-serif;
}
.kofhk-chat-msg.kofhk-chat-user .kofhk-chat-bubble {
  background: var(--kofhk-chat-user-bubble); border-bottom-right-radius: 4px;
}
.kofhk-chat-msg.kofhk-chat-ai .kofhk-chat-bubble {
  background: var(--kofhk-chat-ai-bubble); border: 1px solid var(--kofhk-chat-border); border-bottom-left-radius: 4px;
}

.kofhk-chat-avatar-mini {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 14px;
}
.kofhk-chat-msg.kofhk-chat-ai .kofhk-chat-avatar-mini {
  background: linear-gradient(135deg, var(--kofhk-chat-accent), var(--kofhk-chat-accent2));
}

.kofhk-chat-typing { display: flex; gap: 4px; padding: 10px 14px; align-items: center; }
.kofhk-chat-typing span {
  width: 6px; height: 6px; border-radius: 50%; background: var(--kofhk-chat-text2);
  animation: kofhkDotBounce 1.4s infinite ease-in-out both;
}
.kofhk-chat-typing span:nth-child(1) { animation-delay: 0s; }
.kofhk-chat-typing span:nth-child(2) { animation-delay: .16s; }
.kofhk-chat-typing span:nth-child(3) { animation-delay: .32s; }
@keyframes kofhkDotBounce {
  0%, 80%, 100% { transform: scale(0.6); }
  40% { transform: scale(1); }
}

.kofhk-chat-input-wrap {
  padding: 12px; border-top: 1px solid var(--kofhk-chat-border);
  display: flex; gap: 8px; background: var(--kofhk-chat-card);
}
.kofhk-chat-input-wrap textarea {
  flex: 1; padding: 10px 14px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--kofhk-chat-border); border-radius: 12px;
  color: #e0e0e0; font-size: .88rem; resize: none;
  outline: none; font-family: inherit;
  max-height: 100px; line-height: 1.4;
}
.kofhk-chat-input-wrap textarea:focus { border-color: var(--kofhk-chat-accent); }
.kofhk-chat-input-wrap textarea::placeholder { color: var(--kofhk-chat-text2); }
.kofhk-chat-send-btn {
  width: 42px; height: 42px; border-radius: 50%;
  border: none; background: var(--kofhk-chat-accent);
  color: #000; font-size: 18px; cursor: pointer;
  flex-shrink: 0; align-self: flex-end; transition: opacity .2s;
}
.kofhk-chat-send-btn:disabled { opacity: .4; cursor: not-allowed; }
.kofhk-chat-send-btn:hover:not(:disabled) { opacity: .85; }

.kofhk-chat-empty {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 10px;
  color: var(--kofhk-chat-text2); font-size: .85rem;
  text-align: center; padding: 20px; font-family: sans-serif;
}
.kofhk-chat-empty-icon { font-size: 48px; opacity: .6; }

.kofhk-chat-messages::-webkit-scrollbar { width: 4px; }
.kofhk-chat-messages::-webkit-scrollbar-track { background: transparent; }
.kofhk-chat-messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 4px; }

@media (max-width: 480px) {
  .kofhk-chat-panel { width: 100%; max-width: 100%; bottom: 0; right: 0; border-radius: 16px 16px 0 0; height: 70vh; max-height: 70vh; }
  .kofhk-chat-fab { bottom: 16px; right: 16px; }
}
`;

  // ── DOM Setup ──
  const styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // Floating button
  const fab = document.createElement('button');
  fab.className = 'kofhk-chat-fab';
  fab.title = '小肥喵 AI 助手';
  fab.setAttribute('aria-label', '開啟 AI 聊天');
  fab.textContent = '💬';

  // Panel
  const panel = document.createElement('div');
  panel.className = 'kofhk-chat-panel';
  panel.innerHTML = `
    <div class="kofhk-chat-header" id="kofhkChatHeader">
      <div class="kofhk-chat-header-left">
        <div class="kofhk-chat-avatar">🐱</div>
        <div>
          <div class="kofhk-chat-title">小肥喵 AI 助手</div>
          <div class="kofhk-chat-subtitle">kofhk.com 在線問答</div>
        </div>
      </div>
      <button class="kofhk-chat-close" id="kofhkChatClose" aria-label="關閉聊天">✕</button>
    </div>
    <div class="kofhk-chat-messages" id="kofhkChatMessages">
      <div class="kofhk-chat-empty" id="kofhkChatEmpty">
        <div class="kofhk-chat-empty-icon">🐱</div>
        <div>你好！我是小肥喵～</div>
        <div style="font-size:.78rem;color:#666;">可以問我小說進度、網站導覽，或者任何問題！</div>
      </div>
    </div>
    <div class="kofhk-chat-input-wrap">
      <textarea id="kofhkChatInput" rows="1" placeholder="輸入訊息..." maxlength="2000"></textarea>
      <button class="kofhk-chat-send-btn" id="kofhkChatSend" aria-label="發送">➤</button>
    </div>
  `;

  document.body.appendChild(fab);
  document.body.appendChild(panel);

  // ── Element refs ──
  const header = document.getElementById('kofhkChatHeader');
  const closeBtn = document.getElementById('kofhkChatClose');
  const messagesEl = document.getElementById('kofhkChatMessages');
  const emptyEl = document.getElementById('kofhkChatEmpty');
  const input = document.getElementById('kofhkChatInput');
  const sendBtn = document.getElementById('kofhkChatSend');

  let isOpen = false;
  let isSending = false;
  let history = [];

  // Load history from sessionStorage
  try {
    const saved = sessionStorage.getItem('kofhk-chat-history');
    if (saved) history = JSON.parse(saved);
  } catch (e) { /* ignore */ }

  function saveHistory() {
    try {
      sessionStorage.setItem('kofhk-chat-history', JSON.stringify(history.slice(-MAX_HISTORY)));
    } catch (e) { /* ignore */ }
  }

  // ── Panel toggle ──
  function openPanel() {
    panel.classList.add('kofhk-chat-open');
    fab.classList.add('kofhk-chat-hidden');
    isOpen = true;
    input.focus();
  }
  function closePanel() {
    panel.classList.remove('kofhk-chat-open');
    fab.classList.remove('kofhk-chat-hidden');
    isOpen = false;
  }

  fab.addEventListener('click', openPanel);
  closeBtn.addEventListener('click', (e) => { e.stopPropagation(); closePanel(); });
  header.addEventListener('click', () => {
    // Allow clicking header to close (toggle behavior)
    if (isOpen) closePanel();
  });

  // ── Helpers ──
  function scrollBottom() { messagesEl.scrollTop = messagesEl.scrollHeight; }

  function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML.replace(/\n/g, '<br>');
  }

  function addMessage(role, text) {
    emptyEl.style.display = 'none';
    const div = document.createElement('div');
    div.className = `kofhk-chat-msg kofhk-chat-${role}`;
    if (role === 'ai') {
      div.innerHTML = `<div class="kofhk-chat-avatar-mini">🐱</div><div class="kofhk-chat-bubble">${escapeHtml(text)}</div>`;
    } else {
      div.innerHTML = `<div class="kofhk-chat-bubble">${escapeHtml(text)}</div>`;
    }
    messagesEl.appendChild(div);
    scrollBottom();
    return div;
  }

  function addTyping() {
    emptyEl.style.display = 'none';
    const div = document.createElement('div');
    div.className = 'kofhk-chat-msg kofhk-chat-ai';
    div.id = 'kofhkTypingIndicator';
    div.innerHTML = `<div class="kofhk-chat-avatar-mini">🐱</div><div class="kofhk-chat-bubble"><div class="kofhk-chat-typing"><span></span><span></span><span></span></div></div>`;
    messagesEl.appendChild(div);
    scrollBottom();
  }

  function removeTyping() {
    const el = document.getElementById('kofhkTypingIndicator');
    if (el) el.remove();
  }

  // ── Restore previous messages ──
  if (history.length > 0) {
    emptyEl.style.display = 'none';
    for (const msg of history) {
      addMessage(msg.role === 'assistant' ? 'ai' : 'user', msg.content);
    }
  }

  // ── Send ──
  async function send() {
    const text = input.value.trim();
    if (!text || isSending) return;
    isSending = true;
    sendBtn.disabled = true;
    input.value = '';
    input.style.height = 'auto';

    addMessage('user', text);
    history.push({ role: 'user', content: text });
    saveHistory();

    addTyping();

    try {
      const resp = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: history.slice(-MAX_HISTORY) }),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: resp.statusText }));
        throw new Error(err.error || `HTTP ${resp.status}`);
      }
      const data = await resp.json();
      removeTyping();
      addMessage('ai', data.reply);
      history.push({ role: 'assistant', content: data.reply });
      saveHistory();
    } catch (e) {
      removeTyping();
      addMessage('ai', '⚠️ 出錯了：' + e.message);
    }

    isSending = false;
    sendBtn.disabled = false;
    input.focus();
  }

  sendBtn.addEventListener('click', send);
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });
  input.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 100) + 'px';
  });

  // ── Keyboard shortcut: Ctrl+Shift+K to open chat ──
  document.addEventListener('keydown', function (e) {
    if (e.ctrlKey && e.shiftKey && e.key === 'K') {
      e.preventDefault();
      if (isOpen) closePanel(); else openPanel();
    }
  });

})();
