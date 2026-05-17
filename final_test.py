#!/usr/bin/env python3
"""Final comprehensive test of CyberCloak application"""

import sys
import traceback

def test_imports():
    """Test all imports work correctly"""
    print("🔍 Testing imports...")
    try:
        from app import app, db
        from models import User, EncryptionJob, ContactMessage
        from steganography import SteganoTool
        from encryption import EncryptionTool
        from image_processor import ImageProcessor
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database operations"""
    print("🔍 Testing database...")
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
            print("✅ Database tables created")
            
            # Test creating a user
            from models import User
            test_user = User(
                name="Test User",
                username="testuser",
                email="test@example.com",
                password_hash="test_hash"
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ User creation successful")
            
            # Clean up
            db.session.delete(test_user)
            db.session.commit()
            print("✅ Database cleanup successful")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_routes():
    """Test all routes are accessible"""
    print("🔍 Testing routes...")
    try:
        from app import app
        with app.test_client() as client:
            # Test main routes
            routes_to_test = [
                ('/', 'Home page'),
                ('/login', 'Login page'),
                ('/signup', 'Signup page'),
                ('/about', 'About page'),
                ('/help', 'Help page'),
                ('/contact', 'Contact page'),
                ('/api-docs', 'API docs page'),
            ]
            
            for route, name in routes_to_test:
                response = client.get(route)
                if response.status_code == 200:
                    print(f"✅ {name}: OK")
                else:
                    print(f"❌ {name}: {response.status_code}")
                    return False
        return True
    except Exception as e:
        print(f"❌ Route error: {e}")
        return False

def test_encryption():
    """Test encryption and steganography functionality"""
    print("🔍 Testing encryption...")
    try:
        from encryption import EncryptionTool
        from steganography import SteganoTool
        from image_processor import ImageProcessor
        
        # Test encryption
        enc_tool = EncryptionTool()
        test_message = "This is a test message"
        test_password = "test_password"
        
        encrypted = enc_tool.encrypt_data(test_message, test_password)
        if encrypted:
            print("✅ Encryption successful")
            
            decrypted = enc_tool.decrypt_data(encrypted, test_password)
            if decrypted == test_message:
                print("✅ Decryption successful")
            else:
                print("❌ Decryption failed")
                return False
        else:
            print("❌ Encryption failed")
            return False
            
        # Test steganography
        stego_tool = SteganoTool()
        print("✅ Steganography module loaded")
        
        # Test image processor
        img_processor = ImageProcessor()
        print("✅ Image processor loaded")
        
        return True
    except Exception as e:
        print(f"❌ Encryption error: {e}")
        return False

def test_templates():
    """Test template rendering"""
    print("🔍 Testing templates...")
    try:
        from app import app
        with app.test_client() as client:
            # Test template rendering
            response = client.get('/')
            if b'CyberCloak' in response.data:
                print("✅ Home template renders correctly")
            else:
                print("❌ Home template missing content")
                return False
                
            response = client.get('/about')
            if b'About CyberCloak' in response.data:
                print("✅ About template renders correctly")
            else:
                print("❌ About template missing content")
                return False
                
        return True
    except Exception as e:
        print(f"❌ Template error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting CyberCloak Application Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database,
        test_routes,
        test_encryption,
        test_templates
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            traceback.print_exc()
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CyberCloak is ready to use!")
        print("\n🚀 To start the application:")
        print("   python app.py")
        print("\n🌐 Then open your browser to:")
        print("   http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
