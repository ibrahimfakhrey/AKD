/* ═══════════════════════════════════════════════
   AKD User Frontend — JavaScript Application
   ═══════════════════════════════════════════════ */

// Auto-detect API base (same logic as admin panel)
const API_BASE = (location.port === '' || location.port === '80' || location.port === '443')
    ? '/api/v1'
    : 'http://localhost:5000/api/v1';

const UPLOADS_BASE = (location.port === '' || location.port === '80' || location.port === '443')
    ? ''
    : 'http://localhost:5000';

let accessToken = localStorage.getItem('akd_user_token');
let refreshToken = localStorage.getItem('akd_user_refresh');
let currentUser = null;
let activePage = 'dashboard';
let leaderboardTab = 'points';

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
        throw new Error(data.error || data.msg || `HTTP ${resp.status}`);
    }
    return data;
}

/* ── Toast ────────────────────────────────────── */
function toast(msg, type = 'success') {
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 3000);
}

function esc(str) {
    if (!str) return '';
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

/* ══════════════════════════════════════════════
   AUTH
   ══════════════════════════════════════════════ */

// Toggle login/signup
document.getElementById('show-signup').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'block';
});

document.getElementById('show-login').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
});

// Login
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
        accessToken = data.access_token;
        refreshToken = data.refresh_token;
        localStorage.setItem('akd_user_token', accessToken);
        if (refreshToken) localStorage.setItem('akd_user_refresh', refreshToken);
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

// Signup
document.getElementById('signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const errorEl = document.getElementById('signup-error');
    const btn = document.getElementById('signup-btn');

    btn.textContent = 'Creating account...';
    btn.disabled = true;
    errorEl.style.display = 'none';

    try {
        const data = await api('/auth/signup', {
            method: 'POST',
            body: { display_name: name, email, password },
        });
        accessToken = data.access_token;
        refreshToken = data.refresh_token;
        localStorage.setItem('akd_user_token', accessToken);
        if (refreshToken) localStorage.setItem('akd_user_refresh', refreshToken);
        currentUser = data.user;
        toast('Welcome to AKD!');
        showApp();
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.style.display = 'block';
    } finally {
        btn.textContent = 'Create Account';
        btn.disabled = false;
    }
});

// Logout
document.getElementById('logout-btn').addEventListener('click', () => {
    accessToken = null;
    refreshToken = null;
    currentUser = null;
    localStorage.removeItem('akd_user_token');
    localStorage.removeItem('akd_user_refresh');
    showAuth();
});

function showAuth() {
    document.getElementById('auth-screen').classList.add('active');
    document.getElementById('auth-screen').style.display = 'flex';
    document.getElementById('app').style.display = 'none';
}

function showApp() {
    document.getElementById('auth-screen').classList.remove('active');
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('app').style.display = 'block';
    updateHeader();
    navigateTo('dashboard');
}

function updateHeader() {
    if (!currentUser) return;
    document.getElementById('header-points').textContent = `⭐ ${currentUser.points || 0}`;
    document.getElementById('header-gems').textContent = `💎 ${currentUser.gems || 0}`;
}

/* ══════════════════════════════════════════════
   NAVIGATION
   ══════════════════════════════════════════════ */

document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo(tab.dataset.page);
    });
});

