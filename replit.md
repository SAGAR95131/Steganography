# CyberCloak - AI-Powered Image Encryption and Steganography Suite

## Overview

CyberCloak is a web-based application that combines image encryption with steganography techniques to provide secure, covert image transmission and storage. The application allows users to encrypt images and hide them within cover images using Least Significant Bit (LSB) steganography, making the hidden data virtually undetectable. Built with Flask and featuring a modern web interface, the tool is designed for both individual users and organizations requiring secure image handling capabilities.

The system provides dual functionality: encrypting and hiding images within cover images, and extracting and decrypting hidden images from steganographic containers. The application emphasizes user experience with drag-and-drop file uploads, real-time processing feedback, and multiple theme options.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework Architecture
The application uses Flask as the core web framework with a modular design pattern. The main application is initialized in `app.py` with configuration for file uploads (16MB limit), session management, and proxy handling. Routes are separated into a dedicated `routes.py` module for clean separation of concerns. The application supports both development and production deployment with configurable host and port settings.

### Frontend Architecture
The frontend employs a modern, responsive design using Bootstrap 5 for UI components and custom CSS for theming. The interface features a step-based workflow (Upload → Process → Download) with visual progress indicators. JavaScript handles file drag-and-drop functionality, theme switching, and AJAX communication with the backend. The template system uses Jinja2 with a base template for consistent layout and styling across pages.

### Security and Encryption System
The encryption module implements AES-256 encryption using the Fernet cipher from the cryptography library. Password-based key derivation uses PBKDF2-HMAC with SHA-256 and 100,000 iterations for enhanced security. The system generates encryption keys from user passwords with a static salt (configurable for production use). All encrypted data is base64-encoded for safe storage and transmission.

### Steganography Implementation
The steganography system uses Least Significant Bit (LSB) technique for hiding data within images. The implementation works with OpenCV for image processing and can embed encrypted data into the least significant bits of image pixels. A delimiter system ("###END###") marks the end of hidden messages during extraction. The tool validates image capacity before embedding to ensure data fits within the cover image.

### Image Processing Pipeline
The image processor handles format conversion between JPEG, PNG, WebP, and other formats with quality control options. The system includes optimization routines for better steganography performance, including Gaussian blur for noise reduction. PIL and OpenCV libraries work together to handle various image formats and maintain image quality during processing.

### Session and File Management
The application uses UUID-based session management to handle multiple concurrent users safely. Uploaded files are organized using session IDs to prevent conflicts and unauthorized access. The system includes automatic file cleanup and supports multiple file types with security validation. File naming follows a structured pattern: `{session_id}_{type}_{filename}` for organization and security.

### Theme and Customization System
The frontend supports multiple visual themes (Default, Cyberpunk, Ocean, Sunset) with CSS custom properties for easy switching. The theme system uses a dark-first approach with glass morphism effects and cyberpunk-inspired design elements. Users can switch themes dynamically, and preferences are maintained during the session.

## External Dependencies

### Core Web Framework
- **Flask**: Main web framework for routing, templating, and HTTP handling
- **Werkzeug**: WSGI utilities including ProxyFix for deployment behind reverse proxies

### Cryptography and Security
- **cryptography**: Provides Fernet symmetric encryption and PBKDF2 key derivation
- **hashlib**: Standard library for hashing operations
- **secrets**: Secure random number generation for cryptographic operations

### Image Processing Libraries
- **OpenCV (cv2)**: Primary image processing library for reading, writing, and manipulating images
- **PIL/Pillow**: Additional image processing capabilities and format conversion
- **NumPy**: Array operations for image data manipulation

### Frontend Technologies
- **Bootstrap 5**: CSS framework for responsive UI components
- **FontAwesome**: Icon library for interface elements
- **Custom CSS/JavaScript**: Enhanced user experience with drag-and-drop and theme switching

### File and Data Handling
- **os**: File system operations and path management
- **uuid**: Unique identifier generation for session management
- **json**: Data serialization for AJAX responses
- **base64**: Data encoding for safe storage and transmission

### Development and Deployment
- **logging**: Application logging and debugging
- **time**: Timestamp generation for file management
- **werkzeug.utils**: Secure filename handling for uploaded files

The application is designed to be self-contained with minimal external service dependencies, focusing on client-side processing and local file management for enhanced security and privacy.