# My Bank Chatbot

This is a Flask-based banking chatbot web application with simple NLU (Natural Language Understanding) for intent classification. It allows users to log in, view their dashboard, interact with a banking assistant, and manage accounts and transactions.

## Features
- User authentication (login/signup/logout)
- SQLite database for users, accounts, and transactions
- Chatbot with intent classification using scikit-learn
- Entity extraction for amounts and names
- Responsive web UI with Bootstrap

## Getting Started
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the app:
   ```
   python app.py
   ```
3. Open your browser at `http://localhost:5000`

## Default Demo User
- Email: demo@bank.com
- Password: demo123

## Project Structure
- `app.py` - Main Flask app
- `nlu.py` - NLU logic (intent classification, entity extraction)
- `database.db` - SQLite database
- `dataset.csv` - Training data for NLU
- `models/` - Trained intent model
- `static/` - CSS/JS assets
- `templates/` - HTML templates

## License
MIT License

## 📂 Project Structure
bankbot/

│── app.py # Flask backend entry point

│── nlu.py # NLU model for intent & entity extraction

│── database.db # SQLite database

│── dataset.csv # Training dataset for intents

│── requirements.txt # Dependencies

│── static/ # Frontend assets

│ ├── css/styles.css
│ └── js/chat.js

yaml
Copy code

---

## 🛠️ Installation & Setup

1. **Clone / Extract the Project**
   ```bash
   git clone <repo_url>
   cd bankbot_project/bankbot
Create Virtual Environment (optional)

bash

(Copy code)

python -m venv venv

source venv/bin/activate        # On Linux/Mac

venv\Scripts\activate           # On Windows

Install Dependencies



(Copy code)

pip install -r requirements.txt


Run the Flask App

(Copy code)

python app.py

The server will start on http://127.0.0.1:5000/

🚀 Usage
Open the browser and go to http://127.0.0.1:5000/

Login using the demo credentials (or add new entries in database.db)

Use the chatbot to perform actions like:

“Check my balance”

“Transfer 200 to savings account”

“Show last transactions”




---

👉 This README is professional and ready to add to your project.  

Do you want me to also include **screenshots (outputs) in the README** (like chatbot UI, dashboard, NLU output) so that it looks like a demo-ready documentation? ​:contentReference[oaicite:0]{index=0}​






You said:
yes and give me the file to download and paste it


ChatGPT said:

Analyzed

python


(Copy code)

readme_content = """# BankBot – AI Chatbot for Banking FAQs


## 📌 Overview
BankBot is an AI-powered chatbot designed to handle common banking queries such as **checking account balance, transferring money, and retrieving transaction history**.  
This project was developed as part of **Infosys Springboard 6.0 Internship (Milestone 1)** and integrates:
- **NLU Engine** for intent classification & entity extraction
- **Flask Backend** for API services
- **SQLite Database** for customer data & transactions
- **Frontend (HTML/CSS/JS)** for a chatbot interface

---

## ⚙️ Features
- **Natural Language Understanding (NLU)**
  - Detects intents like `check_balance`, `transfer_money`, `account_info`
  - Extracts entities such as amount, account type, and account number

- **Backend (Flask API)**
  - Routes for query processing (`/predict`) and data retrieval
  - Connects chatbot frontend to NLU engine and database

- **Database (SQLite)**
  - Stores user details, balances, and transactions
  - Supports real-time queries

- **Frontend**
  - Login system with authentication
  - User dashboard showing balance, transactions, and cards
  - Interactive chatbot interface for queries

-------

## 📂 Project Structure

bankbot/

│── app.py # Flask backend entry point
│── nlu.py # NLU model for intent & entity extraction
│── database.db # SQLite database
│── dataset.csv # Training dataset for intents
│── requirements.txt # Dependencies
│── static/ # Frontend assets
│ ├── css/styles.css
│ └── js/chat.js

yaml


(Copy code)

--------

## 🛠️ Installation & Setup

1. **Clone / Extract the Project**
   ```bash
   git clone <repo_url>
   cd bankbot_project/bankbot

   
Create Virtual Environment (optional)

(Copy code)

python -m venv venv


source venv/bin/activate            # On Linux/Mac


venv\\Scripts\\activate             # On Windows


Install Dependencies


(Copy code)


pip install -r requirements.txt


Run the Flask App

(Copy code)


python app.py


The server will start on http://127.0.0.1:5000/


🚀 Usage


Open the browser and go to http://127.0.0.1:5000/

Login using the demo credentials  (or add new entries in database.db)


Use the chatbot to perform actions like:


“Check my balance”

“Transfer 200 to savings account”

“Show last transactions”


📸 Screenshots


1. NLU Training & Prediction
![alt text](<Screenshot 2025-08-31 190532.png>)

2. Flask Server Running
![alt text](<Screenshot 2025-08-31 190645.png>)

3. Login Page
![alt text](<Screenshot 2025-08-31 190732.png>)

4. Dashboard
![alt text](<Screenshot 2025-08-31 190802.png>)

5. Chatbot in Action
![alt text](<Screenshot 2025-08-31 190859.png>)


📦 Dependencies


Python 3.8+

Flask

scikit-learn

pandas

sqlite3

(See requirements.txt for full list)


📌 Future Enhancements


Voice-enabled chatbot

Multi-language support (English + regional)

Fraud detection alerts

Personalized financial recommendations


👨‍💻 Author
Marre Narendar Karthikeya