function navigateTo(page) {
    activePage = page;

    // Update nav
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.nav-tab[data-page="${page}"]`)?.classList.add('active');

    // Show page
    document.querySelectorAll('.page').forEach(p => { p.style.display = 'none'; p.classList.remove('active'); });
    const pageEl = document.getElementById(`page-${page}`);
    if (pageEl) {
        pageEl.style.display = 'block';
        pageEl.classList.add('active');
    }

    loadPage(page);
}

function loadPage(page) {
    switch (page) {
        case 'dashboard': loadDailyQuests(); break;
        case 'challenges': loadChallengesPage(); break;
        case 'friends': loadFriendsPage(); break;
        case 'shop': loadShopPage(); break;
        case 'leaderboard': loadLeaderboard(); break;
        case 'profile': loadProfile(); break;
    }
}

/* ══════════════════════════════════════════════
   DAILY QUESTS (Dashboard)
   ══════════════════════════════════════════════ */

async function loadDailyQuests() {
    const list = document.getElementById('quests-list');
    try {
        const data = await api('/quests/daily');
        const quests = data.quests || data;

        // Update greeting
        const hour = new Date().getHours();
        let greet = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
        document.getElementById('greeting').textContent = `${greet}${currentUser ? ', ' + currentUser.display_name : ''}! Let's be kind today.`;

        if (!quests || quests.length === 0) {
            list.innerHTML = '<div class="empty-state">No quests available today. Check back later!</div>';
            return;
        }

        list.innerHTML = quests.map(q => {
            const completed = q.status === 'completed' || q.status === 'submitted';
            const catClass = `cat-${(q.category || 'community').replace('_', '-')}`;
            return `
                <div class="quest-card ${catClass} ${completed ? 'quest-completed' : ''}">
                    <div class="quest-card-header">
                        <span class="quest-title">${esc(q.title)}</span>
                        <span class="quest-reward">⭐ ${q.reward_points || 10}</span>
                    </div>
                    <p class="quest-desc">${esc(q.description)}</p>
                    <div class="quest-meta">
                        <span class="badge badge-${(q.category || 'community').replace('_', '-')}">${esc(q.category || 'community')}</span>
                        <span class="badge badge-${q.difficulty_hint || 'easy'}">${esc(q.difficulty_hint || 'easy')}</span>
                    </div>
                    ${completed
                    ? ''
                    : `<div class="quest-actions">
                            <button class="btn btn-primary btn-sm" onclick="openProofModal('${q.quest_id || q.id}', 'quest')">Submit Proof</button>
                        </div>`
                }
                </div>
            `;
        }).join('');

        // Refresh user data for header
        refreshUserData();
    } catch (err) {
        list.innerHTML = `<div class="empty-state">Failed to load quests: ${esc(err.message)}</div>`;
    }
}

/* ══════════════════════════════════════════════
   CHALLENGES
   ══════════════════════════════════════════════ */

async function loadChallengesPage() {
    await Promise.all([
        loadAvailableChallenges(),
        loadActiveChallenge(),
        loadReceivedChallenges(),
        loadPastChallenges(),
    ]);
}

async function loadAvailableChallenges() {
    const list = document.getElementById('challenge-pick-list');
    try {
        // Get hard quests from daily endpoint or challenges list
        const data = await api('/challenges/');
        // Show "start challenge" section if user has no active
        list.innerHTML = '<p class="empty-hint">Complete your active challenge first, or wait for a friend to send you one!</p>';
    } catch (err) {
        list.innerHTML = `<p class="empty-hint">${esc(err.message)}</p>`;
    }
}

async function loadActiveChallenge() {
    const section = document.getElementById('active-challenge-section');
    const content = document.getElementById('active-challenge-content');
    try {
        const data = await api('/challenges/active');
        if (data && data.id) {
            section.style.display = 'block';
            const remaining = data.expires_at
                ? Math.max(0, Math.round((new Date(data.expires_at) - Date.now()) / 60000))
                : '?';
            content.innerHTML = `
                <div class="active-challenge-card">
                    <h4>${esc(data.quest_title || data.title || 'Challenge')}</h4>
                    <p>${esc(data.quest_description || data.description || '')}</p>
                    <p style="font-size:13px;color:var(--accent-primary);font-weight:700;">
                        Time remaining: ${remaining} min | Reward: 💎 ${data.reward_gems || 5}
                    </p>
                    <button class="btn btn-primary btn-sm" onclick="openProofModal('${data.id}', 'challenge')" style="margin-top:12px;">
                        Submit Proof
                    </button>
                </div>
            `;
        } else {
            section.style.display = 'none';
        }
    } catch (err) {
        section.style.display = 'none';
    }
}

async function loadReceivedChallenges() {
    const list = document.getElementById('received-challenges-list');
    try {
        const data = await api('/challenges/received');
        const challenges = data.challenges || data;
        if (!challenges || challenges.length === 0) {
            list.innerHTML = '<p class="empty-hint">No challenges from friends yet.</p>';
            return;
        }
        list.innerHTML = challenges.map(c => `
            <div class="received-challenge-card">
                <h4>${esc(c.quest_title || 'Challenge')}</h4>
                <p>From: ${esc(c.sender_name || 'A friend')} | Reward: 💎 ${c.reward_gems || 5}</p>
                <button class="btn btn-primary btn-sm" onclick="acceptReceivedChallenge('${c.id}')">Accept</button>
            </div>
        `).join('');
    } catch (err) {
        list.innerHTML = '<p class="empty-hint">Could not load received challenges.</p>';
    }
}

