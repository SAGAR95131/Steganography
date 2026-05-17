from app import app, User

def test_oauth_conflict():
    with app.app_context():
        # Get an existing user
        existing_user = User.query.first()
        if existing_user:
            print(f"Existing user email: {existing_user.email}")
            print(f"Existing user provider: {existing_user.provider}")
            
            # Test the logic for different scenarios
            if existing_user.provider == 'github':
                print("Conflict message would be: Please use the 'Continue with GitHub' button to log in.")
            elif existing_user.provider == 'google':
                print("Conflict message would be: Please use the 'Continue with Google' button to log in.")
            else:
                print("Conflict message would be: Please use the same login method you used when creating your account.")
        else:
            print("No users found in database.")

if __name__ == "__main__":
    test_oauth_conflict()