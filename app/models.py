from flask import Flask, request, jsonify
from typing import List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from marshmallow import ValidationError
from datetime import datetime
# from app import db


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)


#=== MODELS====

user_skills = db.Table(
    'user_skills',
    db.metadata,
    db.Column('user_id', db.ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),  # Reference to users.id
    db.Column('skill_id', db.ForeignKey('skills.id', ondelete="CASCADE"), primary_key=True)  # Reference to skills.id
)

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    # username: Mapped[str] = mapped_column(db.String(50), nullable=False)
    firstname: Mapped[str] = mapped_column(db.String(50), nullable=False)
    lastname: Mapped[str] = mapped_column(db.String(50), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    rating: Mapped[float] = mapped_column(db.Float, default=0)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)

    transactions: Mapped[List['Transaction']] = db.Relationship(back_populates='requester')
    skills: Mapped[List['Skill']] = db.Relationship(secondary=user_skills, back_populates='users')
    listings: Mapped[List['Listing']] = db.Relationship(back_populates='user')
    reviews_given: Mapped[List['Review']] = db.Relationship(foreign_keys='Review.reviewer_id', back_populates='reviewer')
    reviews_received: Mapped[List['Review']] = db.Relationship(foreign_keys='Review.reviewee_id', back_populates='reviewee')

    profile: Mapped['Profile'] = db.Relationship(back_populates='user', uselist=False)


    
class Skill(Base):
    __tablename__ = 'skills'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    description: Mapped[str] = mapped_column(db.String(250), nullable=True)

# many-to-many with users
    users: Mapped[List['User']] = db.Relationship(secondary=user_skills, back_populates='skills')


    
    
class Listing(Base):
    __tablename__ = 'listings'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[str] = mapped_column(db.String(500), nullable=True)
    city: Mapped[str] = mapped_column(db.String(100), nullable=False)  # City field
    state: Mapped[str] = mapped_column(db.String(100), nullable=False)  # State field
    zip_code: Mapped[str] = mapped_column(db.String(10), nullable=False)  # ZIP Code
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    type: Mapped[str] = mapped_column(db.Enum('job', 'skill_exchange'), nullable=False)  # New column for type
    offered_skill: Mapped[int] = mapped_column(db.ForeignKey('skills.id'), nullable=True)
    wanted_skill: Mapped[int] = mapped_column(db.ForeignKey('skills.id'), nullable=True)
    image: Mapped[str] = mapped_column(db.String(255), nullable=True)  # Path to the uploaded image

    user: Mapped['User'] = db.Relationship(back_populates='listings')
    transactions: Mapped[List['Transaction']] = db.Relationship(back_populates='listing')


    
class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(db.ForeignKey('listings.id'))
    requester_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    status: Mapped[str] = mapped_column(db.Enum('pending', 'completed', 'cancelled'), default='pending')
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)

    listing: Mapped['Listing'] = db.Relationship(back_populates='transactions')
    requester: Mapped['User'] = db.Relationship(back_populates='transactions')

    
    
class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True)
    reviewer_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    reviewee_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    transaction_id: Mapped[int] = mapped_column(db.ForeignKey('transactions.id'))
    rating: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(db.String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)

    reviewer: Mapped['User'] = db.Relationship(foreign_keys=[reviewer_id], back_populates='reviews_given')
    reviewee: Mapped['User'] = db.Relationship(foreign_keys=[reviewee_id], back_populates='reviews_received')



class Profile(Base):
    __tablename__ = 'profiles'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'), unique=True)  # One-to-one relationship with User
    full_name: Mapped[str] = mapped_column(db.String(100), nullable=True)  # fullName
    email: Mapped[str] = mapped_column(db.String(100), nullable=True)  # email
    phone: Mapped[str] = mapped_column(db.String(20), nullable=True)  # phone
    profile_picture: Mapped[str] = mapped_column(db.String(255), nullable=True)  # Store file name of the uploaded profile picture

    city: Mapped[str] = mapped_column(db.String(100), nullable=True)  # City
    state: Mapped[str] = mapped_column(db.String(100), nullable=True)  # State
    zip_code: Mapped[str] = mapped_column(db.String(20), nullable=True)  # ZIP code

    social_links: Mapped[dict] = mapped_column(db.JSON, nullable=True)  # socialLinks as a JSON field
    account_type = Column(db.String(30), nullable=False, default='regular')
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    bio: Mapped[str] = mapped_column(db.Text, nullable=True) 

    user: Mapped['User'] = db.Relationship(back_populates='profile')  # Relationship with the User model

class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'), nullable=False)
    recipient_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    listing_id: Mapped[int] = mapped_column(db.ForeignKey('listings.id'), nullable=False)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    label = db.Column(db.String(50), nullable=True)  # Optional label like "Job Inquiry" or "Skill Exchange"
    reply_to_id: Mapped[int] = mapped_column(db.ForeignKey('messages.id'), nullable=True)

    sender: Mapped['User'] = db.relationship("User", foreign_keys=[sender_id])
    recipient: Mapped['User'] = db.relationship("User", foreign_keys=[recipient_id])
    listing: Mapped['Listing'] = db.relationship("Listing", foreign_keys=[listing_id])
    
    
    reply_to: Mapped['Message'] = db.relationship("Message", remote_side=[id])  # Correct relationship setup