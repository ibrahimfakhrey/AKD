/* ═══════════════════════════════════════════════
   AKD Admin Panel — JavaScript Application
   ═══════════════════════════════════════════════ */

// Auto-detect: behind Nginx proxy → relative path; local dev → localhost:5000
const API_BASE = (location.port === '3000' || location.port === '80' || location.port === '')
    ? '/api/v1'
    : 'http://localhost:5000/api/v1';
const UPLOADS_BASE = (location.port === '3000' || location.port === '80' || location.port === '')
    ? ''
    : 'http://localhost:5000';
let accessToken = localStorage.getItem('akd_admin_token');
let currentUser = null;
let activePage = 'dashboard';
let pollingInterval = null;

/* ── API Client ──────────────────────────────── */
async function api(path, options = {}) {
    const headers = { ...options.headers };
    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }
    if (options.body && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }
    const resp = await fetch(`${API_BASE}${path}`, { ...options, headers });
    const data = await resp.json();
    if (!resp.ok) {
        throw new Error(data.error || `HTTP ${resp.status}`);
    }
    return data;
}

/* ── Toast Notifications ─────────────────────── */
function toast(msg, type = 'success') {
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 3000);
}

/* ── Authentication ──────────────────────────── */
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');
    const btn = document.getElementById('login-btn');

    btn.textContent = 'Signing in...';
    btn.disabled = true;
    errorEl.style.display = 'none';

    try {
        const data = await api('/auth/login', {
            method: 'POST',
            body: { email, password },
        });
        if (!data.user.is_admin) {
            throw new Error('Admin access required');
        }
        accessToken = data.access_token;
        localStorage.setItem('akd_admin_token', accessToken);
        currentUser = data.user;
        showApp();
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.style.display = 'block';
    } finally {
        btn.textContent = 'Sign In';
        btn.disabled = false;
    }
});

document.getElementById('logout-btn').addEventListener('click', () => {
    accessToken = null;
    localStorage.removeItem('akd_admin_token');
    stopPolling();
    showLogin();
});

function showLogin() {
    document.getElementById('login-screen').classList.add('active');
    document.getElementById('login-screen').style.display = 'flex';
    document.getElementById('app-shell').style.display = 'none';
}

function showApp() {
    document.getElementById('login-screen').classList.remove('active');
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('app-shell').style.display = 'flex';
    document.getElementById('admin-name').textContent = currentUser?.display_name || 'Admin';
    activePage = 'dashboard';
    startPolling();
}

/* ── Navigation ──────────────────────────────── */
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const page = item.dataset.page;

        // Update active nav
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        item.classList.add('active');

        // Show page
        document.querySelectorAll('.page').forEach(p => { p.style.display = 'none'; p.classList.remove('active'); });
        const pageEl = document.getElementById(`page-${page}`);
        pageEl.style.display = 'block';
        pageEl.classList.add('active');

        activePage = page;

        // Load data
        loadDataForPage(activePage);
    });
});

function loadDataForPage(page) {
    switch (page) {
        case 'dashboard': loadDashboard(); break;
        case 'quests': loadQuests(); break;
        case 'challenges': loadChallenges(); break;
        case 'moderation': loadModeration(); break;
        case 'users': loadUsers(usersPage); break;
        case 'audit': loadAuditLog(); break;
    }
}

function startPolling() {
    if (pollingInterval) clearInterval(pollingInterval);
    loadDataForPage(activePage);
    pollingInterval = setInterval(() => {
        loadDataForPage(activePage);
    }, 5000);
}

function stopPolling() {
    if (pollingInterval) clearInterval(pollingInterval);
}

/* ── Dashboard ───────────────────────────────── */
async function loadDashboard() {
    try {
        const data = await api('/admin/analytics');
        document.getElementById('stat-users').textContent = data.total_users.toLocaleString();
        document.getElementById('stat-quests').textContent = data.total_quests_completed.toLocaleString();
        document.getElementById('stat-challenges').textContent = data.total_challenges_completed.toLocaleString();
        document.getElementById('stat-pending').textContent = data.pending_proofs.toLocaleString();
        document.getElementById('stat-points').textContent = data.total_points_earned.toLocaleString();
        document.getElementById('stat-gems').textContent = data.total_gems_earned.toLocaleString();

        // Update pending badge
        const badge = document.getElementById('pending-badge');
        if (data.pending_proofs > 0) {
            badge.textContent = data.pending_proofs;
            badge.style.display = 'inline';
        } else {
            badge.style.display = 'none';
        }
    } catch (err) {
        console.error('Failed to load analytics:', err);
    }
}

