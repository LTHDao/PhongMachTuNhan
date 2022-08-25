from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from phongmach import db
from datetime import datetime
from enum import Enum as UserEnum
from flask_login import UserMixin


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(UserEnum):
    ADMIN = 1
    NURSE = 2
    USER = 3


class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False)
    phone_number = Column(Integer, nullable=True)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    activate = Column(Boolean, default=True)
    joined_date = Column(DateTime, default=datetime.now())
    avatar = Column(String(100))
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    registration = relationship('RegistrationForm', backref='user', lazy=True)

    def __str__(self):
        return self.name


class Unit(BaseModel):
    name = Column(String(20), nullable=False)
    medicine = relationship('Medicine', backref='unit', lazy=True)

    def __str__(self):
        return self.name


class Medicine(BaseModel):
    name = Column(String(50), nullable=False)
    uses = Column(String(250))
    ingredients = Column(String(250))
    dosage = Column(String(250))
    price = Column(Float, default=0)
    image = Column(String(100))
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now())
    unit_id = Column(Integer, ForeignKey(Unit.id), nullable=False)
    detail_medicine = relationship('ChiTietPhieuKham', backref='medicine', lazy=True)

    def __str__(self):
        return self.name


class Policy(BaseModel):
    max_patient = Column(Integer)
    max_money = Column(Float)
    created_date = Column(DateTime, default=datetime.now())
    receipt = relationship('Receipt', backref='policy', lazy=True, uselist=False)
    medicine = relationship('PhieuKham', backref='policy', lazy=True)


class ListPatient(BaseModel):
    date = Column(DateTime, nullable=True)
    created_date = Column(DateTime, default=datetime.now())
    regis = relationship('RegistrationForm', backref='list_patient', lazy=True)

    def __str__(self):
        return self.date


class RegistrationForm(BaseModel):
    name_patient = Column(String(50), nullable=False)
    gender = Column(String(10), nullable=False)
    phone_number = Column(String(11), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    created_date = Column(DateTime, default=datetime.now())
    booking_date = Column(DateTime, nullable=False)
    address = Column(String(100), nullable=False)
    phieukham = relationship('PhieuKham', backref='RegistrationForm', lazy=True, uselist=False)
    list_id = Column(Integer, ForeignKey(ListPatient.id), nullable=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    def __str__(self):
        return self.name_patient


class PhieuKham(BaseModel):
    __tablename__ = 'phieukham'

    created_date = Column(DateTime, default=datetime.now())
    symptom = Column(String(100))
    predict = Column(String(100))
    detail = relationship('ChiTietPhieuKham', backref='phieukham', lazy=True)
    regis_id = Column(Integer, ForeignKey(RegistrationForm.id), nullable=False)
    policy_id = Column(Integer, ForeignKey(Policy.id), nullable=False)
    receipt = relationship('Receipt', backref='phieukham', lazy=True, uselist=False)

    def __str__(self):
        return self.name


class ChiTietPhieuKham(db.Model):
    quantity = Column(Integer, default=0)
    dosage = Column(String(250))
    phieukham_id = Column(Integer, ForeignKey(PhieuKham.id), nullable=False, primary_key=True)
    medicine_id = Column(Integer, ForeignKey(Medicine.id), nullable=False, primary_key=True)


class Receipt(BaseModel):
    money_default = Column(Float, nullable=False)
    money_medicines = Column(Float, nullable=False)
    total_money = Column(Float, default=money_medicines + money_default, nullable=True)
    phieukham_id = Column(Integer, ForeignKey(PhieuKham.id), nullable=False)
    policy_id = Column(Integer, ForeignKey(Policy.id), nullable=False)


if __name__ == '__main__':
    db.create_all()