async function loadPastChallenges() {
    const list = document.getElementById('past-challenges-list');
    try {
        const data = await api('/challenges/');
        const challenges = data.challenges || data;
        const past = (challenges || []).filter(c => c.status === 'completed' || c.status === 'expired' || c.status === 'failed');
        if (past.length === 0) {
            list.innerHTML = '<p class="empty-hint">No past challenges yet.</p>';
            return;
        }
        list.innerHTML = past.map(c => `
            <div class="past-challenge-item">
                <div>
                    <strong>${esc(c.quest_title || 'Challenge')}</strong>
                    <div style="font-size:12px;color:var(--text-muted);">${c.status}</div>
                </div>
                <span style="font-weight:700;color:${c.status === 'completed' ? 'var(--accent-success)' : 'var(--text-muted)'};">
                    ${c.status === 'completed' ? '💎 +' + (c.reward_gems || 5) : c.status}
                </span>
            </div>
        `).join('');
    } catch (err) {
        list.innerHTML = '<p class="empty-hint">Could not load past challenges.</p>';
    }
}

async function acceptReceivedChallenge(challengeId) {
    try {
        await api(`/challenges/${challengeId}/submit`, { method: 'POST', body: {} });
        toast('Challenge accepted!');
        loadChallengesPage();
    } catch (err) {
        toast(err.message, 'error');
    }
}

/* ══════════════════════════════════════════════
   FRIENDS
   ══════════════════════════════════════════════ */

async function loadFriendsPage() {
    await Promise.all([loadPendingRequests(), loadFriendsList()]);
}

// Send friend request
document.getElementById('friend-request-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('friend-email').value;
    try {
        await api('/friends/request', { method: 'POST', body: { friend_email: email } });
        toast('Friend request sent!');
        document.getElementById('friend-email').value = '';
    } catch (err) {
        toast(err.message, 'error');
    }
});

async function loadPendingRequests() {
    const list = document.getElementById('pending-requests-list');
    try {
        const data = await api('/friends/pending');
        const requests = data.requests || data;
        if (!requests || requests.length === 0) {
            list.innerHTML = '<p class="empty-hint">No pending requests.</p>';
            return;
        }
        list.innerHTML = requests.map(r => `
            <div class="friend-card">
                <div class="friend-info">
                    <div class="friend-avatar">👤</div>
                    <span class="friend-name">${esc(r.display_name || r.sender_name || r.email || 'User')}</span>
                </div>
                <div style="display:flex;gap:8px;">
                    <button class="btn btn-success btn-sm" onclick="acceptFriend('${r.id}')">Accept</button>
                    <button class="btn btn-ghost btn-sm" onclick="declineFriend('${r.id}')">Decline</button>
                </div>
            </div>
        `).join('');
    } catch (err) {
        list.innerHTML = '<p class="empty-hint">Could not load requests.</p>';
    }
}

async function loadFriendsList() {
    const list = document.getElementById('friends-list');
    try {
        const data = await api('/friends/list?status=accepted');
        const friends = data.friends || data;
        if (!friends || friends.length === 0) {
            list.innerHTML = '<p class="empty-hint">Add some friends to get started!</p>';
            return;
        }
        list.innerHTML = friends.map(f => `
            <div class="friend-card">
                <div class="friend-info">
                    <div class="friend-avatar">👤</div>
                    <div>
                        <div class="friend-name">${esc(f.display_name || f.name || 'Friend')}</div>
                        <div style="font-size:12px;color:var(--text-muted);">⭐ ${f.points || 0} | 💎 ${f.gems || 0}</div>
                    </div>
                </div>
                <div style="display:flex;gap:8px;">
                    <button class="btn btn-ghost btn-sm" onclick="sendChallengeToFriend('${f.friend_id || f.id}')">Challenge</button>
                    <button class="btn btn-ghost btn-sm" onclick="removeFriend('${f.id}')" style="color:var(--accent-danger);">Remove</button>
                </div>
            </div>
        `).join('');
    } catch (err) {
        list.innerHTML = '<p class="empty-hint">Could not load friends list.</p>';
    }
}

async function acceptFriend(requestId) {
    try {
        await api(`/friends/${requestId}/accept`, { method: 'POST' });
        toast('Friend added!');
        loadFriendsPage();
    } catch (err) {
        toast(err.message, 'error');
    }
}

async function declineFriend(requestId) {
    try {
        await api(`/friends/${requestId}`, { method: 'DELETE' });
        toast('Request declined.');
        loadFriendsPage();
    } catch (err) {
        toast(err.message, 'error');
    }
}

