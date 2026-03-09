"""Seed script — populate the database with sample data for development."""
import bcrypt
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.quest import Quest
from app.models.shop import ShopItem


SAMPLE_QUESTS = [
    {
        'title': 'Compliment a Stranger',
        'description': 'Give a genuine compliment to someone you don\'t know today. Take a selfie or photo of the moment!',
        'category': 'community',
        'difficulty_hint': 'easy',
        'reward_points': 10,
    },
    {
        'title': 'Help With Groceries',
        'description': 'Help someone carry their groceries or offer assistance at a store. Snap a photo!',
        'category': 'community',
        'difficulty_hint': 'easy',
        'reward_points': 15,
    },
    {
        'title': 'Pick Up Litter',
        'description': 'Pick up at least 5 pieces of litter from a public space. Take a before/after photo.',
        'category': 'environment',
        'difficulty_hint': 'easy',
        'reward_points': 10,
    },
    {
        'title': 'Write a Thank You Note',
        'description': 'Write a heartfelt thank you note to someone who has helped you. Photo the note!',
        'category': 'self-care',
        'difficulty_hint': 'easy',
        'reward_points': 10,
    },
    {
        'title': 'Donate Clothes',
        'description': 'Gather clothes you no longer need and donate them. Take a photo of your donation bag.',
        'category': 'community',
        'difficulty_hint': 'medium',
        'reward_points': 20,
    },
    {
        'title': 'Plant a Flower or Tree',
        'description': 'Plant something green in your yard or community garden. Document the planting!',
        'category': 'environment',
        'difficulty_hint': 'medium',
        'reward_points': 25,
    },
    {
        'title': 'Cook a Meal for Someone',
        'description': 'Prepare a meal for a friend, neighbor, or family member. Photo the dish!',
        'category': 'community',
        'difficulty_hint': 'medium',
        'reward_points': 20,
    },
    {
        'title': 'Leave a Positive Review',
        'description': 'Leave a genuine positive review for a local business you love. Screenshot it!',
        'category': 'community',
        'difficulty_hint': 'easy',
        'reward_points': 10,
    },
    {
        'title': 'Volunteer for an Hour',
        'description': 'Spend at least one hour volunteering at a local organization. Take a photo on site.',
        'category': 'community',
        'difficulty_hint': 'hard',
        'reward_points': 30,
    },
    {
        'title': 'Share Your Umbrella',
        'description': 'On a rainy day, share your umbrella with someone. Capture the moment!',
        'category': 'community',
        'difficulty_hint': 'easy',
        'reward_points': 10,
    },
]

SAMPLE_SHOP_ITEMS = [
    {
        'name': 'Golden Heart Frame',
        'description': 'A shimmering golden avatar frame showing your generous spirit.',
        'item_type': 'avatar_frame',
        'price_gems': 10,
        'metadata_json': {'color': '#FFD700', 'rarity': 'common'},
    },
    {
        'name': 'Rainbow Aura',
        'description': 'A colorful rainbow aura surrounding your avatar.',
        'item_type': 'cosmetic',
        'price_gems': 25,
        'metadata_json': {'color': 'rainbow', 'rarity': 'rare'},
    },
    {
        'name': 'Kindness Crown',
        'description': 'A royal crown for the most dedicated kindness warriors.',
        'item_type': 'cosmetic',
        'price_gems': 50,
        'metadata_json': {'color': '#9B59B6', 'rarity': 'epic'},
    },
    {
        'name': 'Nature Badge',
        'description': 'A badge shaped like a leaf for environmental heroes.',
        'item_type': 'badge',
        'price_gems': 15,
        'metadata_json': {'color': '#27AE60', 'rarity': 'common'},
    },
    {
        'name': 'Diamond Border',
        'description': 'The most exclusive avatar border. Only for legends.',
        'item_type': 'avatar_frame',
        'price_gems': 100,
        'metadata_json': {'color': '#00BFFF', 'rarity': 'legendary'},
    },
]


def seed():
    app = create_app()
    with app.app_context():
        # Create admin user
        admin = User.query.filter_by(email='admin@akd.app').first()
        if not admin:
            pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(
                email='admin@akd.app',
                password_hash=pw,
                display_name='AKD Admin',
                is_admin=True,
                points=1000,
                gems=500,
            )
            db.session.add(admin)
            print('[+] Created admin user: admin@akd.app / admin123')

        # Create test user
        test_user = User.query.filter_by(email='user@test.com').first()
        if not test_user:
            pw = bcrypt.hashpw('test1234'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            test_user = User(
                email='user@test.com',
                password_hash=pw,
                display_name='Kind Kid',
                points=50,
                gems=10,
            )
            db.session.add(test_user)
            print('[+] Created test user: user@test.com / test1234')

        # Seed quests
        existing_quests = Quest.query.count()
        if existing_quests == 0:
            for qdata in SAMPLE_QUESTS:
                quest = Quest(**qdata)
                db.session.add(quest)
            print(f'[+] Created {len(SAMPLE_QUESTS)} sample quests')

        # Seed shop items
        existing_items = ShopItem.query.count()
        if existing_items == 0:
            for sdata in SAMPLE_SHOP_ITEMS:
                item = ShopItem(**sdata)
                db.session.add(item)
            print(f'[+] Created {len(SAMPLE_SHOP_ITEMS)} shop items')

        db.session.commit()
        print('[✓] Database seeded successfully!')


if __name__ == '__main__':
    seed()
