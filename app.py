import os
import json
import time
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import uuid

# Import our modules
from models import db, User, EncryptionJob, ContactMessage
from steganography import SteganoTool
from encryption import EncryptionTool
from image_processor import ImageProcessor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "cybercloak_secret_key_2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# OAuth configuration
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')
app.config['GITHUB_CLIENT_ID'] = os.environ.get('GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = os.environ.get('GITHUB_CLIENT_SECRET')

# Email configuration
app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY')
app.config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL', 'admin@cybercloak.com')

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this feature.'
login_manager.login_message_category = 'info'

oauth = OAuth(app)

# Configure OAuth providers
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

github = oauth.register(
    name='github',
    client_id=app.config['GITHUB_CLIENT_ID'],
    client_secret=app.config['GITHUB_CLIENT_SECRET'],
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return filename and '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('auth/login.html')

@app.route('/auth/<provider>')
def oauth_login(provider):
    if provider == 'google':
        redirect_uri = url_for('oauth_callback', provider='google', _external=True)
        return google.authorize_redirect(redirect_uri)
    elif provider == 'github':
        redirect_uri = url_for('oauth_callback', provider='github', _external=True)
        return github.authorize_redirect(redirect_uri)
    else:
        flash('Invalid provider', 'error')
        return redirect(url_for('login'))

@app.route('/auth/<provider>/callback')
def oauth_callback(provider):
    try:
        if provider == 'google':
            token = google.authorize_access_token()
            user_info = token.get('userinfo')
            if user_info:
                user = User.query.filter_by(provider='google', provider_id=user_info['sub']).first()
                if not user:
                    # Check if user exists with same email but different provider
                    existing_user = User.query.filter_by(email=user_info['email']).first()
                    if existing_user:
                        flash('An account with this email already exists. Please use the same login method.', 'warning')
                        return redirect(url_for('login'))
                    
                    # Create new user
                    user = User(
                        email=user_info['email'],
                        username=user_info['email'].split('@')[0],
                        name=user_info.get('name', ''),
                        avatar_url=user_info.get('picture', ''),
                        provider='google',
                        provider_id=user_info['sub']
                    )
                    db.session.add(user)
                    db.session.commit()
                    flash('Account created successfully! Welcome to CyberCloak!', 'success')
                else:
                    user.last_login = datetime.utcnow()
                    db.session.commit()
                    flash(f'Welcome back, {user.name}!', 'success')
                
                login_user(user, remember=True)
                return redirect(url_for('dashboard'))
                
        elif provider == 'github':
            token = github.authorize_access_token()
            resp = github.get('user', token=token)
            user_info = resp.json()
            
            # Get user email
            email_resp = github.get('user/emails', token=token)
            emails = email_resp.json()
            primary_email = next((email['email'] for email in emails if email['primary']), None)
            
            if user_info and primary_email:
                user = User.query.filter_by(provider='github', provider_id=str(user_info['id'])).first()
                if not user:
                    # Check if user exists with same email but different provider
                    existing_user = User.query.filter_by(email=primary_email).first()
                    if existing_user:
                        flash('An account with this email already exists. Please use the same login method.', 'warning')
                        return redirect(url_for('login'))
                    
                    # Create new user
                    user = User(
                        email=primary_email,
                        username=user_info['login'],
                        name=user_info.get('name', user_info['login']),
                        avatar_url=user_info.get('avatar_url', ''),
                        provider='github',
                        provider_id=str(user_info['id'])
                    )
                    db.session.add(user)
                    db.session.commit()
                    flash('Account created successfully! Welcome to CyberCloak!', 'success')
                else:
                    user.last_login = datetime.utcnow()
                    db.session.commit()
                    flash(f'Welcome back, {user.name}!', 'success')
                
                login_user(user, remember=True)
                return redirect(url_for('dashboard'))
        
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('login'))
        
    except Exception as e:
        app.logger.error(f"OAuth callback error: {str(e)}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_jobs = EncryptionJob.query.filter_by(user_id=current_user.id).order_by(EncryptionJob.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', jobs=user_jobs)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            
            # Create contact message
            message = ContactMessage(
                user_id=current_user.id if current_user.is_authenticated else None,
                name=data.get('name'),
                email=data.get('email'),
                subject=data.get('subject'),
                message=data.get('message')
            )
            db.session.add(message)
            db.session.commit()
            
            # Message stored in database - no external email service needed
            # Admin can view messages in database
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Message sent successfully!'})
            else:
                flash('Message received! Thank you for contacting us. Rahul will respond to your email soon.', 'success')
                return redirect(url_for('contact'))
                
        except Exception as e:
            app.logger.error(f"Contact form error: {str(e)}")
            if request.is_json:
                return jsonify({'success': False, 'error': 'Failed to send message'}), 500
            else:
                flash('Failed to send message. Please try again.', 'error')
                return redirect(url_for('contact'))
    
    return render_template('contact.html')

def send_contact_email(contact_message):
    """Send contact form email using SendGrid"""
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail
        
        sg = sendgrid.SendGridAPIClient(api_key=app.config['SENDGRID_API_KEY'])
        
        message = Mail(
            from_email=contact_message.email,
            to_emails=app.config['ADMIN_EMAIL'],
            subject=f"CyberCloak Contact: {contact_message.subject}",
            html_content=f"""
            <h3>New Contact Message from CyberCloak</h3>
            <p><strong>Name:</strong> {contact_message.name}</p>
            <p><strong>Email:</strong> {contact_message.email}</p>
            <p><strong>Subject:</strong> {contact_message.subject}</p>
            <p><strong>Message:</strong></p>
            <p>{contact_message.message.replace(chr(10), '<br>')}</p>
            <p><strong>Sent:</strong> {contact_message.created_at}</p>
            """
        )
        
        response = sg.send(message)
        app.logger.info(f"Contact email sent successfully: {response.status_code}")
        
    except Exception as e:
        app.logger.error(f"Failed to send contact email: {str(e)}")

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'input_image' not in request.files:
            return jsonify({'error': 'No input image provided'}), 400
        
        input_file = request.files['input_image']
        
        if input_file.filename == '':
            return jsonify({'error': 'No input image selected'}), 400
        
        if not allowed_file(input_file.filename or ''):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Generate unique session ID for this upload
        session_id = str(uuid.uuid4())
        session['current_session'] = session_id
        
        # Save input file
        input_filename = secure_filename(input_file.filename or 'input.jpg')
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_input_{input_filename}")
        input_file.save(input_path)
        
        # Initialize tools
        steg_tool = SteganoTool()
        
        # Analyze uploaded image
        analysis = steg_tool.analyze_image(input_path)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'analysis': analysis,
            'input_file': input_filename
        })
        
    except Exception as e:
        app.logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/extract_decrypt', methods=['POST'])
