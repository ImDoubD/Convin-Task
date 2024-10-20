from fastapi import FastAPI
from controller import balance_sheet_controller, expense_controller, user_controller

app = FastAPI()

# Include routers
app.include_router(user_controller.router,prefix="/auth", tags=["Users"])
app.include_router(expense_controller.router,prefix="/operation", tags=["Expenses"])
app.include_router(balance_sheet_controller.router,prefix="/balance-sheet", tags=["Balance"])


@app.get("/")
def root():
    return {"message": "Welcome to the Daily Expenses Sharing Portal!"}