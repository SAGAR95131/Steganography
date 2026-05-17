from app import app, User

def check_users():
    with app.app_context():
        users = User.query.all()
        print("Users in database:")
        for user in users:
            print(f"- {user.email} ({user.provider})")
        print(f"Total users: {len(users)}")

if __name__ == "__main__":
    check_users()