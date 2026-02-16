import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer(), primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    file_url = db.Column(db.Text(), nullable=False)
    image_url = db.Column(db.Text(), nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, title, description, content, file_url, image_url):
        super().__init__()
        self.title = title
        self.description = description
        self.content = content
        self.file_url = file_url
        self.image_url = image_url
    
    @staticmethod
    def to_dict(news):
        _ = {
            "id": news.id,
            "title": news.title,
            "description": news.description,
            "content": news.content,
            "file_url": news.file_url,
            "image_url": news.image_url,
            "created_at": str(news.created_at)
        }
        return _