async function removeFriend(requestId) {
    if (!confirm('Remove this friend?')) return;
    try {
        await api(`/friends/${requestId}`, { method: 'DELETE' });
        toast('Friend removed.');
        loadFriendsPage();
    } catch (err) {
        toast(err.message, 'error');
    }
}

/* ── Send challenge to friend ─────────────── */
let sendChallengeQuestId = null;

function sendChallengeToFriend(friendId) {
    // Open modal to pick a quest to challenge them with
    document.getElementById('send-challenge-modal').style.display = 'flex';
    loadFriendsForChallenge(friendId);
}

async function loadFriendsForChallenge(friendId) {
    // For simplicity, directly send with a prompt
    const list = document.getElementById('send-challenge-friends-list');
    list.innerHTML = '<p>Sending challenge...</p>';
    try {
        await api('/challenges/send', {
            method: 'POST',
            body: { friend_id: friendId }
        });
        toast('Challenge sent!');
        document.getElementById('send-challenge-modal').style.display = 'none';
    } catch (err) {
        list.innerHTML = `<p class="empty-hint">${esc(err.message)}</p>`;
    }
}

document.getElementById('send-challenge-close').addEventListener('click', () => {
    document.getElementById('send-challenge-modal').style.display = 'none';
});
document.getElementById('send-challenge-cancel').addEventListener('click', () => {
    document.getElementById('send-challenge-modal').style.display = 'none';
});

/* ══════════════════════════════════════════════
   SHOP
   ══════════════════════════════════════════════ */

async function loadShopPage() {
    await Promise.all([loadShopItems(), loadInventory()]);
    if (currentUser) {
        document.getElementById('shop-gems').textContent = currentUser.gems || 0;
    }
}

async function loadShopItems() {
    const grid = document.getElementById('shop-grid');
    try {
        const data = await api('/shop/items');
        const items = data.items || data;
        if (!items || items.length === 0) {
            grid.innerHTML = '<div class="empty-state">Shop is empty. Check back later!</div>';
            return;
        }
        grid.innerHTML = items.map(item => `
            <div class="shop-item">
                <div class="shop-item-icon">${item.icon || '🎁'}</div>
                <div class="shop-item-name">${esc(item.name)}</div>
                <div class="shop-item-price">💎 ${item.price_gems}</div>
                <button class="btn btn-success btn-sm" onclick="buyItem('${item.id}')">Buy</button>
            </div>
        `).join('');
    } catch (err) {
        grid.innerHTML = `<div class="empty-state">${esc(err.message)}</div>`;
    }
}

async function loadInventory() {
    const grid = document.getElementById('inventory-grid');
    try {
        const data = await api('/shop/inventory');
        const items = data.items || data;
        if (!items || items.length === 0) {
            grid.innerHTML = '<p class="empty-hint">No items yet. Buy some from the shop!</p>';
            return;
        }
        grid.innerHTML = items.map(item => `
            <div class="inventory-item">
                <div class="inventory-item-icon">${item.icon || '🎁'}</div>
                <div class="inventory-item-name">${esc(item.name)}</div>
                ${item.item_type === 'cosmetic'
                ? `<button class="btn btn-ghost btn-sm" onclick="equipItem('${item.id}')" style="margin-top:6px;font-size:11px;">
                        ${item.equipped ? 'Equipped' : 'Equip'}
                    </button>`
                : ''}
            </div>
        `).join('');
    } catch (err) {
        grid.innerHTML = '<p class="empty-hint">Could not load inventory.</p>';
    }
}

async function buyItem(itemId) {
    try {
        await api(`/shop/buy/${itemId}`, { method: 'POST' });
        toast('Item purchased!');
        await refreshUserData();
        loadShopPage();
    } catch (err) {
        toast(err.message, 'error');
    }
}

async function equipItem(itemId) {
    try {
        await api(`/shop/equip/${itemId}`, { method: 'POST' });
        toast('Item equipped!');
        loadInventory();
    } catch (err) {
        toast(err.message, 'error');
    }
}

/* ══════════════════════════════════════════════
   LEADERBOARD
   ══════════════════════════════════════════════ */

document.getElementById('tab-points').addEventListener('click', () => {
    leaderboardTab = 'points';
    document.getElementById('tab-points').classList.add('active');
    document.getElementById('tab-gems').classList.remove('active');
    loadLeaderboard();
});

document.getElementById('tab-gems').addEventListener('click', () => {
    leaderboardTab = 'gems';
    document.getElementById('tab-gems').classList.add('active');
    document.getElementById('tab-points').classList.remove('active');
    loadLeaderboard();
});

