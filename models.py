from sqlalchemy import Column, DateTime, Integer, String, Float, ForeignKey, Table, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Association table for many-to-many relationship between users and expenses
user_expenses = Table(
    'user_expenses', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('expense_id', Integer, ForeignKey('expenses.id'), primary_key=True),
    Column('split_amount', Float, nullable=False)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    mobile = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    token = Column(String, nullable=True)

    expenses = relationship("Expense", secondary=user_expenses, back_populates="participants")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    split_method = Column(String, nullable=False)  # 'equal', 'exact', or 'percentage'
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now(), nullable=False)

    participants = relationship("User", secondary=user_expenses, back_populates="expenses")
