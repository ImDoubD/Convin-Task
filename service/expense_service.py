from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import Expense, User, user_expenses
from schemas.expense_schema import ExpenseParticipant, ExpenseResponse, UserExpenseListResponse, UserExpenseResponse
from sqlalchemy import func

# Add expense with different split methods
def add_expense(data: dict, db: Session):
    created_by_id = data.get("created_by_id")
    description = data.get("description")
    total_amount = data.get("total_amount")
    split_method = data.get("split_method")
    split_list = data.get("split_list")

    participants = []  

    if split_method == "equal":
        # Equal split: Divide total_amount equally among all participants
        num_participants = len(split_list)
        split_amount = total_amount / num_participants

        new_expense = Expense(
            description=description,
            total_amount=total_amount,
            split_method=split_method,
            created_by=created_by_id
        )
        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)

        for participant in split_list:
            db.execute(
                user_expenses.insert().values(
                    user_id=participant["user_id"],
                    expense_id=new_expense.id,
                    split_amount=split_amount
                )
            )
            participants.append(ExpenseParticipant(user_id=participant["user_id"], split_amount=split_amount))  # Add participant details
        db.commit()

    elif split_method == "exact":
        # Exact split: Check if the sum of split amounts equals total_amount
        split_total = sum(item['split_amount'] for item in split_list)
        if split_total != total_amount:
            raise HTTPException(status_code=400, detail="Split amounts do not sum up to total amount.")
        
        new_expense = Expense(
            description=description,
            total_amount=total_amount,
            split_method=split_method,
            created_by=created_by_id
        )
        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)

        for participant in split_list:
            db.execute(
                user_expenses.insert().values(
                    user_id=participant["user_id"],
                    expense_id=new_expense.id,
                    split_amount=participant["split_amount"]
                )
            )
            participants.append(ExpenseParticipant(user_id=participant["user_id"], split_amount=participant["split_amount"]))  # Add participant details
        db.commit()

    elif split_method == "percentage":
        # Percentage split: Check if the sum of percentages equals 100%
        total_percentage = sum(item['split_amount'] for item in split_list)
        if total_percentage != 100:
            raise HTTPException(status_code=400, detail="Split percentages do not add up to 100.")
        
        new_expense = Expense(
            description=description,
            total_amount=total_amount,
            split_method=split_method,
            created_by=created_by_id
        )
        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)

        for participant in split_list:
            split_amount = (participant['split_amount'] / 100) * total_amount
            db.execute(
                user_expenses.insert().values(
                    user_id=participant["user_id"],
                    expense_id=new_expense.id,
                    split_amount=split_amount
                )
            )
            participants.append(ExpenseParticipant(user_id=participant["user_id"], split_amount=split_amount))  # Add participant details
        db.commit()

    else:
        raise HTTPException(status_code=400, detail="Invalid split method.")

    return ExpenseResponse(
        id=new_expense.id,
        description=new_expense.description,
        total_amount=new_expense.total_amount,
        split_method=new_expense.split_method,
        participants=participants
    )

# fetch particular expense details using the expense id and the id of user who created the expense 
def get_expense_by_id(user_id:int, expense_id: int, db: Session):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.created_by == user_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found for the given user.")

    # Retrieve participants and split amounts
    participants_data = db.execute(
        user_expenses.select().where(user_expenses.c.expense_id == expense_id)
    ).fetchall()

    # Transform the participants data into ExpenseParticipant objects
    participants = [
        ExpenseParticipant(user_id=participant.user_id, split_amount=participant.split_amount)
        for participant in participants_data
    ]

    return ExpenseResponse(
        id=expense.id,
        description=expense.description,
        total_amount=expense.total_amount,
        split_method=expense.split_method,
        participants=participants
    )

# Fetch all expense details of a particular user
def get_user_expenses(user_id: int, db: Session):
    user_expense = (
        db.query(user_expenses.c.expense_id, user_expenses.c.split_amount)
        .filter(user_expenses.c.user_id == user_id)
        .distinct()
        .all()
    )

    if not user_expense:
        raise HTTPException(status_code=404, detail="No expenses found for this user.")

    # Fetch expense details using the retrieved expense IDs
    expense_ids = [user_exp[0] for user_exp in user_expense]
    expenses = (
        db.query(Expense)
        .filter(Expense.id.in_(expense_ids))
        .all()
    )

    # Dictionary to map expense ID to its details
    expense_map = {expense.id: expense for expense in expenses}


    expense_list = [
        UserExpenseResponse(
            expense_id=expense_id,
            description=expense_map[expense_id].description,
            total_amount=expense_map[expense_id].total_amount,
            amount_owed=split_amount,
            created_at=expense_map[expense_id].created_at
        )
        for expense_id, split_amount in user_expense
    ]

    return expense_list


# Fetch expenses details of all the users in the system
def show_overall_expenses(db: Session):
    users = db.query(User).all()

    if not users:
        raise HTTPException(status_code=404, detail="No users found.")

    overall_expenses = []
    for user in users:
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        
        user_expense = (
            db.query(user_expenses.c.expense_id, user_expenses.c.split_amount)
            .filter(user_expenses.c.user_id == user.id)
            .distinct()
            .all()
        )

        expense_ids = [user_exp[0] for user_exp in user_expense]
        expenses = (
            db.query(Expense)
            .filter(Expense.id.in_(expense_ids))
            .all()
        )

        # Dictionary to map expense ID to its details
        expense_map = {expense.id: expense for expense in expenses}
        expense_list = [
            UserExpenseResponse(
                expense_id=expense_id,
                description=expense_map[expense_id].description,
                total_amount=expense_map[expense_id].total_amount,
                amount_owed=split_amount,
                created_at=expense_map[expense_id].created_at
            )
            for expense_id, split_amount in user_expense
        ]

        if not expense_list:
            expense_list = []

        # Append the user details and their expense list to the overall_expenses
        overall_expenses.append(UserExpenseListResponse(
            user_id=user.id,
            name=user.name,
            email=user.email,
            mobile=user.mobile,
            expense_list=expense_list
        ))

    return overall_expenses