async function loadLeaderboard() {
    const list = document.getElementById('leaderboard-list');
    try {
        const data = await api(`/leaderboard/${leaderboardTab}?limit=50`);
        const entries = data.leaderboard || data;
        if (!entries || entries.length === 0) {
            list.innerHTML = '<div class="empty-state">No entries yet. Start completing quests!</div>';
            return;
        }
        const icon = leaderboardTab === 'points' ? '⭐' : '💎';
        list.innerHTML = entries.map((entry, i) => {
            const isMe = currentUser && entry.user_id === currentUser.id;
            return `
                <div class="lb-row ${isMe ? 'lb-me' : ''}">
                    <span class="lb-rank">${i + 1}</span>
                    <span class="lb-name">${esc(entry.display_name || 'User')}</span>
                    <span class="lb-value">${icon} ${leaderboardTab === 'points' ? entry.points : entry.gems}</span>
                </div>
            `;
        }).join('');
    } catch (err) {
        list.innerHTML = `<div class="empty-state">${esc(err.message)}</div>`;
    }
}

/* ══════════════════════════════════════════════
   PROFILE
   ══════════════════════════════════════════════ */

async function loadProfile() {
    try {
        const user = await api('/auth/profile');
        currentUser = user;
        updateHeader();

        document.getElementById('profile-name').textContent = user.display_name || 'User';
        document.getElementById('profile-email').textContent = user.email || '';
        document.getElementById('profile-points').textContent = user.points || 0;
        document.getElementById('profile-gems').textContent = user.gems || 0;
        document.getElementById('edit-display-name').value = user.display_name || '';
    } catch (err) {
        toast('Failed to load profile', 'error');
    }
}

document.getElementById('profile-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const displayName = document.getElementById('edit-display-name').value;
    try {
        const user = await api('/auth/profile', {
            method: 'PUT',
            body: { display_name: displayName },
        });
        currentUser = user;
        updateHeader();
        toast('Profile updated!');
        loadProfile();
    } catch (err) {
        toast(err.message, 'error');
    }
});

/* ══════════════════════════════════════════════
   PROOF UPLOAD MODAL
   ══════════════════════════════════════════════ */

function openProofModal(targetId, targetType) {
    document.getElementById('proof-target-id').value = targetId;
    document.getElementById('proof-target-type').value = targetType;
    document.getElementById('proof-form').reset();
    document.getElementById('proof-target-id').value = targetId;
    document.getElementById('proof-target-type').value = targetType;
    document.getElementById('proof-modal-title').textContent =
        targetType === 'challenge' ? 'Submit Challenge Proof' : 'Submit Quest Proof';
    document.getElementById('proof-modal').style.display = 'flex';
}

document.getElementById('proof-modal-close').addEventListener('click', closeProofModal);
document.getElementById('proof-cancel-btn').addEventListener('click', closeProofModal);

function closeProofModal() {
    document.getElementById('proof-modal').style.display = 'none';
}

document.getElementById('proof-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const targetId = document.getElementById('proof-target-id').value;
    const targetType = document.getElementById('proof-target-type').value;
    const fileInput = document.getElementById('proof-file');
    const btn = document.getElementById('proof-submit-btn');

    if (!fileInput.files[0]) {
        toast('Please select a photo', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('photo', fileInput.files[0]);

    btn.textContent = 'Uploading...';
    btn.disabled = true;

    try {
        let url;
        if (targetType === 'challenge') {
            url = `/challenges/${targetId}/submit`;
        } else {
            url = `/quests/${targetId}/submit`;
        }
        await api(url, { method: 'POST', body: formData });
        toast('Proof submitted! Awaiting review.');
        closeProofModal();
        await refreshUserData();
        loadPage(activePage);
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        btn.textContent = 'Upload';
        btn.disabled = false;
    }
});

/* ══════════════════════════════════════════════
   HELPERS
   ══════════════════════════════════════════════ */

async function refreshUserData() {
    try {
        const user = await api('/auth/profile');
        currentUser = user;
        updateHeader();
    } catch (_) { }
}

/* ══════════════════════════════════════════════
   INIT — Auto-login check
   ══════════════════════════════════════════════ */

(async function init() {
    if (accessToken) {
        try {
            const user = await api('/auth/profile');
            currentUser = user;
            showApp();
            return;
        } catch (_) {
            // Token expired, clear it
            localStorage.removeItem('akd_user_token');
            accessToken = null;
        }
    }
    showAuth();
})();