@app.route('/extract_decrypt', methods=['POST'])
def api_extract_decrypt():
    if 'encrypted_image' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['encrypted_image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    try:
        # Generate session ID for this extraction
        session_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(filepath)
        
        # Get password if provided
        password = request.form.get('decrypt_password', '')
        
        # Extract and decrypt message
        result = steganography_processor.extract_decrypt(
            image_path=filepath,
            password=password if password else None
        )
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': result['message'],
            'was_encrypted': result['was_encrypted']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/encrypt_hide', methods=['POST'])
@login_required
def encrypt_hide():
    try:
        session_id = request.form.get('session_id')
        message = request.form.get('message', '')
        password = request.form.get('password', '')
        
        if not session_id:
            return jsonify({'error': 'No active session'}), 400
        
        # Find input file
        input_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                      if f.startswith(f"{session_id}_input_")]
        
        if not input_files:
            return jsonify({'error': 'Input file not found'}), 400
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_files[0])
        
        # Initialize tools
        steg_tool = SteganoTool()
        encrypt_tool = EncryptionTool()
        
        # Encrypt message if password provided
        if password:
            encrypted_message = encrypt_tool.encrypt_data(message, password)
        else:
            encrypted_message = message
        
        # Hide message in image
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_output.png")
        success = steg_tool.hide_message(input_path, encrypted_message, output_path)
        
        if success:
            # Save encryption job to database
            job = EncryptionJob(
                user_id=current_user.id,
                original_filename=input_files[0],
                encrypted_filename=f"{session_id}_output.png",
                message=message[:100] + "..." if len(message) > 100 else message,
                has_password=bool(password),
                file_size=os.path.getsize(output_path),
                status='completed'
            )
            db.session.add(job)
            db.session.commit()
            
            # Perform security analysis
            security_analysis = steg_tool.security_analysis(output_path)
            
            return jsonify({
                'success': True,
                'output_file': f"{session_id}_output.png",
                'security_analysis': security_analysis
            })
        else:
            return jsonify({'error': 'Failed to hide message in image'}), 500
            
    except Exception as e:
        app.logger.error(f"Encrypt/Hide error: {str(e)}")
        return jsonify({'error': f'Process failed: {str(e)}'}), 500

