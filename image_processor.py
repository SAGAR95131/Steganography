import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import os
import io
from steganography import SteganoTool
from encryption import EncryptionTool

class ImageProcessor:
    def __init__(self):
        self.steganography = SteganoTool()
        self.encryption = EncryptionTool()
    
    def hide_message(self, image_data, message, password=None):
        """Hide message in image data using steganography and optional encryption"""
        try:
            # Convert image data to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return None
            
            # Encrypt message if password provided
            if password:
                encrypted_message = self.encryption.encrypt_data(message, password)
                if not encrypted_message:
                    return None
                message_to_hide = encrypted_message
            else:
                message_to_hide = message
            
            # Add delimiter to message
            message_with_delimiter = message_to_hide + self.steganography.delimiter
            
            # Convert message to binary
            binary_message = ''.join([format(ord(char), '08b') for char in message_with_delimiter])
            
            # Check if message can fit in image
            total_pixels = img.shape[0] * img.shape[1]
            if len(binary_message) > total_pixels * 3:  # 3 channels (BGR)
                return None
            
            # Flatten image array
            img_flat = img.flatten()
            
            # Hide message in LSB
            for i in range(len(binary_message)):
                img_flat[i] = (img_flat[i] & 0xFE) | int(binary_message[i])
            
            # Reshape back to original image dimensions
            img_with_message = img_flat.reshape(img.shape)
            
            # Encode image back to bytes
            _, buffer = cv2.imencode('.png', img_with_message)
            return buffer.tobytes()
            
        except Exception as e:
            print(f"Error hiding message: {str(e)}")
            return None
    
    def extract_message(self, image_data, password=None):
        """Extract hidden message from image data"""
        try:
            # Convert image data to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return None
            
            # Flatten image array
            img_flat = img.flatten()
            
            # Extract LSBs
            binary_message = ""
            for pixel in img_flat:
                binary_message += str(int(pixel) & 1)
            
            # Convert binary to text
            message = ""
            for i in range(0, len(binary_message), 8):
                if i + 8 <= len(binary_message):
                    byte = binary_message[i:i+8]
                    char = chr(int(byte, 2))
                    message += char
                    
                    # Check for delimiter
                    if message.endswith(self.steganography.delimiter):
                        extracted_message = message[:-len(self.steganography.delimiter)]
                        
                        # Try to decrypt if password provided
                        if password:
                            decrypted_message = self.encryption.decrypt_data(extracted_message, password)
                            if decrypted_message:
                                return decrypted_message
                            else:
                                return extracted_message  # Return as-is if decryption fails
                        else:
                            return extracted_message
            
            return None
            
        except Exception as e:
            print(f"Error extracting message: {str(e)}")
            return None
    
    def convert_format(self, input_path, output_path, target_format, quality=85):
        """Convert image format"""
        try:
            # Open image with PIL
            img = Image.open(input_path)
            
            # Convert to RGB if necessary for JPEG
            if target_format.upper() == 'JPEG' or target_format.upper() == 'JPG':
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                img.save(output_path, format='JPEG', quality=quality, optimize=True)
            elif target_format.upper() == 'PNG':
                img.save(output_path, format='PNG', optimize=True)
            elif target_format.upper() == 'WEBP':
                img.save(output_path, format='WEBP', quality=quality, optimize=True)
            else:
                img.save(output_path, format=target_format.upper())
            
            file_size = os.path.getsize(output_path)
            return True, file_size
            
        except Exception as e:
            print(f"Format conversion error: {str(e)}")
            return False, 0
    
    def optimize_for_steganography(self, image_path, output_path):
        """Optimize image for better steganography performance"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False
            
            # Apply slight Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(img, (3, 3), 0)
            
            # Enhance contrast slightly
            lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            cv2.imwrite(output_path, enhanced)
            return True
            
        except Exception as e:
            print(f"Optimization error: {str(e)}")
            return False
    
    def resize_image(self, image_path, output_path, target_size):
        """Resize image while maintaining aspect ratio"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False
            
            h, w = img.shape[:2]
            
            # Calculate scaling factor
            scale = min(target_size[0] / w, target_size[1] / h)
            
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            
            cv2.imwrite(output_path, resized)
            return True
            
        except Exception as e:
            print(f"Resize error: {str(e)}")
            return False
    
    def enhance_image(self, image_path, output_path, enhancement_type='auto'):
        """Enhance image quality"""
        try:
            img = Image.open(image_path)
            
            if enhancement_type == 'brightness':
                enhancer = ImageEnhance.Brightness(img)
                enhanced = enhancer.enhance(1.2)
            elif enhancement_type == 'contrast':
                enhancer = ImageEnhance.Contrast(img)
                enhanced = enhancer.enhance(1.3)
            elif enhancement_type == 'sharpness':
                enhancer = ImageEnhance.Sharpness(img)
                enhanced = enhancer.enhance(1.5)
            else:  # auto
                # Apply multiple enhancements
                contrast_enhancer = ImageEnhance.Contrast(img)
                enhanced = contrast_enhancer.enhance(1.1)
                
                sharpness_enhancer = ImageEnhance.Sharpness(enhanced)
                enhanced = sharpness_enhancer.enhance(1.2)
            
            enhanced.save(output_path, quality=95, optimize=True)
            return True
            
        except Exception as e:
            print(f"Enhancement error: {str(e)}")
            return False
    
    def add_noise_reduction(self, image_path, output_path):
        """Apply noise reduction to image"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False

            # Apply Non-local Means Denoising
            denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

            cv2.imwrite(output_path, denoised)
            return True

        except Exception as e:
            print(f"Noise reduction error: {str(e)}")
            return False

    def apply_filter(self, image_path, output_path, filter_type):
        """Apply various image filters"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False

            if filter_type == 'blur':
                filtered = cv2.GaussianBlur(img, (15, 15), 0)
            elif filter_type == 'sharpen':
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                filtered = cv2.filter2D(img, -1, kernel)
            elif filter_type == 'edge':
                filtered = cv2.Canny(img, 100, 200)
                filtered = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
            elif filter_type == 'emboss':
                kernel = np.array([[-2,-1,0], [-1,1,1], [0,1,2]])
                filtered = cv2.filter2D(img, -1, kernel)
                filtered = cv2.convertScaleAbs(filtered)
            elif filter_type == 'sepia':
                kernel = np.array([[0.272, 0.534, 0.131],
                                  [0.349, 0.686, 0.168],
                                  [0.393, 0.769, 0.189]])
                filtered = cv2.transform(img, kernel)
                filtered = np.clip(filtered, 0, 255).astype(np.uint8)
            elif filter_type == 'grayscale':
                filtered = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                filtered = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
            else:
                filtered = img

            cv2.imwrite(output_path, filtered)
            return True

        except Exception as e:
            print(f"Filter application error: {str(e)}")
            return False

    def add_watermark(self, image_path, output_path, watermark_text, position='bottom-right', opacity=0.5):
        """Add text watermark to image"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False

            # Create overlay
            overlay = img.copy()

            # Add text
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = min(img.shape[1], img.shape[0]) / 1000
            font_thickness = max(1, int(font_scale * 2))

            # Calculate text size
            (text_width, text_height), _ = cv2.getTextSize(watermark_text, font, font_scale, font_thickness)

            # Position watermark
            margin = 20
            if position == 'bottom-right':
                x = img.shape[1] - text_width - margin
                y = img.shape[0] - margin
            elif position == 'bottom-left':
                x = margin
                y = img.shape[0] - margin
            elif position == 'top-right':
                x = img.shape[1] - text_width - margin
                y = text_height + margin
            elif position == 'top-left':
                x = margin
                y = text_height + margin
            else:  # center
                x = (img.shape[1] - text_width) // 2
                y = (img.shape[0] + text_height) // 2

            # Add text to overlay
            cv2.putText(overlay, watermark_text, (x, y), font, font_scale,
                       (255, 255, 255), font_thickness, cv2.LINE_AA)

            # Blend with original image
            cv2.addWeighted(overlay, opacity, img, 1 - opacity, 0, img)

            cv2.imwrite(output_path, img)
            return True

        except Exception as e:
            print(f"Watermark error: {str(e)}")
            return False

    def extract_metadata(self, image_path):
        """Extract image metadata"""
        try:
            from PIL import Image as PILImage
            import os

            img = PILImage.open(image_path)

            metadata = {
                'filename': os.path.basename(image_path),
                'format': img.format,
                'size': img.size,
                'mode': img.mode,
                'width': img.width,
                'height': img.height,
                'file_size': os.path.getsize(image_path)
            }

            # Try to get EXIF data
            try:
                exif_data = img.getexif()
                if exif_data:
                    metadata['exif'] = str(dict(exif_data))
                else:
                    metadata['exif'] = 'No EXIF data available'
            except:
                metadata['exif'] = 'EXIF extraction failed'

            img.close()
            return metadata

        except Exception as e:
            print(f"Metadata extraction error: {str(e)}")
            return {'error': str(e)}

    def compress_image(self, image_path, output_path, quality=80):
        """Compress image to reduce file size"""
        try:
            img = Image.open(image_path)

            # Convert RGBA to RGB for JPEG
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background

            img.save(output_path, quality=quality, optimize=True)
            return True, os.path.getsize(output_path)

        except Exception as e:
            print(f"Compression error: {str(e)}")
            return False, 0
