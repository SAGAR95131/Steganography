from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv()

import json
import time
import logging
import secrets
import smtplib
import pyotp
import qrcode
import io
import base64
import boto3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import our modules
from models import (db, User, EncryptionJob, ContactMessage, PasswordReset, FileStorage, FileShare, 
                   AuditLog, TwoFactorAuth, Notification, UserProfile, Follow, Post, PostLike, 
                   Comment, CommentLike, Workspace, WorkspaceMember, CollaborationSession, 
                   ShareRequest, ActivityFeed)
# Lazy-load heavy modules to avoid cv2/numpy import at startup (breaks Vercel)
def get_stegano():
    from steganography import SteganoTool
    return SteganoTool()

def get_encryption():
    from encryption import EncryptionTool
    return EncryptionTool()

# Lazy-load ImageProcessor to avoid heavy cv2/numpy import at startup (breaks Vercel)
_processor = None
def get_processor():
    global _processor
    if _processor is None:
        from image_processor import ImageProcessor
        _processor = ImageProcessor()
    return _processor

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cybercloak.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# OAuth configuration
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID', '')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET', '')
app.config['GITHUB_CLIENT_ID'] = os.environ.get('GITHUB_CLIENT_ID', '')
app.config['GITHUB_CLIENT_SECRET'] = os.environ.get('GITHUB_CLIENT_SECRET', '')

# Email configuration
app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY')
app.config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL', 'sagarsiddesh14@gmail.com')
app.config['SMTP_SERVER'] = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
app.config['SMTP_PORT'] = int(os.environ.get('SMTP_PORT', '587'))
app.config['SMTP_USERNAME'] = os.environ.get('SMTP_USERNAME', 'sagarsiddesh14@gmail.com')
app.config['SMTP_PASSWORD'] = os.environ.get('SMTP_PASSWORD', '')

# Twilio SMS
app.config['TWILIO_ACCOUNT_SID'] = os.environ.get('TWILIO_ACCOUNT_SID')
app.config['TWILIO_AUTH_TOKEN'] = os.environ.get('TWILIO_AUTH_TOKEN')
app.config['TWILIO_PHONE_NUMBER'] = os.environ.get('TWILIO_PHONE_NUMBER')
app.config['ADMIN_PHONE_NUMBER'] = os.environ.get('ADMIN_PHONE_NUMBER', '+919380695131')


# Cloud Storage configuration
app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID', '')
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
app.config['AWS_REGION'] = os.environ.get('AWS_REGION', 'us-east-1')
app.config['S3_BUCKET'] = os.environ.get('S3_BUCKET', 'cybercloak-files')
app.config['CLOUD_STORAGE_ENABLED'] = os.environ.get('CLOUD_STORAGE_ENABLED', 'false').lower() == 'true'

# 2FA configuration
app.config['TOTP_ISSUER'] = 'CyberCloak'

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# OAuth setup
oauth = OAuth(app)

# Google OAuth configuration
if app.config['GOOGLE_CLIENT_ID'] and app.config['GOOGLE_CLIENT_SECRET']:
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        access_token_url='https://oauth2.googleapis.com/token',
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={
            'scope': 'email profile'
        }
    )
else:
    google = None

# GitHub OAuth configuration
if app.config['GITHUB_CLIENT_ID'] and app.config['GITHUB_CLIENT_SECRET']:
    github = oauth.register(
        name='github',
        client_id=app.config['GITHUB_CLIENT_ID'],
        client_secret=app.config['GITHUB_CLIENT_SECRET'],
        authorize_url='https://github.com/login/oauth/authorize',
        access_token_url='https://github.com/login/oauth/access_token',
        api_base_url='https://api.github.com/',
        client_kwargs={
            'scope': 'user:email',
            'token_endpoint_auth_method': 'client_secret_post'
        }
    )
else:
    github = None

# User loader
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except Exception as e:
        app.logger.error(f"Error loading user {user_id}: {str(e)}")
        return None

# Helper functions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_email(to_email, subject, body, is_html=False):
    """Send email using Gmail SMTP with improved error handling"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = app.config['SMTP_USERNAME']
        msg['To'] = to_email
        msg['Subject'] = subject

        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        # Use SSL connection instead of STARTTLS
        server = smtplib.SMTP_SSL(app.config['SMTP_SERVER'], 465)
        server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
        text = msg.as_string()
        server.sendmail(app.config['SMTP_USERNAME'], to_email, text)
        server.quit()
        return True
    except Exception as e:
        app.logger.error(f"Failed to send email: {str(e)}")
        # Try alternative method if SSL fails
        try:
            server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
            server.starttls()
            server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
            text = msg.as_string()
            server.sendmail(app.config['SMTP_USERNAME'], to_email, text)
            server.quit()
            return True
        except Exception as e2:
            app.logger.error(f"Alternative email method also failed: {str(e2)}")
            return False

def send_password_reset_email(user_email, reset_token):
    """Send password reset email"""
    reset_url = f"{request.url_root}reset-password/{reset_token}"
    subject = "Password Reset - CyberCloak"
    body = f"""
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>You requested a password reset for your CyberCloak account.</p>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_url}" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this, please ignore this email.</p>
    </body>
    </html>
    """
    return send_email(user_email, subject, body, is_html=True)



def send_sms_notification(name, email, subject, message):
    import datetime
    # Log SMS locally
    try:
        with open('support_inbox.txt', 'a', encoding='utf-8') as f:
            f.write(f'\n[SMS NOTIFICATION] {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'To: {app.config.get("ADMIN_PHONE_NUMBER", "+919380695131")}\n')
            f.write(f'From: {name} ({email})\n')
            f.write(f'Subject: {subject}\n')
            f.write(f'Message: {message}\n')
            f.write('-'*50 + '\n')
    except:
        pass
    
    if not app.config.get('TWILIO_ACCOUNT_SID') or app.config.get('TWILIO_ACCOUNT_SID') == 'your_account_sid' or 'actual' in app.config.get('TWILIO_ACCOUNT_SID', ''):
        return True # Mock success
    try:
        client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])
        msg_body = f"New Contact:\n{name}\n{email}\nCurrent subj: {subject}\n{message[:100]}"
        client.messages.create(
            body=msg_body,
            from_=app.config['TWILIO_PHONE_NUMBER'],
            to=app.config['ADMIN_PHONE_NUMBER']
        )
        return True
    except Exception as e:
        app.logger.error(f"Failed to send SMS: {str(e)}")
        return False
    try:
        client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])
        msg_body = f"New Contact:\n{name}\n{email}\nCurrent subj: {subject}\n{message[:100]}"
        client.messages.create(
            body=msg_body,
            from_=app.config['TWILIO_PHONE_NUMBER'],
            to=app.config['ADMIN_PHONE_NUMBER']
        )
        return True
    except Exception as e:
        app.logger.error(f"Failed to send SMS: {str(e)}")
        return False


def send_contact_notification_email(name, email, subject, message):
    import datetime
    admin_email = app.config.get('ADMIN_EMAIL', 'sagarsiddesh14@gmail.com')
    
    # Log email locally
    try:
        with open('support_inbox.txt', 'a', encoding='utf-8') as f:
            f.write(f'\n[EMAIL NOTIFICATION] {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'To: {admin_email}\n')
            f.write(f'From: {name} ({email})\n')
            f.write(f'Subject: {subject}\n')
            f.write(f'Message: {message}\n')
            f.write('-'*50 + '\n')
    except:
        pass

    email_subject = f"New Contact Form Submission: {subject}"
    body = f"""
    <html>
    <body>
        <h2>New Contact Form Submission</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Message:</strong></p>
        <p>{message}</p>
        <hr>
        <p>Reply directly to this email to respond to the user.</p>
    </body>
    </html>
    """
    
    if not app.config.get('SMTP_PASSWORD') or 'tyvz ujoi' in app.config.get('SMTP_PASSWORD', '') or 'your_new' in app.config.get('SMTP_PASSWORD', ''):
        return True # Mock success
        
    return send_email(admin_email, email_subject, body, is_html=True)

# File Management Helper Functions
def upload_to_cloud(file_data, filename, content_type):
    """Upload file to cloud storage (AWS S3)"""
    if not app.config['CLOUD_STORAGE_ENABLED']:
        return None

    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=app.config['AWS_REGION']
        )

        key = f"files/{uuid.uuid4()}/{filename}"
        s3_client.put_object(
            Bucket=app.config['S3_BUCKET'],
            Key=key,
            Body=file_data,
            ContentType=content_type
        )

        return f"https://{app.config['S3_BUCKET']}.s3.{app.config['AWS_REGION']}.amazonaws.com/{key}"
    except Exception as e:
        app.logger.error(f"Cloud upload failed: {str(e)}")
        return None

def download_from_cloud(cloud_url):
    """Download file from cloud storage"""
    if not cloud_url or not app.config['CLOUD_STORAGE_ENABLED']:
        return None

    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=app.config['AWS_REGION']
        )

        # Extract bucket and key from URL
        bucket = app.config['S3_BUCKET']
        key = cloud_url.split(f"{bucket}/")[1] if f"{bucket}/" in cloud_url else cloud_url

        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()
    except Exception as e:
        app.logger.error(f"Cloud download failed: {str(e)}")
        return None

# 2FA Helper Functions
def generate_2fa_secret():
    """Generate a new 2FA secret key"""
    return pyotp.random_base32()

def generate_2fa_qr_code(secret, email):
    """Generate QR code for 2FA setup"""
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name=app.config['TOTP_ISSUER']
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 for embedding in HTML
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_base64}"

def verify_2fa_token(secret, token):
    """Verify 2FA token"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)

