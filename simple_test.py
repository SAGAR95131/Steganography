#!/usr/bin/env python3
"""
Simple test to verify CyberCloak functionality
"""
import sys
import os

# Add current directory to path
sys.path.append('.')

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")

    try:
        from image_processor import ImageProcessor
        print("OK: ImageProcessor imported successfully")
    except Exception as e:
        print(f"ERROR: ImageProcessor import failed: {e}")
        return False

    try:
        from steganography import SteganoTool
        print("OK: SteganoTool imported successfully")
    except Exception as e:
        print(f"ERROR: SteganoTool import failed: {e}")
        return False

    try:
        from encryption import EncryptionTool
        print("OK: EncryptionTool imported successfully")
    except Exception as e:
        print(f"ERROR: EncryptionTool import failed: {e}")
        return False

    return True

def test_basic_functionality():
    """Test basic functionality without PIL"""
    print("\n🔧 Testing basic functionality...")

    try:
        from image_processor import ImageProcessor
        processor = ImageProcessor()

        # Create a simple test image using numpy
        import numpy as np
        import cv2

        # Create a 100x100 RGB image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[:, :] = [255, 255, 255]  # White background

        # Add some color blocks
        img[20:40, 20:40] = [255, 0, 0]    # Red
        img[20:40, 60:80] = [0, 255, 0]    # Green
        img[60:80, 20:40] = [0, 0, 255]    # Blue
        img[60:80, 60:80] = [255, 255, 0]  # Yellow

        # Encode to PNG bytes
        _, buffer = cv2.imencode('.png', img)
        image_data = buffer.tobytes()

        print(f"📊 Created test image: {len(image_data)} bytes")

        # Test message
        test_message = "Hello CyberCloak!"
        test_password = "test123"

        print(f"💬 Test message: {test_message}")

        # Test encryption
        print("🔒 Testing encryption...")
        encrypted_data = processor.hide_message(image_data, test_message, test_password)

        if encrypted_data:
            print("✅ Encryption successful!")
            print(f"📊 Encrypted size: {len(encrypted_data)} bytes")
        else:
            print("❌ Encryption failed!")
            return False

        # Test decryption without password
        print("🔓 Testing decryption without password...")
        decrypted_message = processor.extract_message(encrypted_data)

        if decrypted_message:
            print("✅ Decryption without password successful!")
            print(f"💬 Decrypted message: {decrypted_message}")
        else:
            print("❌ Decryption without password failed!")
            return False

        # Test decryption with password
        print("🔐 Testing decryption with password...")
        decrypted_message = processor.extract_message(encrypted_data, test_password)

        if decrypted_message and decrypted_message == test_message:
            print("✅ Decryption with password successful!")
            print(f"💬 Decrypted message: {decrypted_message}")
            print("🎉 Message verification successful!")
            return True
        else:
            print("❌ Decryption with password failed!")
            print(f"Expected: {test_message}")
            print(f"Got: {decrypted_message}")
            return False

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_routes():
    """Test if Flask routes are accessible"""
    print("\n🌐 Testing Flask routes...")

    try:
        from app import app
        with app.test_client() as client:
            # Test dashboard route
            response = client.get('/dashboard')
            if response.status_code == 200:
                print("✅ Dashboard route accessible")
            else:
                print(f"❌ Dashboard route failed: {response.status_code}")

            # Test encryption endpoint (without file)
            response = client.post('/encrypt')
            if response.status_code == 400:
                print("✅ Encryption endpoint responds (expected 400 without file)")
            else:
                print(f"⚠️  Encryption endpoint unexpected response: {response.status_code}")

        return True
    except Exception as e:
        print(f"❌ Flask routes test failed: {e}")
        return False

if __name__ == "__main__":
    print("CyberCloak Simple Test Suite")
    print("=" * 50)

    # Test imports
    imports_ok = test_imports()

    if imports_ok:
        # Test basic functionality
        basic_ok = test_basic_functionality()

        # Test Flask routes
        flask_ok = test_flask_routes()

        if basic_ok and flask_ok:
            print("\n🎊 All tests passed! CyberCloak is working correctly.")
        else:
            print("\n💥 Some tests failed. Please check the implementation.")
    else:
        print("\n💥 Import tests failed. Please check dependencies.")

    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")