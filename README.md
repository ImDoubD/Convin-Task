# Convin-Backend-Task
 To create a Daily Expenses Sharing Application. This application can register, authorize a user, add personalized expenses with user tagging, fetch individual user expense data, overall user expense data, generate balance sheet csv for individual user data, overall users in the system.

## Installation
This package uses Python 3.12.
```bash
python -m venv env
.\env\Scripts\Activate
pip install -r requirements.txt
```

## Code Structure
- The code structure being followed is the Model-Service-Controller architecture. Model comprises of the collection structure, Service comprises of the methods with business logic and validations, Controller comprises with methods with API endpoints.
- Error and input validations are done mostly in the Service layer methods.
- Proper comments are provided to specify responsiblity of various methods/APIs.
- Further config.py consists of connection and authorization secrets and security.py consists of methods for proper authorization through bearer JWT token generation and decoding those JWT tokens when endpoints are being hit to get access to user and expense details. These tokens are generated when login takes place after successful registration and time limit is of 120 minutes as of now.
- Database used is PostgreSQL which is deployed on Render.
- Certain unit tests are also written using pytest and httpx for the controller APIs and service methods.

## Run and Test the application
- Clone the github repository
- Pip install all the given requirements in virtual environment as provided in the installation part.
- The database is deployed so these APIs can be hit without any problem.
- To start the server, use command: `uvicorn main:app --reload`
  Hit the API's (in Postman or Thunderclient) in this order: 
- Post `http://127.0.0.1:8000/auth/register` \
  Sample input:
  ```bash
  {
    "name": "deepan",
    "email": "deepan@example.com",
    "password": "password123", 
    "mobile": "+12345678999"
  }
  ```
  This above API is for registration of users, where the user's details are inserted in the database.
- Post `http://127.0.0.1:8000/auth/login` \
  Sample input:
  ```bash
  {
    "email": "johndoe@example.com",
    "password": "password123"
  }
  ```
  This above API log in the user and generate the bearer JWT token for authorization. This token will be stored in the database, which will remain active for 120 minutes. 
- Get `http://127.0.0.1:8000/auth/user/details` \
  Sample input:
  ```bash
  <Bearer> : Token [Authorization]
  ```
  This above API will fetch authorized user personal details.
- Post `http://127.0.0.1:8000/operation/expense/add` \
  Sample input:
  Sample input:
  ```bash
  <Bearer> : Token [Authorization]
  {
    "description": "Dinner at Restaurant",
    "total_amount": 1499.00,
    "split_method": "percentage",  [# can be 'exact', 'equal', 'percentage']
    "split_list": [
      {"user_id": 2, "split_amount": 25.00},
      {"user_id": 3, "split_amount": 48.00},
      {"user_id": 4, "split_amount": 27.00}
    ]
  }
  ```
  This above API will let the authorized user to create expense, by tagging other users in it. 
- Get `http://127.0.0.1:8000/operation/expense/{expense_id}` \
  Sample input:
  Sample input:
  ```bash
  expense_id = 1
  url = http://127.0.0.1:8000/operation/expense/1
  <Bearer> : Token [Authorization]
  ```
  This above API will let the authorized user fetch a particular expense details created by him/her, validating the expense using provided expense_id.
- Get `http://127.0.0.1:8000/operation/expenses/user` \
  Sample input:
  ```bash
  <Bearer> : Token [Authorization]
  ```
  This above API fetches all the details including the expense data of the authorized user in which he/she is tagged, along with the amount owed.
- Get `http://127.0.0.1:8000/operation/expenses/overall` \
  Sample input:
  ```bash
  <Bearer> : Token [Authorization]
  ```
  This above API fetches all the details along with the expense data of all the users currently in the system. This API can be only hit by an authorized user.
- Get `http://127.0.0.1:8000/balance-sheet/user/{user_id}` \
  Sample input:
  ```bash
  user_id = 1
  url = http://127.0.0.1:8000/balance-sheet/user/1
  <Bearer> : Token [Authorization]
  ```
  This above API generates balance sheet csv of the authorized user details along with all the expenses' details in which he/she is tagged and amount owed. This API validates whether the user_id provided is same as the user_id of the authorized user from the JWT token, then provides the access accordingly.
- Get `http://127.0.0.1:8000/balance-sheet/overall` \
  Sample input:
  ```bash
  <Bearer> : Token [Authorization]
  ```
  This above API generates balance sheet csv with all the details along with the expense data of all the users currently in the system. This API can be only hit by an authorized user.
- In terminal, type `pytest` which in return will start the unit tests for the controller and service methods.
