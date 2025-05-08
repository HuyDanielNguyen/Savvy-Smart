import uuid
import bcrypt
import pandas as pd
from datetime import date
import streamlit as st

def generate_uuid():
    return str(uuid.uuid4())

class User:
    def __init__(self, id, email, username, password=None, avatar_url=None, created_at=None):
        self.id = id
        self.email = email
        self.username = username
        self.password_hash = None
        self.avatar_url = avatar_url or "https://icons.iconarchive.com/icons/iconarchive/wild-camping/512/Bird-Owl-icon.png"
        self.created_at = created_at
        if password:
            self.password_hash = self.hash_password(password)

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    @classmethod
    def from_session(cls):
        if "user" in st.session_state:
            return cls(**st.session_state.user)
        return None

class Transaction:
    def __init__(self, id, user_id, amount, category, detail, transaction_type, date):
        self.id = id
        self.user_id = user_id
        self.amount = amount
        self.category = category
        self.detail = detail
        self.transaction_type = transaction_type
        self.date = date