@app.route('/api/decrypt_reveal', methods=['POST'])
@login_required
def decrypt_reveal():
    try:
        session_id = request.form.get('session_id')
        password = request.form.get('password', '')
        
        if not session_id:
            return jsonify({'error': 'No active session'}), 400
        
        # Find input file
        input_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                      if f.startswith(f"{session_id}_input_")]
        
        if not input_files:
            return jsonify({'error': 'Input file not found'}), 400
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_files[0])
        
        # Initialize tools
        steg_tool = SteganoTool()
        encrypt_tool = EncryptionTool()
        
        # Extract hidden message
        hidden_message = steg_tool.extract_message(input_path)
        
        if hidden_message:
            # Try to decrypt if password provided
            if password:
                try:
                    decrypted_message = encrypt_tool.decrypt_data(hidden_message, password)
                    revealed_message = decrypted_message
                except:
                    revealed_message = "Failed to decrypt with provided password"
            else:
                revealed_message = hidden_message
            
            return jsonify({
                'success': True,
                'message': revealed_message,
                'encrypted': bool(password)
            })
        else:
            return jsonify({'error': 'No hidden message found in image'}), 404
            
    except Exception as e:
        app.logger.error(f"Decrypt/Reveal error: {str(e)}")
        return jsonify({'error': f'Process failed: {str(e)}'}), 500

@app.route('/api/extract_decrypt', methods=['POST'])
def extract_decrypt():
    try:
        # Get uploaded file
        if 'encrypted_image' not in request.files:
            return jsonify({'error': 'No encrypted image provided'}), 400
        
        encrypted_file = request.files['encrypted_image']
        if encrypted_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        session_id = str(uuid.uuid4())
        filename = secure_filename(encrypted_file.filename or 'encrypted.png')
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_encrypted_{filename}")
        encrypted_file.save(file_path)
        
        # Initialize tools
        steg_tool = SteganoTool()
        encrypt_tool = EncryptionTool()
        
        # Extract message from image
        extracted_message = steg_tool.extract_message(file_path)
        
        if not extracted_message:
            return jsonify({'error': 'No hidden message found in image'}), 400
        
        # Try to decrypt if password provided
        password = request.form.get('decrypt_password', '')
        if password:
            try:
                decrypted_message = encrypt_tool.decrypt_data(extracted_message, password)
                final_message = decrypted_message
            except Exception as e:
                # If decryption fails, maybe it wasn't encrypted
                final_message = extracted_message
        else:
            final_message = extracted_message
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': final_message,
            'was_encrypted': bool(password and final_message != extracted_message)
        })
        
    except Exception as e:
        app.logger.error(f"Extract/decrypt error: {str(e)}")
        return jsonify({'error': f'Extraction failed: {str(e)}'}), 500

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        return "Download failed", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)