import os
from sqlalchemy import Column, String, Integer, Text, ForeignKey, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
from flask_migrate import Migrate

database_name = os.environ.get('TABLE_NAME')
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')
database_path = "postgresql://{}:{}@{}/{}".format(
    user, password, "localhost:5432", database_name
)

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Migrate(app, db)
        
        
"""
Db Models - start with base
"""
class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    
    # Base methods to use throughout
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def rollback(self):
        db.session.rollback()

"""
Article

"""
class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    article_link = Column(String(250), nullable=False)
    tags = Column(String(250), nullable=False)
    publisher_id = Column(Integer, ForeignKey("publishers.id"))
    author_id = Column(Integer, ForeignKey("authors.id"))

    
        
    def __init__(self, title,
                 publisher_id, author_id, tags, article_link):
        self.title = title
        self.publisher_id = publisher_id
        self.author_id = author_id
        self.tags = tags
        self.article_link = article_link
        

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'publisher_id': self.publisher_id,
            'author_id': self.author_id,
            'tags': self.tags,
            'article_link': self.article_link
            }
        
    def format_short(self):
        return {
            'id': self.id,
            'title': self.title,
            'tags': self.tags
            }
        
    

"""
Author

"""
class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    names = Column(String(80), nullable=False)
    lastname = Column(String(50), nullable=False)
    articles = db.relationship('Article', backref='authors',
                               cascade='all, delete-orphan')

    def __init__(self, names, lastname):
        self.names = names
        self.lastname = lastname
        self.articles = []
    

    def format(self):
        return {
            'id': self.id,
            'full_name': f'{self.names}  {self.lastname}',
            'articles': [{"article_id" : article.id, "title": article.title} 
                         for article in self.articles]
            }
        
    def format_short(self):
        return {
            'id': self.id,
            'full_name': f'{self.names}  {self.lastname}',
            }
        
"""
Publisher

"""
class Publisher(Base):
    __tablename__ = 'publishers'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    company_link = Column(String(120), nullable=False)
    articles = db.relationship('Article', backref='publishers',
                               cascade='all, delete-orphan')

    def __init__(self, name, company_link):
        self.name = name
        self.company_link = company_link
        self.articles = []
    

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'company_link': self.company_link,
            'articles': [{"article_id" : article.id, "title": article.title} 
                         for article in self.articles]
            }
        
    def format_short(self):
        return {
            'id': self.id,
            'name': self.name
            }

