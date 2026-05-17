#!/usr/bin/env python3
"""
Test script to verify encryption and decryption functionality
"""
import os
import sys
import io
try:
    from PIL import Image
except ImportError:
    raise ImportError("PIL is required for this script. Install with: pip install Pillow")
import numpy as np

# Add current directory to path
sys.path.append('.')

from image_processor import ImageProcessor

def create_test_image():
    """Create a simple test image"""
    # Create a 100x100 RGB image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :] = [255, 255, 255]  # White background

    # Add some color blocks
    img[20:40, 20:40] = [255, 0, 0]    # Red
    img[20:40, 60:80] = [0, 255, 0]    # Green
    img[60:80, 20:40] = [0, 0, 255]    # Blue
    img[60:80, 60:80] = [255, 255, 0]  # Yellow

    # Convert to PIL Image
    pil_img = Image.fromarray(img)

    # Save to bytes
    buffer = io.BytesIO()
    pil_img.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer.getvalue()

def test_encryption_decryption():
    """Test the full encryption/decryption cycle"""
    print("🔍 Testing CyberCloak Encryption/Decryption...")

    # Initialize processor
    processor = ImageProcessor()

    # Create test image
    print("📸 Creating test image...")
    test_image_data = create_test_image()

    # Test message
    test_message = "Hello, this is a test message for CyberCloak steganography!"
    test_password = "testpassword123"

    print(f"💬 Test message: {test_message}")
    print(f"🔐 Test password: {test_password}")

    # Test encryption
    print("\n🔒 Testing encryption...")
    try:
        encrypted_data = processor.hide_message(test_image_data, test_message, test_password)
        if encrypted_data:
            print("✅ Encryption successful!")
            print(f"📊 Original size: {len(test_image_data)} bytes")
            print(f"📊 Encrypted size: {len(encrypted_data)} bytes")
        else:
            print("❌ Encryption failed!")
            return False
    except Exception as e:
        print(f"❌ Encryption error: {str(e)}")
        return False

    # Test decryption without password
    print("\n🔓 Testing decryption without password...")
    try:
        decrypted_message = processor.extract_message(encrypted_data)
        if decrypted_message:
            print("✅ Decryption without password successful!")
            print(f"💬 Decrypted message: {decrypted_message}")
        else:
            print("❌ Decryption without password failed!")
            return False
    except Exception as e:
        print(f"❌ Decryption error: {str(e)}")
        return False

    # Test decryption with password
    print("\n🔐 Testing decryption with password...")
    try:
        decrypted_message = processor.extract_message(encrypted_data, test_password)
        if decrypted_message:
            print("✅ Decryption with password successful!")
            print(f"💬 Decrypted message: {decrypted_message}")

            # Verify the message matches
            if decrypted_message == test_message:
                print("🎉 Message verification successful!")
                return True
            else:
                print("❌ Message verification failed!")
                print(f"Expected: {test_message}")
                print(f"Got: {decrypted_message}")
                return False
        else:
            print("❌ Decryption with password failed!")
            return False
    except Exception as e:
        print(f"❌ Decryption with password error: {str(e)}")
        return False

def test_image_formats():
    """Test different image formats"""
    print("\n🖼️  Testing different image formats...")

    processor = ImageProcessor()
    test_message = "Format test message"

    formats = ['PNG', 'JPEG', 'BMP']

    for fmt in formats:
        try:
            # Create test image in different format
            img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
            pil_img = Image.fromarray(img)

            buffer = io.BytesIO()
            pil_img.save(buffer, format=fmt)
            buffer.seek(0)
            image_data = buffer.getvalue()

            # Test encryption
            encrypted = processor.hide_message(image_data, test_message)
            if encrypted:
                # Test decryption
                decrypted = processor.extract_message(encrypted)
                if decrypted == test_message:
                    print(f"✅ {fmt} format: OK")
                else:
                    print(f"❌ {fmt} format: Decryption failed")
            else:
                print(f"❌ {fmt} format: Encryption failed")

        except Exception as e:
            print(f"❌ {fmt} format: Error - {str(e)}")

if __name__ == "__main__":
    print("🚀 CyberCloak Encryption/Decryption Test Suite")
    print("=" * 50)

    # Test basic functionality
    success = test_encryption_decryption()

    if success:
        print("\n🎊 All tests passed! CyberCloak is working correctly.")
    else:
        print("\n💥 Some tests failed. Please check the implementation.")

    # Test different formats
    test_image_formats()

    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")