from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # For email/password auth
    avatar_url = db.Column(db.String(200))
    provider = db.Column(db.String(20), nullable=True)  # 'google', 'github', or 'email'
    provider_id = db.Column(db.String(100), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    encryption_jobs = db.relationship('EncryptionJob', backref='user', lazy=True, cascade='all, delete-orphan')
    contact_messages = db.relationship('ContactMessage', backref='user', lazy=True, cascade='all, delete-orphan')
    stored_files = db.relationship('FileStorage', backref='user', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True, cascade='all, delete-orphan')
    two_factor_auth = db.relationship('TwoFactorAuth', backref='user', lazy=True, cascade='all, delete-orphan', uselist=False)
    profile = db.relationship('UserProfile', backref='user', lazy=True, cascade='all, delete-orphan', uselist=False)
    posts = db.relationship('Post', backref='user', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='user', lazy=True, cascade='all, delete-orphan')
    post_likes = db.relationship('PostLike', backref='user', lazy=True, cascade='all, delete-orphan')
    comment_likes = db.relationship('CommentLike', backref='user', lazy=True, cascade='all, delete-orphan')
    following = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy=True, cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys='Follow.following_id', backref='following', lazy=True, cascade='all, delete-orphan')
    owned_workspaces = db.relationship('Workspace', backref='owner', lazy=True, cascade='all, delete-orphan')
    workspace_memberships = db.relationship('WorkspaceMember', backref='user', lazy=True, cascade='all, delete-orphan')
    collaboration_sessions = db.relationship('CollaborationSession', backref='user', lazy=True, cascade='all, delete-orphan')
    sent_share_requests = db.relationship('ShareRequest', foreign_keys='ShareRequest.from_user_id', backref='from_user', lazy=True, cascade='all, delete-orphan')
    received_share_requests = db.relationship('ShareRequest', foreign_keys='ShareRequest.to_user_id', backref='to_user', lazy=True, cascade='all, delete-orphan')
    activity_feed = db.relationship('ActivityFeed', foreign_keys='ActivityFeed.user_id', backref='user', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('ActivityFeed', foreign_keys='ActivityFeed.actor_id', backref='actor', lazy=True, cascade='all, delete-orphan')

class EncryptionJob(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    encrypted_filename = db.Column(db.String(255))
    message = db.Column(db.Text)
    has_password = db.Column(db.Boolean, default=False)
    file_size = db.Column(db.Integer)
    security_score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed

class ContactMessage(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='unread')  # unread, read, replied

class PasswordReset(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FileStorage(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    is_encrypted = db.Column(db.Boolean, default=False)
    encryption_key = db.Column(db.String(500), nullable=True)
    cloud_provider = db.Column(db.String(50), default='local')  # local, aws, gcp, azure
    cloud_url = db.Column(db.String(500), nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    download_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

class FileShare(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = db.Column(db.String(36), db.ForeignKey('file_storage.id'), nullable=False)
    shared_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    shared_with = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)  # null for public shares
    share_token = db.Column(db.String(255), nullable=False, unique=True)
    share_type = db.Column(db.String(20), nullable=False)  # public, private, password_protected
    password_hash = db.Column(db.String(255), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    max_downloads = db.Column(db.Integer, nullable=True)
    download_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    file = db.relationship('FileStorage', backref='shares')

class AuditLog(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # login, logout, file_upload, file_download, etc.
    resource_type = db.Column(db.String(50), nullable=True)  # file, user, system
    resource_id = db.Column(db.String(36), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON string with additional details
    status = db.Column(db.String(20), default='success')  # success, failed, warning
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

class TwoFactorAuth(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, unique=True)
    secret_key = db.Column(db.String(32), nullable=False)
    backup_codes = db.Column(db.Text, nullable=True)  # JSON array of backup codes
    is_enabled = db.Column(db.Boolean, default=False)
    last_used = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

class Notification(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # info, success, warning, error
    is_read = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.String(500), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

# Social Features Models
class UserProfile(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, unique=True)
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    social_links = db.Column(db.Text, nullable=True)  # JSON with social media links
    is_public = db.Column(db.Boolean, default=True)
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

class Follow(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    follower_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    following_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id', name='unique_follow'),)

class Post(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(20), nullable=False)  # text, image, file, achievement
    file_id = db.Column(db.String(36), db.ForeignKey('file_storage.id'), nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    file = db.relationship('FileStorage', backref='posts')

class PostLike(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.String(36), db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    post = db.relationship('Post', backref='likes')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_post_like'),)

class Comment(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.String(36), db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.String(36), db.ForeignKey('comment.id'), nullable=True)  # For replies
    content = db.Column(db.Text, nullable=False)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    post = db.relationship('Post', backref='comments')
    parent = db.relationship('Comment', remote_side=[id], backref='replies')

class CommentLike(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.String(36), db.ForeignKey('comment.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    comment = db.relationship('Comment', backref='likes')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='unique_comment_like'),)

# Collaboration Features
class Workspace(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    members_count = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = db.relationship('WorkspaceMember', backref='workspace', cascade='all, delete-orphan')

class WorkspaceMember(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = db.Column(db.String(36), db.ForeignKey('workspace.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # owner, admin, member, viewer
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('workspace_id', 'user_id', name='unique_workspace_member'),)

class CollaborationSession(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = db.Column(db.String(36), db.ForeignKey('workspace.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    file_id = db.Column(db.String(36), db.ForeignKey('file_storage.id'), nullable=True)
    session_type = db.Column(db.String(20), nullable=False)  # encryption, decryption, steganography
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    workspace = db.relationship('Workspace', backref='collaboration_sessions')
    file = db.relationship('FileStorage', backref='collaboration_sessions')

# Sharing and Social Features
class ShareRequest(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = db.Column(db.String(36), db.ForeignKey('file_storage.id'), nullable=False)
    from_user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)  # null for public
    message = db.Column(db.Text, nullable=True)
    share_type = db.Column(db.String(20), nullable=False)  # public, private, workspace
    expires_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    file = db.relationship('FileStorage', backref='share_requests')

class ActivityFeed(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # file_upload, file_share, post_created, etc.
    actor_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    target_id = db.Column(db.String(36), nullable=True)  # ID of the target resource
    target_type = db.Column(db.String(50), nullable=True)  # file, post, comment, etc.
    description = db.Column(db.Text, nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    