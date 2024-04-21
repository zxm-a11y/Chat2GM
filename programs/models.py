# from flask_sqlalchemy import SQLAlchemy
#
# db = SQLAlchemy()
#
# class ChatHistory(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     message = db.Column(db.String(500), nullable=False)
#     response = db.Column(db.String(500), nullable=True)
#     timestamp = db.Column(db.DateTime, server_default=db.func.now())

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, server_default=db.func.now())
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    response = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