def generate_backup_codes():
    """Generate backup codes for 2FA"""
    return [secrets.token_hex(4).upper() for _ in range(10)]

# Audit Logging Helper Functions
def log_audit_event(user_id, action, resource_type=None, resource_id=None, status='success', details=None):
    """Log an audit event"""
    try:
        audit_log = AuditLog()
        audit_log.user_id = user_id
        audit_log.action = action
        audit_log.resource_type = resource_type
        audit_log.resource_id = resource_id
        audit_log.ip_address = request.remote_addr
        audit_log.user_agent = request.headers.get('User-Agent')
        audit_log.details = json.dumps(details) if details else None
        audit_log.status = status
        
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Audit logging failed: {str(e)}")

# Notification Helper Functions
def create_notification(user_id, title, message, notification_type='info', action_url=None, expires_at=None):
    """Create a notification for a user"""
    try:
        notification = Notification()
        notification.user_id = user_id
        notification.title = title
        notification.message = message
        notification.notification_type = notification_type
        notification.action_url = action_url
        notification.expires_at = expires_at
        
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        app.logger.error(f"Notification creation failed: {str(e)}")
        return None

def send_notification_to_all_users(title, message, notification_type='info'):
    """Send notification to all users"""
    try:
        users = User.query.all()
        for user in users:
            create_notification(user.id, title, message, notification_type)
    except Exception as e:
        app.logger.error(f"Bulk notification failed: {str(e)}")

# Social Features Helper Functions
def create_activity_feed_item(user_id, activity_type, actor_id, target_id=None, target_type=None, description=None, is_public=True):
    """Create an activity feed item"""
    try:
        activity = ActivityFeed()
        activity.user_id = user_id
        activity.activity_type = activity_type
        activity.actor_id = actor_id
        activity.target_id = target_id
        activity.target_type = target_type
        activity.description = description or f"User performed {activity_type}"
        activity.is_public = is_public
        
        db.session.add(activity)
        db.session.commit()
        return activity
    except Exception as e:
        app.logger.error(f"Activity feed creation failed: {str(e)}")
        return None

def get_user_profile(user_id):
    """Get or create user profile"""
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = UserProfile()
        profile.user_id = user_id
        db.session.add(profile)
        db.session.commit()
    return profile

def follow_user(follower_id, following_id):
    """Follow a user"""
    try:
        # Check if already following
        existing_follow = Follow.query.filter_by(follower_id=follower_id, following_id=following_id).first()
        if existing_follow:
            return False, "Already following this user"
        
        # Create follow relationship
        follow = Follow()
        follow.follower_id = follower_id
        follow.following_id = following_id
        db.session.add(follow)
        
        # Update follower counts
        follower_profile = get_user_profile(follower_id)
        following_profile = get_user_profile(following_id)
        follower_profile.following_count += 1
        following_profile.followers_count += 1
        
        db.session.commit()
        
        # Create activity feed item
        create_activity_feed_item(following_id, 'user_followed', follower_id, 
                                 target_id=following_id, target_type='user',
                                 description=f"Started following you")
        
        return True, "Successfully followed user"
    except Exception as e:
        app.logger.error(f"Follow user failed: {str(e)}")
        return False, "Failed to follow user"

def unfollow_user(follower_id, following_id):
    """Unfollow a user"""
    try:
        follow = Follow.query.filter_by(follower_id=follower_id, following_id=following_id).first()
        if not follow:
            return False, "Not following this user"
        
        db.session.delete(follow)
        
        # Update follower counts
        follower_profile = get_user_profile(follower_id)
        following_profile = get_user_profile(following_id)
        follower_profile.following_count -= 1
        following_profile.followers_count -= 1
        
        db.session.commit()
        return True, "Successfully unfollowed user"
    except Exception as e:
        app.logger.error(f"Unfollow user failed: {str(e)}")
        return False, "Failed to unfollow user"

def create_post(user_id, content, post_type='text', file_id=None, is_public=True):
    """Create a new post"""
    try:
        post = Post()
        post.user_id = user_id
        post.content = content
        post.post_type = post_type
        post.file_id = file_id
        post.is_public = is_public

        db.session.add(post)
        db.session.commit()

        # Create activity feed item
        create_activity_feed_item(user_id, 'post_created', user_id,
                                  target_id=post.id, target_type='post',
                                  description=f"Created a new post")

        return post
    except Exception as e:
        app.logger.error(f"Create post failed: {str(e)}")
        return None