/* ── Quests Management ───────────────────────── */
async function loadQuests() {
    try {
        const allQuestsData = await api('/admin/quests');
        const quests = allQuestsData.filter(q => q.difficulty_hint !== 'hard');
        const tbody = document.getElementById('quests-tbody');
        tbody.innerHTML = quests.map(q => `
            <tr>
                <td><strong>${esc(q.title)}</strong></td>
                <td>${esc(q.category || '—')}</td>
                <td><span class="badge badge-${q.difficulty_hint}">${q.difficulty_hint}</span></td>
                <td>⭐ ${q.reward_points}</td>
                <td><span class="badge ${q.active ? 'badge-active' : 'badge-inactive'}">${q.active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="btn btn-ghost btn-sm" onclick="editQuest('${q.id}')">Edit</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteQuest('${q.id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        toast('Failed to load quests: ' + err.message, 'error');
    }
}

async function loadChallenges() {
    try {
        const allQuestsData = await api('/admin/quests');
        const challenges = allQuestsData.filter(q => q.difficulty_hint === 'hard');
        const tbody = document.getElementById('challenges-tbody');
        tbody.innerHTML = challenges.map(q => `
            <tr>
                <td><strong>${esc(q.title)}</strong></td>
                <td>${esc(q.category || '—')}</td>
                <td><span class="badge badge-hard">Hard</span></td>
                <td>💎 ${q.reward_gems || 0}</td>
                <td><span class="badge ${q.active ? 'badge-active' : 'badge-inactive'}">${q.active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="btn btn-ghost btn-sm" onclick="editChallenge('${q.id}')">Edit</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteQuest('${q.id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        toast('Failed to load challenges: ' + err.message, 'error');
    }
}

// Quest Modal
document.getElementById('add-quest-btn').addEventListener('click', () => {
    document.getElementById('quest-modal-title').textContent = 'New Quest';
    document.getElementById('quest-form').reset();
    document.getElementById('quest-edit-id').value = '';
    document.getElementById('quest-modal').style.display = 'flex';
});

document.getElementById('quest-modal-close').addEventListener('click', closeQuestModal);
document.getElementById('quest-cancel-btn').addEventListener('click', closeQuestModal);

function closeQuestModal() {
    document.getElementById('quest-modal').style.display = 'none';
}

document.getElementById('quest-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const editId = document.getElementById('quest-edit-id').value;
    const payload = {
        title: document.getElementById('quest-title').value,
        description: document.getElementById('quest-description').value,
        category: document.getElementById('quest-category').value,
        difficulty_hint: document.getElementById('quest-difficulty').value,
        reward_points: parseInt(document.getElementById('quest-reward').value),
    };

    try {
        if (editId) {
            await api(`/admin/quests/${editId}`, { method: 'PUT', body: payload });
            toast('Quest updated!');
        } else {
            await api('/admin/quests', { method: 'POST', body: payload });
            toast('Quest created!');
        }
        closeQuestModal();
        loadQuests();
    } catch (err) {
        toast('Error: ' + err.message, 'error');
    }
});

async function editQuest(id) {
    try {
        const quests = await api('/admin/quests');
        const q = quests.find(x => x.id === id);
        if (!q) return;

        document.getElementById('quest-modal-title').textContent = 'Edit Quest';
        document.getElementById('quest-edit-id').value = q.id;
        document.getElementById('quest-title').value = q.title;
        document.getElementById('quest-description').value = q.description;
        document.getElementById('quest-category').value = q.category || 'community';
        document.getElementById('quest-difficulty').value = q.difficulty_hint;
        document.getElementById('quest-reward').value = q.reward_points;
        document.getElementById('quest-modal').style.display = 'flex';
    } catch (err) {
        toast('Error: ' + err.message, 'error');
    }
}

// Challenge Modal
document.getElementById('add-challenge-btn').addEventListener('click', () => {
    document.getElementById('challenge-modal-title').textContent = 'New Hard Challenge';
    document.getElementById('challenge-form').reset();
    document.getElementById('challenge-edit-id').value = '';
    document.getElementById('challenge-modal').style.display = 'flex';
});

document.getElementById('challenge-modal-close').addEventListener('click', closeChallengeModal);
document.getElementById('challenge-cancel-btn').addEventListener('click', closeChallengeModal);

function closeChallengeModal() {
    document.getElementById('challenge-modal').style.display = 'none';
}

document.getElementById('challenge-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const editId = document.getElementById('challenge-edit-id').value;
    const payload = {
        title: document.getElementById('challenge-title').value,
        description: document.getElementById('challenge-description').value,
        category: document.getElementById('challenge-category').value,
        difficulty_hint: 'hard',
        reward_gems: parseInt(document.getElementById('challenge-reward').value),
    };

    try {
        if (editId) {
            await api(`/admin/quests/${editId}`, { method: 'PUT', body: payload });
            toast('Challenge updated!');
        } else {
            await api('/admin/quests', { method: 'POST', body: payload });
            toast('Challenge created!');
        }
        closeChallengeModal();
        loadChallenges();
    } catch (err) {
        toast('Error: ' + err.message, 'error');
    }
});

async function editChallenge(id) {
    try {
        const quests = await api('/admin/quests');
        const q = quests.find(x => x.id === id);
        if (!q) return;

        document.getElementById('challenge-modal-title').textContent = 'Edit Hard Challenge';
        document.getElementById('challenge-edit-id').value = q.id;
        document.getElementById('challenge-title').value = q.title;
        document.getElementById('challenge-description').value = q.description;
        document.getElementById('challenge-category').value = q.category || 'community';
        document.getElementById('challenge-reward').value = q.reward_gems || 5;
        document.getElementById('challenge-modal').style.display = 'flex';
    } catch (err) {
        toast('Error: ' + err.message, 'error');
    }
}

async function deleteQuest(id) {
    if (!confirm('Deactivate this item?')) return;
    try {
        await api(`/admin/quests/${id}`, { method: 'DELETE' });
        toast('Item deactivated');
        activePage === 'quests' ? loadQuests() : loadChallenges();
    } catch (err) {
        toast('Error: ' + err.message, 'error');
    }
}

/* ── Moderation ──────────────────────────────── */
async function loadModeration() {
    try {
        const proofs = await api('/admin/proofs/pending');
        const grid = document.getElementById('moderation-grid');

        if (proofs.length === 0) {
            grid.innerHTML = '<p class="empty-state">🎉 No pending proofs to review!</p>';
            return;
        }

        // Define moderation rendering code here using a custom style for challenges
        grid.innerHTML = proofs.map(p => {
            const confidence = Math.round((p.verifier_confidence || 0) * 100);
            const barColor = confidence > 70 ? '#10b981' : confidence > 40 ? '#f59e0b' : '#ef4444';
            const isChallenge = p.proof_type === 'challenge';
            const cardBorder = isChallenge ? 'border: 2px solid #FBBF24; box-shadow: 0 0 10px rgba(251, 191, 36, 0.2);' : '';
            const badgeHTML = isChallenge
                ? '<div style="background:#FBBF24; color:#000; padding: 2px 8px; border-radius:4px; font-size:11px; font-weight:bold; display:inline-block; margin-bottom: 4px;">🏆 Challenge Proof</div>'
                : '<div style="background:#4ECDC4; color:#000; padding: 2px 8px; border-radius:4px; font-size:11px; font-weight:bold; display:inline-block; margin-bottom: 4px;">⭐ Quest Proof</div>';

            return `
                <div class="proof-card" id="proof-${p.id}" style="${cardBorder}">
                    <div class="proof-image">
                        ${p.file_url ? `<img src="${UPLOADS_BASE}${p.file_url}" alt="Proof" onerror="this.parentElement.innerHTML='📷'">` : '📷'}
                    </div>
                    <div class="proof-info">
                        ${badgeHTML}
                        <div class="proof-meta">
                            <div>User: ${esc(p.user_id.substring(0, 8))}...</div>
                            <div>Uploaded: ${new Date(p.upload_time).toLocaleString()}</div>
                        </div>
                        <div class="proof-confidence">
                            <span style="font-size:12px;color:var(--text-secondary);">AI Confidence:</span>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width:${confidence}%;background:${barColor}"></div>
                            </div>
                            <span style="font-size:12px;font-weight:600;">${confidence}%</span>
                        </div>
                        <div class="proof-actions">
                            <button class="btn btn-success btn-sm" onclick="verdictProof('${p.id}', true)" style="flex:1;">✓ Approve</button>
                            <button class="btn btn-danger btn-sm" onclick="verdictProof('${p.id}', false)" style="flex:1;">✗ Reject</button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        toast('Failed to load proofs: ' + err.message, 'error');
    }
}

async function verdictProof(proofId, approved) {
    try {
        await api(`/admin/proofs/${proofId}/verdict`, {
            method: 'POST',
            body: { approved },
        });
        toast(approved ? 'Proof approved!' : 'Proof rejected');
        const card = document.getElementById(`proof-${proofId}`);
        if (card) {
            card.style.opacity = '0';
            card.style.transform = 'scale(0.9)';
            setTimeout(() => { card.remove(); loadDashboard(); }, 300);
        }
    } catch (err) {
        toast('Error: ' + err.message, 'error');
    }
}

/* ── Users Management ────────────────────────── */
let usersPage = 1;

async function loadUsers(page = 1) {
    usersPage = page;
    const search = document.getElementById('user-search')?.value || '';
    try {
        const data = await api(`/admin/users?page=${page}&per_page=20&search=${encodeURIComponent(search)}`);
        const tbody = document.getElementById('users-tbody');
        tbody.innerHTML = data.users.map(u => `
            <tr>
                <td><strong>${esc(u.display_name)}</strong></td>
                <td>${esc(u.email)}</td>
                <td>⭐ ${u.points || 0}</td>
                <td>💎 ${u.gems || 0}</td>
                <td><span class="badge ${u.is_banned ? 'badge-banned' : 'badge-active'}">${u.is_banned ? 'Banned' : 'Active'}</span></td>
                <td>${new Date(u.created_at).toLocaleDateString()}</td>
                <td>
                    ${u.is_banned
                ? `<button class="btn btn-success btn-sm" onclick="unbanUser('${u.id}')">Unban</button>`
                : `<button class="btn btn-danger btn-sm" onclick="banUser('${u.id}')">Ban</button>`
            }
                    <button class="btn btn-primary btn-sm" onclick="openBalanceModal('${u.id}')">Modify Balances</button>
                </td>
            </tr>
        `).join('');

        // Pagination
        const pagination = document.getElementById('users-pagination');
        pagination.innerHTML = '';
        if (data.pages > 1) {
            for (let i = 1; i <= data.pages; i++) {
                const btn = document.createElement('button');
                btn.textContent = i;
                btn.className = i === page ? 'active' : '';
                btn.onclick = () => loadUsers(i);
                pagination.appendChild(btn);
            }
        }
    } catch (err) {
        toast('Failed to load users: ' + err.message, 'error');
    }
}

document.getElementById('user-search')?.addEventListener('input', debounce(() => loadUsers(1), 400));

async function banUser(userId) {
    if (!confirm('Ban this user?')) return;
    try {
        await api(`/admin/users/${userId}/ban`, { method: 'POST' });
        toast('User banned');
        loadUsers(usersPage);
    } catch (err) {
        toast('Error: ' + err.message, 'error');
    }
}

async function unbanUser(userId) {
    try {
        await api(`/admin/users/${userId}/unban`, { method: 'POST' });
        toast('User unbanned');
        loadUsers(usersPage);
    } catch (err) {
        toast('Error: ' + err.message, 'error');
    }
}

function openBalanceModal(userId) {
    document.getElementById('balance-user-id').value = userId;
    document.getElementById('balance-points-delta').value = '0';
    document.getElementById('balance-gems-delta').value = '0';
    document.getElementById('balance-modal').style.display = 'flex';
}

document.getElementById('balance-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const userId = document.getElementById('balance-user-id').value;
    const pointsDelta = parseInt(document.getElementById('balance-points-delta').value) || 0;
    const gemsDelta = parseInt(document.getElementById('balance-gems-delta').value) || 0;

    try {
        await api(`/admin/users/${userId}/modify_balances`, {
            method: 'POST',
            body: { points_delta: pointsDelta, gems_delta: gemsDelta }
        });
        toast('Balances updated successfully!');
        document.getElementById('balance-modal').style.display = 'none';
        loadUsers(usersPage);
        loadDashboard(); // Refresh stats
    } catch (err) {
        toast('Error: ' + err.message, 'error');
    }
});

/* ── Audit Log ───────────────────────────────── */
async function loadAuditLog() {
    try {
        const logs = await api('/admin/audit-log?limit=50');
        const tbody = document.getElementById('audit-tbody');
        tbody.innerHTML = logs.map(log => `
            <tr>
                <td>${new Date(log.timestamp).toLocaleString()}</td>
                <td>${esc(log.actor_id.substring(0, 8))}...</td>
                <td><span class="badge badge-easy">${esc(log.action_type)}</span></td>
                <td>${log.target_id ? esc(log.target_id.substring(0, 8)) + '...' : '—'}</td>
                <td><code style="font-size:11px;color:var(--text-muted);">${log.details ? JSON.stringify(log.details).substring(0, 60) : '—'}</code></td>
            </tr>
        `).join('');
    } catch (err) {
        toast('Failed to load audit log: ' + err.message, 'error');
    }
}

/* ── Utilities ───────────────────────────────── */
function esc(str) {
    if (!str) return '';
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

function debounce(fn, ms) {
    let t;
    return function (...args) {
        clearTimeout(t);
        t = setTimeout(() => fn.apply(this, args), ms);
    };
}

/* ── Auto-login check ────────────────────────── */
(async function init() {
    if (accessToken) {
        try {
            const user = await api('/auth/profile');
            if (user.is_admin) {
                currentUser = user;
                showApp();
                return;
            }
        } catch (_) { }
    }
    showLogin();
})();
