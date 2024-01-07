from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class MemberHarian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    jenis_kelamin = db.Column(db.String(10))
    alamat = db.Column(db.String(200))

    def __init__(self, nama, jenis_kelamin, alamat):
        self.nama = nama
        self.jenis_kelamin = jenis_kelamin
        self.alamat = alamat

class MemberBulanan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    jenis_kelamin = db.Column(db.String(10))
    alamat = db.Column(db.String(200))
    nomor_hp = db.Column(db.String(15))

    def __init__(self, nama, jenis_kelamin, alamat, nomor_hp):
        self.nama = nama
        self.jenis_kelamin = jenis_kelamin
        self.alamat = alamat
        self.nomor_hp = nomor_hp


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Integer, default=0)

    def __init__(self, username, password, is_admin=0):
        self.username = username
        self.set_password(password)
        self.is_admin = is_admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return self.password_hash == password