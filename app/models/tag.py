from datetime import datetime
from app import db
from app.models.task import task_tags


class Tag(db.Model):
    """Tag model for categorizing tasks"""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    color = db.Column(db.String(7), default='#808080')  # Hex color code
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tasks = db.relationship('Task', secondary=task_tags, back_populates='tags', lazy='dynamic')

    def __repr__(self):
        return f'<Tag {self.name}>'

    @property
    def task_count(self):
        """Get number of tasks with this tag"""
        return self.tasks.count()

    def to_dict(self, include_task_count=True):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_task_count:
            data['task_count'] = self.task_count

        return data
