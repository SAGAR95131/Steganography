from app import app, User

# Test the OAuth provider detection logic
def test_provider_detection():
    # Simulate checking for an existing user with a specific provider
    with app.app_context():
        # Create a test user
        user = User()
        user.email = "test@example.com"
        user.provider = "google"
        user.provider_id = "12345"
        
        print(f"User email: {user.email}")
        print(f"User provider: {user.provider}")
        print(f"User provider_id: {user.provider_id}")
        
        # Test the logic that would be used in the OAuth callback
        if user.provider == 'github':
            print("Would show: Please use the 'Continue with GitHub' button to log in.")
        elif user.provider == 'google':
            print("Would show: Please use the 'Continue with Google' button to log in.")
        else:
            print("Would show: Please use the same login method you used when creating your account.")

if __name__ == "__main__":
    test_provider_detection()