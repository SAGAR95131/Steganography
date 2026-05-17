# CyberCloak - Secure Image Encryption Platform

A modern, full-featured web application for secure steganography and image encryption. Hide your secrets within images using military-grade encryption and advanced steganography techniques.

## 🚀 Features

### Core Functionality
- **Military-Grade Encryption**: AES-256 encryption with PBKDF2 key derivation
- **Advanced Steganography**: LSB (Least Significant Bit) techniques for invisible data hiding
- **Cross-Platform**: Works seamlessly across all devices and browsers
- **Real-time Processing**: Lightning-fast encryption and decryption
- **Zero Data Logging**: Complete privacy with no data storage

### User Interface
- **Modern Design**: Beautiful, responsive UI with dark theme
- **Multiple Themes**: Default, Cyberpunk, Ocean, Sunset themes
- **Interactive Animations**: Smooth transitions and hover effects
- **Mobile-First**: Fully responsive design for all screen sizes
- **Accessibility**: WCAG compliant with keyboard navigation

### User Management
- **OAuth Integration**: Google and GitHub login support
- **User Profiles**: Comprehensive profile management
- **Activity Tracking**: Complete history of encryption operations
- **Security Dashboard**: Real-time security status monitoring

### Pages & Navigation
- **Homepage**: Feature showcase with live demo
- **About**: Company information and team details
- **Help Center**: FAQ, tutorials, and documentation
- **Dashboard**: User control panel with statistics
- **Profile**: Account settings and preferences
- **Activity**: Complete operation history
- **Contact**: Support and communication
- **Legal**: Privacy Policy, Terms of Service, GDPR compliance

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **Flask-Login**: User authentication
- **Authlib**: OAuth integration
- **Cryptography**: Encryption libraries
- **Pillow**: Image processing
- **OpenCV**: Computer vision

### Frontend
- **Bootstrap 5**: CSS framework
- **Font Awesome**: Icons
- **Vanilla JavaScript**: Interactive functionality
- **CSS3**: Advanced styling with animations
- **HTML5**: Semantic markup

### Database
- **SQLite**: Development database
- **PostgreSQL**: Production ready

## 📁 Project Structure

```
sas/
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── models.py             # Database models
├── encryption.py         # Encryption utilities
├── steganography.py      # Steganography functions
├── image_processor.py    # Image processing utilities
├── pyproject.toml        # Dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   ├── main.js       # Core JavaScript
│   │   └── dashboard.js  # Dashboard functionality
│   └── images/           # Static images
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── dashboard.html    # User dashboard
│   ├── about.html        # About page
│   ├── help.html         # Help center
│   ├── contact.html      # Contact page
│   ├── privacy.html      # Privacy policy
│   ├── terms.html        # Terms of service
│   ├── profile.html      # User profile
│   ├── activity.html     # Activity history
│   ├── placeholder.html  # Placeholder pages
│   └── auth/
│       ├── login.html    # Login page
│       └── signup.html   # Signup page
└── uploads/              # File uploads directory
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- pip or uv package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sas
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. **Run the application**
   ```bash
   python app.py
   # or
   python main.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=sqlite:///instance/cybercloak.db

# Security
SESSION_SECRET=your-secret-key-here

# OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Email (Optional)
SENDGRID_API_KEY=your-sendgrid-api-key
ADMIN_EMAIL=admin@example.com
```

### OAuth Setup

1. **Google OAuth**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URIs

2. **GitHub OAuth**:
   - Go to GitHub Settings > Developer settings > OAuth Apps
   - Create a new OAuth App
   - Set authorization callback URL

## 📱 Usage

### Basic Workflow

1. **Sign Up/Login**: Create an account or use OAuth
2. **Upload Image**: Choose a high-quality image (PNG recommended)
3. **Enter Message**: Type your secret message
4. **Add Password**: Optionally encrypt with a password
5. **Process**: Click to encrypt and hide the message
6. **Download**: Get your encrypted image

### Message Extraction

1. **Upload Encrypted Image**: Use the extraction tool on homepage
2. **Enter Password**: If the message was encrypted
3. **Extract**: Click to reveal the hidden message

## 🔒 Security Features

- **AES-256 Encryption**: Military-grade symmetric encryption
- **PBKDF2 Key Derivation**: Password-based key derivation
- **Zero-Knowledge Architecture**: No server-side message storage
- **Client-Side Processing**: All encryption happens locally
- **Secure File Handling**: Temporary file cleanup
- **Session Management**: Secure user sessions
- **CSRF Protection**: Cross-site request forgery prevention

## 🎨 Customization

### Themes
The application supports multiple themes:
- Default: Professional blue gradient
- Cyberpunk: Neon pink and purple
- Ocean: Blue and teal tones
- Sunset: Warm orange and yellow

### Styling
- Modify `static/css/style.css` for custom styling
- CSS variables for easy color customization
- Responsive breakpoints for mobile optimization

## 🧪 Testing

### Manual Testing
1. Test all navigation links
2. Verify responsive design on different screen sizes
3. Test file upload and processing
4. Verify OAuth login flows
5. Test form validations

### Automated Testing
```bash
# Run tests (when implemented)
python -m pytest tests/
```

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   export FLASK_ENV=production
   export DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

2. **Database Migration**
   ```bash
   flask db upgrade
   ```

3. **Static Files**
   ```bash
   python -c "from app import app; app.app_context().push()"
   ```

4. **WSGI Server**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the Help Center in the application
- **Issues**: Report bugs via GitHub Issues
- **Contact**: Use the contact form in the application
- **Email**: support@cybercloak.com

## 🔮 Roadmap

### Planned Features
- [ ] Batch processing
- [ ] API endpoints
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Team collaboration
- [ ] Cloud storage integration
- [ ] Advanced steganography methods
- [ ] Real-time collaboration

### Version History
- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added user management and profiles
- **v1.2.0**: Enhanced UI and responsive design
- **v1.3.0**: Added help center and documentation

## 🙏 Acknowledgments

- Flask community for the excellent framework
- Bootstrap team for the CSS framework
- Font Awesome for the icon library
- All contributors and users

---

**Made with ❤️ for digital privacy and security**
