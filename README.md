# AKD — Acts of Kindness Daily

A gamified kindness app: complete daily quests, take photo proofs, earn points & gems, challenge friends, and climb the leaderboard.

## Tech Stack

| Layer | Tech |
|-------|------|
| **API** | Flask 3, SQLAlchemy, JWT, PostgreSQL |
| **Admin Panel** | Vanilla HTML/CSS/JS, served by Nginx |
| **Mobile** | Flutter *(coming soon)* |
| **Infra** | Docker Compose, Gunicorn, Redis |

---

## Quick Start (Docker)

```bash
# Clone and start everything
docker-compose up --build

# In another terminal, seed the database
docker-compose exec backend python seed.py
```

| Service | URL |
|---------|-----|
| **API** | http://localhost:5000/api/v1/health |
| **Admin Panel** | http://localhost:3000 |

**Default accounts** (after seeding):

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@akd.app` | `admin123` |
| User | `user@test.com` | `test1234` |

---

## Quick Start (Local Dev — no Docker)

```bash
cd backend
pip install -r requirements.txt

# Seed with sample data
python seed.py

# Run dev server
python wsgi.py
```

The backend uses **SQLite** by default in development — no Postgres needed.  
Admin panel: just open `admin/index.html` in a browser (or serve with `npx serve admin/`).

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Create account |
| POST | `/api/v1/auth/login` | Login, get JWT |
| POST | `/api/v1/auth/refresh` | Refresh token |
| GET | `/api/v1/auth/profile` | Get profile |
| PUT | `/api/v1/auth/profile` | Update profile |

### Daily Quests
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/quests/daily` | Get 3 daily quests |
| POST | `/api/v1/quests/<id>/submit` | Submit photo proof |

### Challenges
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/challenges/start` | Start challenge (−10 pts) |
| GET | `/api/v1/challenges/active` | Get active challenge |
| POST | `/api/v1/challenges/<id>/submit` | Submit challenge proof |
| GET | `/api/v1/challenges/` | List past challenges |

### Friends
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/friends/request` | Send friend request |
| POST | `/api/v1/friends/<id>/accept` | Accept request |
| DELETE | `/api/v1/friends/<id>` | Remove friend |
| GET | `/api/v1/friends/list` | List friends |
| GET | `/api/v1/friends/pending` | Incoming requests |

### Shop
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/shop/items` | Browse items |
| POST | `/api/v1/shop/buy/<id>` | Buy with gems |
| GET | `/api/v1/shop/inventory` | Your purchases |

### Leaderboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/leaderboard/points` | Points ranking |
| GET | `/api/v1/leaderboard/gems` | Gems ranking |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/v1/admin/quests` | Quest CRUD |
| GET | `/api/v1/admin/proofs/pending` | Moderation queue |
| POST | `/api/v1/admin/proofs/<id>/verdict` | Approve/reject proof |
| GET | `/api/v1/admin/users` | List/search users |
| POST | `/api/v1/admin/users/<id>/ban` | Ban user |
| GET | `/api/v1/admin/audit-log` | Audit log |
| GET | `/api/v1/admin/analytics` | Dashboard stats |

---

## Tests

```bash
cd backend
python -m pytest tests/ -v
```

**51 tests** covering: auth, quests, challenges, friends, shop, leaderboard, ledger, admin.

---

## Project Structure

```
AKD/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory
│   │   ├── config.py            # Dev/Test/Prod configs
│   │   ├── extensions.py        # SQLAlchemy, JWT, etc.
│   │   ├── models/              # Database models (7 files)
│   │   ├── api/v1/              # REST endpoints (8 blueprints)
│   │   ├── services/            # Business logic (5 services)
│   │   └── utils/               # Decorators, error handlers
│   ├── tests/                   # Pytest suite (8 test files)
│   ├── seed.py                  # Sample data seeder
│   ├── wsgi.py                  # WSGI entry point
│   ├── Dockerfile
│   └── requirements.txt
├── admin/                       # React-less admin panel
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   └── nginx.conf
└── docker-compose.yml
```
