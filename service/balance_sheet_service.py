from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import User
from io import StringIO
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from service.expense_service import get_user_expenses, show_overall_expenses
import csv
import os


def save_csv_file(csv_buffer: StringIO, filename: str):
    """
    Save the CSV data from the buffer to a file in the project directory.
    """
    save_directory = os.path.join(os.getcwd(), "balance-sheets")  
    os.makedirs(save_directory, exist_ok=True)

    file_path = os.path.join(save_directory, filename)
    
    # Write the CSV data to the file
    with open(file_path, 'w', newline='') as csv_file:
        csv_file.write(csv_buffer.getvalue())

    return file_path


# overall balance sheet
def download_overall_balance_sheet(db: Session):
    # Use the existing service function to get overall expense data
    overall_expenses = show_overall_expenses(db)

    if not overall_expenses:
        raise HTTPException(status_code=404, detail="No expenses found.")

    # Create a CSV string buffer
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)

    # Write CSV header
    writer.writerow(["user_id", "name", "email", "mobile", "expense_ids", "descriptions", "total_amounts", "amount_owed", "created_at"])

    # Iterate through the overall expenses and write rows to the CSV
    for user_data in overall_expenses:

        user_id = user_data.user_id
        name = user_data.name
        email = user_data.email
        phone = user_data.mobile
        
        expense_ids = []
        descriptions = []
        total_amounts = []
        amount_owed = []
        created_ats = []

        # Collect all expense data for the user, convert to string for CSV
        for expense in user_data.expense_list:
            expense_ids.append(str(expense.expense_id))  
            descriptions.append(expense.description)
            total_amounts.append(str(expense.total_amount))
            amount_owed.append(str(expense.amount_owed))
            created_ats.append(expense.created_at.isoformat()) 

        # Join each list with newline characters for the CSV, with multiple details separated by new line
        writer.writerow([
            user_id,
            name,
            email,
            phone,
            "\n".join(expense_ids),        
            "\n".join(descriptions),       
            "\n".join(total_amounts),   
            "\n".join(amount_owed),      
            "\n".join(created_ats) 
        ])

    # Reset buffer to the beginning
    csv_buffer.seek(0)

    # Save the CSV to a file
    filename = "overall_balance_sheet.csv"
    save_csv_file(csv_buffer, filename)

    response = StreamingResponse(csv_buffer, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=overall_balance_sheet.csv"
    return response


# individual balance sheet 
def download_individual_balance_sheet(user_id: int, db: Session):
    # Query to get user details
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Use the existing service function to get individual expense data
    expense_list = get_user_expenses(user_id, db)

    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)

    writer.writerow(["user_id", "name", "email", "mobile", "expense_ids", "descriptions", "total_amounts", "amount_owed", "created_at"])

    expense_ids = []
    descriptions = []
    total_amounts = []
    amount_owed = []
    created_ats = []

    # Collect all expense data for the user, convert to string for CSV
    for expense in expense_list:
        expense_ids.append(str(expense.expense_id))  
        descriptions.append(expense.description)  
        total_amounts.append(str(expense.total_amount)) 
        amount_owed.append(str(expense.amount_owed)) 
        created_ats.append(expense.created_at.isoformat())

    # Join each list with newline characters for the CSV, multiple details separated by new line
    writer.writerow([
        user.id,
        user.name,
        user.email,
        user.mobile,
        "\n".join(expense_ids), 
        "\n".join(descriptions), 
        "\n".join(total_amounts), 
        "\n".join(amount_owed), 
        "\n".join(created_ats) 
    ])

    csv_buffer.seek(0)

    filename = f"{user.name}_balance_sheet.csv"
    save_csv_file(csv_buffer, filename)

    response = StreamingResponse(csv_buffer, media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=balance_sheet_user_{user.id}.csv"
    return response

