from datetime import datetime
from app import db
import enum


class TaskStatus(enum.Enum):
    """Task status enum"""
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class TaskPriority(enum.Enum):
    """Task priority enum"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'


# Association table for many-to-many relationship between Task and Tag
task_tags = db.Table('task_tags',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class Task(db.Model):
    """Task model"""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default=TaskStatus.PENDING.value, nullable=False)
    priority = db.Column(db.String(50), default=TaskPriority.MEDIUM.value, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='tasks')
    tags = db.relationship('Tag', secondary=task_tags, back_populates='tasks', lazy='dynamic')

    def __repr__(self):
        return f'<Task {self.id}: {self.title}>'

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status != TaskStatus.COMPLETED.value:
            return datetime.utcnow() > self.due_date
        return False

    @property
    def is_completed(self):
        """Check if task is completed"""
        return self.status == TaskStatus.COMPLETED.value

    def mark_completed(self):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()

    def add_tag(self, tag):
        """Add tag to task"""
        # Simply append - SQLAlchemy handles duplicates in many-to-many
        self.tags.append(tag)

    def remove_tag(self, tag):
        """Remove tag from task"""
        self.tags.remove(tag)

    def has_tag(self, tag):
        """Check if task has tag"""
        # For checking, use a safer approach that works with sessions
        try:
            return tag in self.tags.all()
        except:
            # If not in session, check the collection directly
            return tag in self.tags

    def to_dict(self, include_user=False, include_tags=True):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_overdue': self.is_overdue,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }

        if include_user and self.user:
            data['user'] = self.user.to_dict(include_role=False)

        if include_tags:
            data['tags'] = [tag.to_dict() for tag in self.tags.all()]

        return data