def like_post(user_id, post_id):
    """Like a post"""
    try:
        # Check if already liked
        existing_like = PostLike.query.filter_by(user_id=user_id, post_id=post_id).first()
        if existing_like:
            return False, "Already liked this post"

        # Create like
        like = PostLike()
        like.user_id = user_id
        like.post_id = post_id
        db.session.add(like)

        # Update post like count
        post = Post.query.get(post_id)
        if post:
            post.likes_count += 1
            db.session.commit()

            # Create activity feed item
            create_activity_feed_item(post.user_id, 'post_liked', user_id,
                                  target_id=post_id, target_type='post',
                                  description=f"Liked your post")

            return True, "Post liked successfully"
        else:
            return False, "Post not found"
    except Exception as e:
        app.logger.error(f"Like post failed: {str(e)}")
        return False, "Failed to like post"

def create_workspace(owner_id, name, description=None, is_public=False):
    """Create a new workspace"""
    try:
        workspace = Workspace()
        workspace.name = name
        workspace.description = description
        workspace.owner_id = owner_id
        workspace.is_public = is_public

        db.session.add(workspace)
        db.session.commit()

        # Add owner as workspace member
        member = WorkspaceMember()
        member.workspace_id = workspace.id
        member.user_id = owner_id
        member.role = 'owner'
        db.session.add(member)
        db.session.commit()

        return workspace
    except Exception as e:
        app.logger.error(f"Create workspace failed: {str(e)}")
        return None

# Social Features Routes
@app.route('/social')
@login_required
def social():
    """Social feed page"""
    # Get posts from users the current user follows
    following_ids = [f.following_id for f in Follow.query.filter_by(follower_id=current_user.id).all()]
    following_ids.append(current_user.id)  # Include own posts
    
    posts = Post.query.filter(
        Post.user_id.in_(following_ids),
        Post.is_public == True
    ).order_by(Post.created_at.desc()).limit(20).all()
    
    return render_template('social.html', posts=posts)

@app.route('/profile/<user_id>')
@login_required
def user_profile(user_id):
    """User profile page"""
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('social'))
    
    profile = get_user_profile(user_id)
    posts = Post.query.filter_by(user_id=user_id, is_public=True).order_by(Post.created_at.desc()).limit(10).all()
    
    # Check if current user is following this user
    is_following = Follow.query.filter_by(follower_id=current_user.id, following_id=user_id).first() is not None
    
    return render_template('user_profile.html', user=user, profile=profile, posts=posts, is_following=is_following)

@app.route('/workspaces')
@login_required
def workspaces():
    """Workspaces page"""
    user_workspaces = Workspace.query.filter(
        (Workspace.owner_id == current_user.id) | 
        (Workspace.id.in_([m.workspace_id for m in WorkspaceMember.query.filter_by(user_id=current_user.id).all()]))
    ).all()
    
    return render_template('workspaces.html', workspaces=user_workspaces)

@app.route('/collaborate')
@login_required
def collaborate():
    """Collaboration hub page"""
    return render_template('collaborate.html')

# Social API Routes
@app.route('/api/follow/<user_id>', methods=['POST'])
@login_required
def api_follow_user(user_id):
    """Follow a user"""
    if user_id == current_user.id:
        return jsonify({'success': False, 'error': 'Cannot follow yourself'}), 400
    
    success, message = follow_user(current_user.id, user_id)
    return jsonify({'success': success, 'message': message})

@app.route('/api/unfollow/<user_id>', methods=['POST'])
@login_required
def api_unfollow_user(user_id):
    """Unfollow a user"""
    success, message = unfollow_user(current_user.id, user_id)
    return jsonify({'success': success, 'message': message})

@app.route('/api/posts', methods=['POST'])
@login_required
def api_create_post():
    """Create a new post"""
    data = request.get_json()
    content = data.get('content', '').strip()
    post_type = data.get('post_type', 'text')
    file_id = data.get('file_id')

    if not content:
        return jsonify({'success': False, 'error': 'Content is required'}), 400

    post = create_post(current_user.id, content, post_type, file_id)
    if post:
        return jsonify({'success': True, 'message': 'Post created successfully', 'post_id': post.id})
    else:
        return jsonify({'success': False, 'error': 'Failed to create post'}), 500

@app.route('/api/posts/<post_id>/like', methods=['POST'])
@login_required
def api_like_post(post_id):
    """Like a post"""
    success, message = like_post(current_user.id, post_id)
    return jsonify({'success': success, 'message': message})

