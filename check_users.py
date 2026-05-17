from app import app, User

with app.app_context():
    users = User.query.all()
    print("Users in database:")
    for user in users:
        print(f"- {user.email} ({user.provider})")