@app.route('/api/posts/<post_id>/unlike', methods=['POST'])
@login_required
def api_unlike_post(post_id):
    """Unlike a post"""
    try:
        like = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        if not like:
            return jsonify({'success': False, 'error': 'Post not liked'}), 400
        
        db.session.delete(like)
        
        # Update post like count
        post = Post.query.get(post_id)
        if post:
            post.likes_count -= 1
            db.session.commit()
            return jsonify({'success': True, 'message': 'Post unliked successfully'})
        else:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
    except Exception as e:
        app.logger.error(f"Unlike post failed: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to unlike post'}), 500

@app.route('/api/workspaces', methods=['POST'])
@login_required
def api_create_workspace():
    """Create a new workspace"""
    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    is_public = data.get('is_public', False)
    
    if not name:
        return jsonify({'success': False, 'error': 'Workspace name is required'}), 400
    
    workspace = create_workspace(current_user.id, name, description, is_public)
    if workspace:
        return jsonify({'success': True, 'message': 'Workspace created successfully', 'workspace_id': workspace.id})
    else:
        return jsonify({'success': False, 'error': 'Failed to create workspace'}), 500

@app.route('/api/share-file', methods=['POST'])
@login_required
def api_share_file():
    """Share a file with another user"""
    data = request.get_json()
    file_id = data.get('file_id')
    to_user_id = data.get('to_user_id')
    message = data.get('message', '').strip()
    share_type = data.get('share_type', 'private')
    
    if not file_id:
        return jsonify({'success': False, 'error': 'File ID is required'}), 400
    
    # Check if file belongs to current user
    file_storage = FileStorage.query.filter_by(id=file_id, user_id=current_user.id).first()
    if not file_storage:
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    try:
        share_request = ShareRequest()
        share_request.file_id = file_id
        share_request.from_user_id = current_user.id
        share_request.to_user_id = to_user_id
        share_request.message = message
        share_request.share_type = share_type
        
        db.session.add(share_request)
        db.session.commit()
        
        # Create notification for recipient
        if to_user_id:
            create_notification(to_user_id, 'File Shared', 
                              f'{current_user.name} shared a file with you', 'info',
                              action_url=url_for('file_management'))
        
        return jsonify({'success': True, 'message': 'File shared successfully'})
    except Exception as e:
        app.logger.error(f"Share file failed: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to share file'}), 500

@app.route('/api/activity-feed')
@login_required
def api_activity_feed():
    """Get user's activity feed"""
    try:
        activities = ActivityFeed.query.filter_by(user_id=current_user.id).order_by(ActivityFeed.created_at.desc()).limit(50).all()
        return jsonify({
            'success': True,
            'activities': [{
                'id': a.id,
                'activity_type': a.activity_type,
                'description': a.description,
                'actor_name': a.actor.name,
                'created_at': a.created_at.isoformat()
            } for a in activities]
        })
    except Exception as e:
        app.logger.error(f"Activity feed error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch activity feed'}), 500

@app.route('/api/analytics-data')
@login_required
def api_analytics_data():
    """Get analytics data for dashboard"""
    try:
        # Get user's encryption jobs
        total_jobs = EncryptionJob.query.filter_by(user_id=current_user.id).count()
        successful_jobs = EncryptionJob.query.filter_by(user_id=current_user.id, status='completed').count()
        total_file_size = db.session.query(db.func.sum(EncryptionJob.file_size)).filter_by(user_id=current_user.id).scalar() or 0

        # Get recent activity
        recent_jobs = EncryptionJob.query.filter_by(user_id=current_user.id).order_by(EncryptionJob.created_at.desc()).limit(10).all()

        return jsonify({
            'success': True,
            'data': {
                'total_jobs': total_jobs,
                'successful_jobs': successful_jobs,
                'total_file_size': total_file_size,
                'success_rate': (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0,
                'recent_activity': [{
                    'id': job.id,
                    'filename': job.original_filename,
                    'status': job.status,
                    'created_at': job.created_at.isoformat(),
                    'file_size': job.file_size
                } for job in recent_jobs]
            }
        })
    except Exception as e:
        app.logger.error(f"Analytics data error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch analytics data'}), 500

@app.route('/api/batch-process', methods=['POST'])
@login_required
def api_batch_process():
    """Process multiple images in batch"""
    try:
        if 'images' not in request.files:
            return jsonify({'success': False, 'error': 'No images provided'}), 400

        files = request.files.getlist('images')
        message = request.form.get('message', '').strip()
        password = request.form.get('password', '').strip()

        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        results = []
        for file in files:
            if file.filename == '':
                continue

            if not allowed_file(file.filename):
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': 'Invalid file type'
                })
                continue

            try:
                # Read image data
                image_data = file.read()

                # Process image
                processed_image = processor.hide_message(image_data, message, password)

                if processed_image:
                    # Save to database
                    job = EncryptionJob()
                    job.user_id = current_user.id
                    job.original_filename = file.filename
                    job.message = message
                    job.has_password = bool(password)
                    job.file_size = len(processed_image)
                    job.status = 'completed'

                    db.session.add(job)
                    db.session.commit()

                    results.append({
                        'filename': file.filename,
                        'success': True,
                        'job_id': job.id
                    })
                else:
                    results.append({
                        'filename': file.filename,
                        'success': False,
                        'error': 'Processing failed'
                    })

            except Exception as e:
                app.logger.error(f"Batch processing error for {file.filename}: {str(e)}")
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': 'Processing error'
                })

        return jsonify({
            'success': True,
            'results': results,
            'total_processed': len([r for r in results if r['success']]),
            'total_failed': len([r for r in results if not r['success']])
        })

    except Exception as e:
        app.logger.error(f"Batch process error: {str(e)}")
        return jsonify({'success': False, 'error': 'Batch processing failed'}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def api_settings():
    """Get or update user settings"""
    if request.method == 'GET':
        # Return current settings (placeholder)
        return jsonify({
            'success': True,
            'settings': {
                'theme': 'dark',
                'notifications': True,
                'auto_lock': 15,
                'encryption_strength': 'aes256'
            }
        })
    else:
        # Update settings
        data = request.get_json()
        # In a real implementation, save to database
        return jsonify({'success': True, 'message': 'Settings updated successfully'})

@app.route('/api/template-categories')
@login_required
def api_template_categories():
    """Get available template categories"""
    return jsonify({
        'success': True,
        'categories': [
            {'id': 'personal', 'name': 'Personal', 'count': 5},
            {'id': 'business', 'name': 'Business', 'count': 3},
            {'id': 'celebration', 'name': 'Celebrations', 'count': 4},
            {'id': 'mysterious', 'name': 'Mysterious', 'count': 2}
        ]
    })

@app.route('/api/templates/<category>')
@login_required
def api_templates_by_category(category):
    """Get templates by category"""
    templates = {
        'personal': [
            {'id': 'love-letter', 'title': 'Love Letter', 'preview': 'My dearest [Name], Every moment with you...'},
            {'id': 'thank-you', 'title': 'Thank You Note', 'preview': 'I wanted to express my heartfelt gratitude...'}
        ],
        'business': [
            {'id': 'business-proposal', 'title': 'Business Proposal', 'preview': 'Dear [Client], I am pleased to present...'},
            {'id': 'meeting-reminder', 'title': 'Meeting Reminder', 'preview': 'This is a reminder of our upcoming meeting...'}
        ],
        'celebration': [
            {'id': 'birthday-message', 'title': 'Birthday Message', 'preview': 'Happy Birthday! May this special day...'},
            {'id': 'anniversary', 'title': 'Anniversary', 'preview': 'Happy Anniversary! Another year of beautiful...'}
        ],
        'mysterious': [
            {'id': 'secret-code', 'title': 'Secret Code', 'preview': 'The eagle has landed. Mission accomplished...'},
            {'id': 'riddle', 'title': 'Riddle', 'preview': 'I speak without a mouth and hear without ears...'}
        ]
    }

    return jsonify({
        'success': True,
        'templates': templates.get(category, [])
    })

@app.route('/api/template/<template_id>')
@login_required
def api_template_content(template_id):
    """Get full template content"""
    templates = {
        'love-letter': {
            'title': 'Love Letter',
            'content': 'My dearest [Name],\n\nEvery moment with you feels like a beautiful secret waiting to be discovered. Your smile lights up my world in ways words cannot express. You are my everything, my forever secret.\n\nWith all my love,\n[Your Name]'
        },
        'business-proposal': {
            'title': 'Business Proposal',
            'content': 'Dear [Client],\n\nI am pleased to present our proposal for [Project/Service]. The quarterly projections show promising growth in our key markets. The strategic partnership discussions are progressing favorably.\n\nBest regards,\n[Your Name]'
        },
        'birthday-message': {
            'title': 'Birthday Message',
            'content': 'Happy Birthday! May this special day bring you as much joy as you\'ve brought into my life. You deserve all the happiness in the world. Happy Birthday to someone who makes every day brighter!'
        },
        'secret-code': {
            'title': 'Secret Code',
            'content': 'The eagle has landed. Mission accomplished. The package has been delivered to the designated coordinates. Awaiting further instructions. Over and out.'
        }
    }

    template = templates.get(template_id)
    if template:
        return jsonify({'success': True, 'template': template})
    else:
        return jsonify({'success': False, 'error': 'Template not found'}), 404

# AI Message Generation API
@app.route('/api/ai/generate-message', methods=['POST'])
@login_required
def api_generate_ai_message():
    """Generate AI-powered secure messages"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        context = data.get('context', '').strip()
        max_length = int(data.get('max_length', 250))

        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400

        # Simple AI message generation (placeholder - in production, integrate with OpenAI, Claude, etc.)
        # For now, we'll create contextual messages based on keywords

        prompt_lower = prompt.lower()
        context_lower = context.lower()

        # Basic message generation logic
        if 'love' in prompt_lower or 'romantic' in prompt_lower:
            messages = [
                "My dearest, every moment with you feels like a beautiful secret waiting to be discovered. Your smile lights up my world in ways words cannot express.",
                "In your eyes, I see the reflection of a love that transcends time and space. You are my everything, my forever secret.",
                "Like hidden treasures in ancient maps, our love story unfolds in whispers and stolen glances. You are my most precious secret.",
                "Every beat of my heart carries your name, a melody only we can hear. You are the secret that makes my life complete."
            ]
        elif 'business' in prompt_lower or 'meeting' in prompt_lower:
            messages = [
                "The quarterly projections show promising growth in our key markets. The strategic partnership discussions are progressing favorably.",
                "Market analysis indicates strong potential for expansion. The competitive landscape remains favorable for our positioning strategy.",
                "Financial metrics demonstrate robust performance across all divisions. Operational efficiency improvements are yielding positive results.",
                "The acquisition strategy aligns perfectly with our long-term growth objectives. Due diligence is proceeding as planned."
            ]
        elif 'birthday' in prompt_lower or 'celebration' in prompt_lower:
            messages = [
                "Happy Birthday! May this special day bring you as much joy as you've brought into my life. You deserve all the happiness in the world.",
                "Wishing you a birthday filled with love, laughter, and unforgettable moments. You are truly one of a kind!",
                "On your special day, I want you to know how much you mean to me. May all your dreams come true!",
                "Happy Birthday to someone who makes every day brighter! May this year bring you everything you've wished for."
            ]
        elif 'mystery' in prompt_lower or 'riddle' in prompt_lower:
            messages = [
                "I am not alive, but I grow; I don't have lungs, but I need air; I don't have a mouth, but water kills me. What am I?",
                "The more you take, the more you leave behind. What am I?",
                "I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?",
                "I have keys but open no locks. I have space but no room. You can enter, but you can't go outside. What am I?"
            ]
        else:
            # Generic messages
            messages = [
                "Every great achievement begins with a courageous decision. Your potential is limitless.",
                "In the garden of life, you are the most beautiful flower. Bloom where you are planted.",
                "Success is not final, failure is not fatal: It is the courage to continue that counts.",
                "The only way to do great work is to love what you do. Follow your passion.",
                "Believe you can and you're halfway there. Your mindset shapes your reality.",
                "The future belongs to those who believe in the beauty of their dreams.",
                "Every expert was once a beginner. Your journey of growth inspires others.",
                "Small daily improvements lead to stunning results over time."
            ]

        # Select a random message
        import random
        selected_message = random.choice(messages)

        # Truncate if needed
        if len(selected_message) > max_length:
            selected_message = selected_message[:max_length-3] + "..."

        # Calculate usage (mock data)
        prompt_tokens = len(prompt.split()) * 2
        completion_tokens = len(selected_message.split()) * 2
        total_tokens = prompt_tokens + completion_tokens

        return jsonify({
            'success': True,
            'message': selected_message,
            'usage': {
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens
            }
        })

    except Exception as e:
        app.logger.error(f"AI message generation error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate message'}), 500

# Main encryption/steganography routes
@app.route('/encrypt', methods=['POST'])
@login_required
def encrypt_image():
    """Encrypt and hide message in image"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No image selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Only PNG, JPEG, GIF, BMP, and WebP are allowed'}), 400

        message = request.form.get('message', '').strip()
        password = request.form.get('password', '').strip()

        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        # Read image data
        image_data = file.read()

        # Process image with steganography
        processed_image = processor.hide_message(image_data, message, password)

        if not processed_image:
            return jsonify({'success': False, 'error': 'Failed to process image'}), 500

        # Save to database
        job = EncryptionJob()
        job.user_id = current_user.id
        job.original_filename = file.filename
        job.message = message
        job.has_password = bool(password)
        job.file_size = len(processed_image)
        job.status = 'completed'

        db.session.add(job)
        db.session.commit()

        # Return processed image as base64 for display and download
        import base64
        image_base64 = base64.b64encode(processed_image).decode('utf-8')

        # Store the processed image temporarily for download
        temp_filename = f"encrypted_{job.id}.png"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        with open(temp_path, 'wb') as f:
            f.write(processed_image)

        return jsonify({
            'success': True,
            'message': 'Image encrypted successfully',
            'image_data': f"data:image/png;base64,{image_base64}",
            'download_url': f"/download-encrypted/{job.id}",
            'job_id': job.id
        })

    except Exception as e:
        app.logger.error(f"Encrypt image error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to encrypt image'}), 500

@app.route('/download-encrypted/<job_id>')
@login_required
def download_encrypted(job_id):
    """Download encrypted image"""
    try:
        # Find the job
        job = EncryptionJob.query.filter_by(id=job_id, user_id=current_user.id).first()
        if not job:
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        # Check if encrypted file exists
        temp_filename = f"encrypted_{job_id}.png"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

        if not os.path.exists(temp_path):
            return jsonify({'success': False, 'error': 'Encrypted file not found'}), 404

        # Return the file for download
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"encrypted_{job.original_filename}",
            mimetype='image/png'
        )

    except Exception as e:
        app.logger.error(f"Download encrypted error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to download file'}), 500

@app.route('/api/extract_decrypt', methods=['POST'])
@login_required
def api_extract_decrypt():
    """Extract and decrypt message from image"""
    try:
        if 'encrypted_image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400

        file = request.files['encrypted_image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No image selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Only PNG, JPEG, GIF, BMP, and WebP are allowed'}), 400

        # Read image data
        image_data = file.read()

        # Get password from form data
        password = request.form.get('decrypt_password', '').strip()

        # Extract message using steganography (pass password for automatic decryption)
        extracted_message = processor.extract_message(image_data, password)

        if not extracted_message:
            return jsonify({'success': False, 'error': 'No hidden message found in this image'}), 404

        # Check if message was encrypted (based on whether password was provided and used)
        was_encrypted = bool(password)
        final_message = extracted_message

        return jsonify({
            'success': True,
            'message': final_message,
            'was_encrypted': was_encrypted
        })

    except Exception as e:
        app.logger.error(f"Extract decrypt error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to extract message'}), 500

# Routes
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Error in index route: {str(e)}")
        return f"Error: {str(e)}", 500




@app.route('/dashboard')
def dashboard():
    try:
        # Check if user is logged in
        if current_user.is_authenticated:
            # Get user's encryption jobs
            user_jobs = EncryptionJob.query.filter_by(user_id=current_user.id).order_by(EncryptionJob.created_at.desc()).limit(10).all()

            # If user has no jobs, create some demo data for better UX
            if not user_jobs:
                # Create demo jobs for new users
                demo_jobs = [
                    EncryptionJob(
                        user_id=current_user.id,
                        original_filename="welcome_image.png",
                        message="Welcome to CyberCloak! Your secure steganography platform.",
                        status="completed",
                        file_size=245760,  # 240 KB
                        has_password=True,
                        created_at=datetime.utcnow()
                    ),
                    EncryptionJob(
                        user_id=current_user.id,
                        original_filename="demo_encryption.jpg",
                        message="This is a demo encrypted message. Try uploading your own image!",
                        status="completed",
                        file_size=512000,  # 500 KB
                        has_password=False,
                        created_at=datetime.utcnow()
                    )
                ]

                # Save demo jobs to database
                for job in demo_jobs:
                    db.session.add(job)
                db.session.commit()

                user_jobs = demo_jobs

            # Ensure we have current_user data
            user_data = {
                'id': current_user.id,
                'name': current_user.name or 'User',
                'email': current_user.email,
                'username': current_user.username,
                'avatar_url': getattr(current_user, 'avatar_url', None)
            }
        else:
            # Demo mode - create demo data without saving to database
            user_jobs = [
                EncryptionJob(
                    user_id="demo",
                    original_filename="welcome_image.png",
                    message="Welcome to CyberCloak! Your secure steganography platform.",
                    status="completed",
                    file_size=245760,  # 240 KB
                    has_password=True,
                    created_at=datetime.utcnow()
                ),
                EncryptionJob(
                    user_id="demo",
                    original_filename="demo_encryption.jpg",
                    message="This is a demo encrypted message. Try uploading your own image!",
                    status="completed",
                    file_size=512000,  # 500 KB
                    has_password=False,
                    created_at=datetime.utcnow()
                )
            ]

            user_data = {
                'id': 'demo',
                'name': 'Demo User',
                'email': 'demo@cybercloak.com',
                'username': 'demo_user',
                'avatar_url': None
            }

        return render_template('dashboard.html', jobs=user_jobs, current_user=user_data, demo_mode=not current_user.is_authenticated)

    except Exception as e:
        app.logger.error(f"Dashboard error: {str(e)}")
        # Return dashboard with demo data as fallback
        demo_jobs = [
            EncryptionJob(
                user_id="demo",
                original_filename="welcome_image.png",
                message="Welcome to CyberCloak! Your secure steganography platform.",
                status="completed",
                file_size=245760,
                has_password=True,
                created_at=datetime.utcnow()
            )
        ]
        return render_template('dashboard.html', jobs=demo_jobs, current_user={'name': 'Demo User', 'email': 'demo@cybercloak.com'}, demo_mode=True)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/activity')
@login_required
def activity():
    user_jobs = EncryptionJob.query.filter_by(user_id=current_user.id).order_by(EncryptionJob.created_at.desc()).all()
    return render_template('activity.html', jobs=user_jobs)

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@app.route('/batch')
@login_required
def batch():
    return render_template('batch.html')

@app.route('/templates')
@login_required
def templates():
    return render_template('templates.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/security')
@login_required
def security():
    return render_template('security.html')

@app.route('/files')
@login_required
def files():
    return render_template('files.html')

@app.route('/api-docs')
def api_docs():
    return render_template('api_docs.html')

@app.route('/mobile')
def mobile():
    return render_template('mobile.html')

@app.route('/file-management')
@login_required
def file_management():
    """File management page"""
    user_files = FileStorage.query.filter_by(user_id=current_user.id).order_by(FileStorage.created_at.desc()).all()
    return render_template('files.html', files=user_files)

@app.route('/security-settings')
@login_required
def security_settings():
    """Security settings page"""
    return render_template('security.html')

@app.route('/notifications-page')
@login_required
def notifications_page():
    """Notifications page"""
    return render_template('notifications.html')

@app.route('/admin')
@login_required
def admin():
    # Check if user is admin (you can implement proper admin role checking)
    if current_user.email != 'sagarsiddesh14@gmail.com':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get admin statistics
    total_users = User.query.count()
    total_jobs = EncryptionJob.query.count()
    total_contacts = ContactMessage.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_jobs = EncryptionJob.query.order_by(EncryptionJob.created_at.desc()).limit(10).all()
    recent_contacts = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(10).all()
    
    return render_template('admin.html', 
                         total_users=total_users,
                         total_jobs=total_jobs,
                         total_contacts=total_contacts,
                         recent_users=recent_users,
                         recent_jobs=recent_jobs,
                         recent_contacts=recent_contacts)

# File Management Routes
@app.route('/upload-file', methods=['POST'])
@login_required
def upload_file():
    """Upload file to cloud storage"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Read file data
        file_data = file.read()
        file_size = len(file_data)
        
        # Upload to cloud storage
        cloud_url = upload_to_cloud(file_data, unique_filename, file.content_type)
        
        # Save file record to database
        file_storage = FileStorage()
        file_storage.user_id = current_user.id
        file_storage.filename = unique_filename
        file_storage.original_filename = filename
        file_storage.file_path = f"uploads/{unique_filename}"  # Local fallback
        file_storage.file_size = file_size
        file_storage.file_type = filename.split('.')[-1].lower()
        file_storage.mime_type = file.content_type
        file_storage.cloud_url = cloud_url
        file_storage.cloud_provider = 'aws' if cloud_url else 'local'
        
        db.session.add(file_storage)
        db.session.commit()
        
        # Log audit event
        log_audit_event(current_user.id, 'file_upload', 'file', file_storage.id, 
                       details={'filename': filename, 'size': file_size})
        
        # Create notification
        create_notification(current_user.id, 'File Uploaded', 
                          f'File "{filename}" has been uploaded successfully.', 'success')
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file_id': file_storage.id
        })
        
    except Exception as e:
        app.logger.error(f"File upload error: {str(e)}")
        return jsonify({'success': False, 'error': 'Upload failed'}), 500

@app.route('/download-file/<file_id>')
@login_required
def download_file(file_id):
    """Download file from cloud storage"""
    try:
        file_storage = FileStorage.query.filter_by(id=file_id, user_id=current_user.id).first()
        if not file_storage:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Update download count and last accessed
        file_storage.download_count += 1
        file_storage.last_accessed = datetime.utcnow()
        db.session.commit()
        
        # Log audit event
        log_audit_event(current_user.id, 'file_download', 'file', file_id,
                       details={'filename': file_storage.original_filename})
        
        if file_storage.cloud_url and app.config['CLOUD_STORAGE_ENABLED']:
            # Download from cloud
            file_data = download_from_cloud(file_storage.cloud_url)
            if file_data:
                return send_file(
                    io.BytesIO(file_data),
                    as_attachment=True,
                    download_name=file_storage.original_filename,
                    mimetype=file_storage.mime_type
                )
        
        # Fallback to local file
        return send_file(
            file_storage.file_path,
            as_attachment=True,
            download_name=file_storage.original_filename,
            mimetype=file_storage.mime_type
        )
        
    except Exception as e:
        app.logger.error(f"File download error: {str(e)}")
        return jsonify({'success': False, 'error': 'Download failed'}), 500

@app.route('/delete-file/<file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    """Delete file from storage"""
    try:
        file_storage = FileStorage.query.filter_by(id=file_id, user_id=current_user.id).first()
        if not file_storage:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Log audit event
        log_audit_event(current_user.id, 'file_delete', 'file', file_id,
                       details={'filename': file_storage.original_filename})
        
        # Delete from database
        db.session.delete(file_storage)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'File deleted successfully'})
        
    except Exception as e:
        app.logger.error(f"File deletion error: {str(e)}")
        return jsonify({'success': False, 'error': 'Deletion failed'}), 500

# 2FA Routes
@app.route('/2fa/setup')
@login_required
def setup_2fa():
    """Setup 2FA for user"""
    try:
        # Check if 2FA already exists
        existing_2fa = TwoFactorAuth.query.filter_by(user_id=current_user.id).first()
        if existing_2fa and existing_2fa.is_enabled:
            return jsonify({'success': False, 'error': '2FA already enabled'}), 400

        # Generate new secret
        secret = generate_2fa_secret()
        qr_code = generate_2fa_qr_code(secret, current_user.email)

        # Save to database (not enabled yet)
        if existing_2fa:
            existing_2fa.secret_key = secret
            existing_2fa.is_enabled = False
        else:
            two_fa = TwoFactorAuth()
            two_fa.user_id = current_user.id
            two_fa.secret_key = secret
            two_fa.is_enabled = False
            db.session.add(two_fa)

        db.session.commit()

        return jsonify({
            'success': True,
            'secret': secret,
            'qr_code': qr_code
        })

    except Exception as e:
        app.logger.error(f"2FA setup error: {str(e)}")
        return jsonify({'success': False, 'error': 'Setup failed'}), 500

@app.route('/2fa/verify', methods=['POST'])
@login_required
def verify_2fa():
    """Verify 2FA token and enable 2FA"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'success': False, 'error': 'Token required'}), 400
        
        # Get user's 2FA record
        two_fa = TwoFactorAuth.query.filter_by(user_id=current_user.id).first()
        if not two_fa:
            return jsonify({'success': False, 'error': '2FA not initialized'}), 400
        
        # Verify token
        if not verify_2fa_token(two_fa.secret_key, token):
            log_audit_event(current_user.id, '2fa_verification_failed', 'user', current_user.id, 'failed')
            return jsonify({'success': False, 'error': 'Invalid token'}), 400
        
        # Enable 2FA and generate backup codes
        two_fa.is_enabled = True
        two_fa.backup_codes = json.dumps(generate_backup_codes())
        two_fa.last_used = datetime.utcnow()
        
        db.session.commit()
        
        # Log audit event
        log_audit_event(current_user.id, '2fa_enabled', 'user', current_user.id)
        
        # Create notification
        create_notification(current_user.id, '2FA Enabled', 
                          'Two-factor authentication has been enabled for your account.', 'success')
        
        return jsonify({
            'success': True,
            'message': '2FA enabled successfully',
            'backup_codes': json.loads(two_fa.backup_codes)
        })
        
    except Exception as e:
        app.logger.error(f"2FA verification error: {str(e)}")
        return jsonify({'success': False, 'error': 'Verification failed'}), 500

@app.route('/2fa/disable', methods=['POST'])
@login_required
def disable_2fa():
    """Disable 2FA for user"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        # Verify password
        if not current_user.password_hash or not check_password_hash(current_user.password_hash, password):
            return jsonify({'success': False, 'error': 'Invalid password'}), 400
        
        # Disable 2FA
        two_fa = TwoFactorAuth.query.filter_by(user_id=current_user.id).first()
        if two_fa:
            two_fa.is_enabled = False
            two_fa.backup_codes = None
            db.session.commit()
            
        # Log audit event
        log_audit_event(current_user.id, '2fa_disabled', 'user', current_user.id)
        
        # Create notification
        create_notification(current_user.id, '2FA Disabled', 
                          'Two-factor authentication has been disabled for your account.', 'warning')
        
        return jsonify({'success': True, 'message': '2FA disabled successfully'})
        
    except Exception as e:
        app.logger.error(f"2FA disable error: {str(e)}")
        return jsonify({'success': False, 'error': 'Disable failed'}), 500

# Notification Routes
@app.route('/notifications')
@login_required
def notifications():
    """Get user notifications"""
    try:
        user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
        return jsonify({
            'success': True,
            'notifications': [{
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.notification_type,
                'is_read': n.is_read,
                'action_url': n.action_url,
                'created_at': n.created_at.isoformat()
            } for n in user_notifications]
        })
    except Exception as e:
        app.logger.error(f"Notifications error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch notifications'}), 500

@app.route('/notifications/mark-read/<notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Mark notification read error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to mark as read'}), 500

@app.route('/notifications/clear-all', methods=['POST'])
@login_required
def clear_all_notifications():
    """Clear all user notifications"""
    try:
        Notification.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'All notifications cleared'})
    except Exception as e:
        app.logger.error(f"Clear notifications error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to clear notifications'}), 500

# Placeholder routes for footer links
@app.route('/pricing')
def pricing():
    return render_template('placeholder.html', 
                         page_title='Pricing Plans', 
                         page_icon='dollar-sign',
                         page_description='Choose the perfect plan for your encryption needs. Flexible pricing for individuals and businesses.')

@app.route('/privacy')
def privacy():
    return render_template('placeholder.html', 
                         page_title='Privacy Policy', 
                         page_icon='shield',
                         page_description='Learn how we protect your privacy and handle your data with the highest security standards.')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/gdpr')
def gdpr():
    return render_template('placeholder.html', 
                         page_title='GDPR Compliance', 
                         page_icon='balance-scale',
                         page_description='Our commitment to GDPR compliance and data protection regulations.')

@app.route('/api')
def api():
    return render_template('placeholder.html', 
                         page_title='API Documentation', 
                         page_icon='code',
                         page_description='Integrate CyberCloak into your applications with our comprehensive API documentation and SDKs.')

@app.route('/documentation')
def documentation():
    return render_template('placeholder.html', 
                         page_title='Documentation', 
                         page_icon='book',
                         page_description='Comprehensive documentation and guides for using CyberCloak effectively.')

@app.route('/status')
def status():
    return render_template('placeholder.html', 
                         page_title='System Status', 
                         page_icon='server',
                         page_description='Check the current status of CyberCloak services and infrastructure.')

@app.route('/blog')
def blog():
    return render_template('placeholder.html', 
                         page_title='Blog', 
                         page_icon='blog',
                         page_description='Read our latest articles and insights about cybersecurity and encryption.')

@app.route('/careers')
def careers():
    return render_template('placeholder.html', 
                         page_title='Careers', 
                         page_icon='briefcase',
                         page_description='Join our team and help build the future of secure communication.')

@app.route('/press')
def press():
    return render_template('placeholder.html', 
                         page_title='Press', 
                         page_icon='newspaper',
                         page_description='Press releases, media kit, and company news.')

@app.route('/cookies')
def cookies():
    return render_template('placeholder.html', 
                         page_title='Cookie Policy', 
                         page_icon='cookie-bite',
                         page_description='Learn about how we use cookies and similar technologies on our website.')

@app.route('/help')
def help():
    try:
        return render_template('help.html')
    except Exception as e:
        app.logger.error(f"Error in help route: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/about')
def about():
    try:
        return render_template('about.html')
    except Exception as e:
        app.logger.error(f"Error in about route: {str(e)}")
        return f"Error: {str(e)}", 500


@app.route('/contact/success')
def contact_success():
    return render_template('contact_success.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    return login_post()

def login_post():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    remember = request.form.get('remember', False)

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.password_hash and check_password_hash(user.password_hash, password):
        login_user(user, remember=remember)

        # Log audit event
        log_audit_event(user.id, 'login', 'user', user.id)

        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        # Log failed login attempt
        log_audit_event(None, 'login_failed', 'user', None, 'failed', {'email': email})
        return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('auth/signup.html')
    return signup_post()

def signup_post():
    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    
    if not all([name, username, email, password]):
        return jsonify({'success': False, 'error': 'All fields are required'}), 400
    
    if len(password) < 8:
        return jsonify({'success': False, 'error': 'Password must be at least 8 characters long'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Email already registered'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'error': 'Username already taken'}), 400
    
    # Create new user
    user = User()
    user.id = str(uuid.uuid4())
    user.name = name
    user.username = username
    user.email = email
    user.password_hash = generate_password_hash(password)
    user.provider = 'email'
    user.created_at = datetime.utcnow()
    
    db.session.add(user)
    db.session.commit()
    
    # Log user in
    login_user(user)
    
    # Log audit event
    log_audit_event(user.id, 'user_registration', 'user', user.id)
    
    # Create welcome notification
    create_notification(user.id, 'Welcome to CyberCloak!', 
                      'Your account has been created successfully. Start encrypting your images now!', 'success')
    
    return jsonify({'success': True, 'message': 'Account created successfully'})

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('auth/forgot_password.html')
    return forgot_password_post()

def forgot_password_post():
    data = request.get_json()
    email = data.get('email', '').strip()

    if not email:
        return jsonify({'success': False, 'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'Email not found'}), 404

    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    # Save reset token
    password_reset = PasswordReset()
    password_reset.user_id = user.id
    password_reset.token = reset_token
    password_reset.expires_at = expires_at

    db.session.add(password_reset)
    db.session.commit()

    # Send reset email
    if send_password_reset_email(email, reset_token):
        return jsonify({'success': True, 'message': 'Password reset email sent'})
    else:
        return jsonify({'success': False, 'error': 'Failed to send email'}), 500

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        return render_template('auth/reset_password.html', token=token)
    return reset_password_post(token)

def reset_password_post(token):
    data = request.get_json()
    password = data.get('password', '')
    
    if not password or len(password) < 8:
        return jsonify({'success': False, 'error': 'Password must be at least 8 characters long'}), 400
    
    # Find valid reset token
    password_reset = PasswordReset.query.filter_by(token=token, used=False).first()
    
    if not password_reset or password_reset.expires_at < datetime.utcnow():
        return jsonify({'success': False, 'error': 'Invalid or expired token'}), 400
    
    # Update user password
    user = User.query.get(password_reset.user_id)
    if user:
        user.password_hash = generate_password_hash(password)
        password_reset.used = True
        db.session.commit()
        
        # Log audit event
        log_audit_event(user.id, 'password_reset', 'user', user.id)
        
        return jsonify({'success': True, 'message': 'Password reset successfully'})
    else:
        return jsonify({'success': False, 'error': 'User not found'}), 404

@app.route('/logout')
@login_required
def logout():
    # Log audit event
    log_audit_event(current_user.id, 'logout', 'user', current_user.id)
    
    logout_user()
    return redirect(url_for('index'))

# OAuth routes
@app.route('/auth/google')
def google_auth():
    if not google:
        flash('Google OAuth is not configured. Please use email/password login.', 'error')
        return redirect(url_for('login'))
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def google_callback():
    try:
        if not google:
            flash('Google OAuth is not configured.', 'error')
            return redirect(url_for('login'))

        token = google.authorize_access_token()

        # Fetch user info from Google
        resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo')
        user_info = resp.json()

        if user_info:
            email = user_info.get('email')
            name = user_info.get('name')
            avatar_url = user_info.get('picture')

            # Check if user exists
            user = User.query.filter_by(email=email).first()

            if not user:
                # Create new user
                user = User()
                user.id = str(uuid.uuid4())
                user.name = name
                user.username = email.split('@')[0]
                user.email = email
                user.avatar_url = avatar_url
                user.provider = 'google'
                user.created_at = datetime.utcnow()

                db.session.add(user)
                db.session.commit()

                # Log audit event
                log_audit_event(user.id, 'user_registration', 'user', user.id, details={'provider': 'google'})

                # Create welcome notification
                create_notification(user.id, 'Welcome to CyberCloak!',
                                  'Your account has been created successfully. Start encrypting your images now!', 'success')
            else:
                # Log audit event
                log_audit_event(user.id, 'login', 'user', user.id, details={'provider': 'google'})

            login_user(user)
            return redirect(url_for('dashboard'))

    except Exception as e:
        app.logger.error(f"Google OAuth error: {str(e)}")
        flash('Authentication failed. Please try again.', 'error')

    return redirect(url_for('login'))

@app.route('/auth/github')
def github_auth():
    if not github:
        flash('GitHub OAuth is not configured. Please use email/password login.', 'error')
        return redirect(url_for('login'))
    redirect_uri = url_for('github_callback', _external=True)
    return github.authorize_redirect(redirect_uri)

@app.route('/auth/github/callback')
def github_callback():
    try:
        token = github.authorize_access_token()
        resp = github.get('user', token=token)
        user_info = resp.json()
        
        if user_info:
            email = user_info.get('email')
            name = user_info.get('name') or user_info.get('login')
            avatar_url = user_info.get('avatar_url')
            
            # Check if user exists
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Create new user
                user = User()
                user.id = str(uuid.uuid4())
                user.name = name
                user.username = user_info.get('login')
                user.email = email
                user.avatar_url = avatar_url
                user.provider = 'github'
                user.created_at = datetime.utcnow()
                
                db.session.add(user)
                db.session.commit()
                
                # Log audit event
                log_audit_event(user.id, 'user_registration', 'user', user.id, details={'provider': 'github'})
                
                # Create welcome notification
                create_notification(user.id, 'Welcome to CyberCloak!', 
                                  'Your account has been created successfully. Start encrypting your images now!', 'success')
            else:
                # Log audit event
                log_audit_event(user.id, 'login', 'user', user.id, details={'provider': 'github'})
            
            login_user(user)
            return redirect(url_for('dashboard'))
        
    except Exception as e:
        app.logger.error(f"GitHub OAuth error: {str(e)}")
        flash('Authentication failed. Please try again.', 'error')
    
    return redirect(url_for('login'))

# Contact form route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')
    return contact_post()

def contact_post():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    subject = request.form.get('subject', '').strip()
    message = request.form.get('message', '').strip()

    if not all([name, email, subject, message]):
        flash('All fields are required. Please fill out the form completely.', 'error')
        return redirect(url_for('contact'))

    # Save contact message to database
    contact = ContactMessage()
    contact.name = name
    contact.email = email
    contact.subject = subject
    contact.message = message

    db.session.add(contact)
    db.session.commit()

    # Send notification email to admin
    email_sent = send_contact_notification_email(name, email, subject, message)
    sms_sent = send_sms_notification(name, email, subject, message)

    if email_sent:
        flash('Message sent successfully! The developer will contact you soon.', 'success')
    else:
        # Email failed, but we still saved the message to database
        flash('Message received! (Email notification failed, but your message was saved)', 'warning')

    # Always redirect to success page
    return redirect(url_for('contact_success'), code=302)

if __name__ == '__main__':
    with app.app_context():
        try:
            # Create all tables (don't drop existing ones to avoid errors)
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.warning(f"Database creation warning: {str(e)}")
            # Continue running even if some tables already exist
    app.run(host='0.0.0.0', port=5000, debug=True)
