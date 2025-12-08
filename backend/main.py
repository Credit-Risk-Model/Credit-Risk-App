from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FastAPI backend is running"}

class Loan(BaseModel):
    person_age: int
    person_income: float
    person_homeownership: str
    person_emplength: int
    loan_intent: str
    loan_grade: str
    loan_amnt: float
    loan_intrate: float
    loan_percentincome: float
    defaultonfile: bool
    credhistlength: int

def covertFormData(loan: Loan, columns, type):
    person_age = loan.person_age
    person_income = loan.person_income
    person_emp_length = loan.person_emplength
    loan_amnt = loan.loan_amnt
    loan_int_rate = loan.loan_intrate
    loan_percent_income = loan.loan_percentincome/100
    cb_person_cred_hist_length = loan.credhistlength

    person_home_ownership_MORTGAGE = 0
    person_home_ownership_OTHER = 0
    person_home_ownership_OWN = 0
    person_home_ownership_RENT = 0
    if loan.person_homeownership == 'RENT':
        person_home_ownership_RENT = 1
    elif loan.person_homeownership == 'OWN':
        person_home_ownership_OWN = 1
    elif loan.person_homeownership == 'MORTGAGE':
        person_home_ownership_MORTGAGE = 1
    elif loan.person_homeownership == 'OTHER':
        person_home_ownership_OTHER = 1

    loan_intent_DEBTCONSOLIDATION = 0
    loan_intent_EDUCATION = 0
    loan_intent_HOMEIMPROVEMENT = 0
    loan_intent_MEDICAL = 0
    loan_intent_PERSONAL = 0
    loan_intent_VENTURE = 0
    if loan.loan_intent == 'DEBT_CONSOLIDATION':
        loan_intent_DEBTCONSOLIDATION = 1
    elif loan.loan_intent == 'EDUCATION':
        loan_intent_EDUCATION = 1
    elif loan.loan_intent == 'HOME_IMPROVEMENT':
        loan_intent_HOMEIMPROVEMENT = 1
    elif loan.loan_intent == 'MEDICAL':
        loan_intent_MEDICAL = 1
    elif loan.loan_intent == 'PERSONAL':
        loan_intent_PERSONAL = 1
    elif loan.loan_intent == 'VENTURE':
        loan_intent_VENTURE = 1

    loan_grade_A = 0
    loan_grade_B = 0
    loan_grade_C = 0
    loan_grade_D = 0
    loan_grade_E = 0
    loan_grade_F = 0
    loan_grade_G = 0
    if loan.loan_grade == 'A':
        loan_grade_A = 1
    elif loan.loan_grade == 'B':
        loan_grade_B = 1
    elif loan.loan_grade == 'C':
        loan_grade_C = 1
    elif loan.loan_grade == 'D':
        loan_grade_D = 1
    elif loan.loan_grade == 'E':
        loan_grade_E = 1
    elif loan.loan_grade == 'F':
        loan_grade_F = 1
    elif loan.loan_grade == 'G':
        loan_grade_G = 1

    cb_person_default_on_file_N = 0
    cb_person_default_on_file_Y = 0
    if loan.defaultonfile:
        cb_person_default_on_file_Y = 1
    else:
        cb_person_default_on_file_N = 1

    if type == "forest":
        loan_grade = (loan_grade_A * 6 +
                            loan_grade_B * 5 +
                            loan_grade_C * 4 +
                            loan_grade_D * 3 +
                            loan_grade_E * 2 +
                            loan_grade_F * 1 +
                            loan_grade_G * 0)
        return pd.DataFrame([[
        person_age,
        person_income,
        person_emp_length,
        loan_amnt,
        loan_int_rate,
        loan_percent_income,
        cb_person_cred_hist_length,
        person_home_ownership_MORTGAGE,
        person_home_ownership_OTHER,
        person_home_ownership_OWN,
        person_home_ownership_RENT,
        loan_intent_DEBTCONSOLIDATION,
        loan_intent_EDUCATION,
        loan_intent_HOMEIMPROVEMENT,
        loan_intent_MEDICAL,
        loan_intent_PERSONAL,
        loan_intent_VENTURE,
        loan_grade,
        cb_person_default_on_file_N
    ]], columns=columns)

    else:
        return pd.DataFrame([[
            person_age,
            person_income,
            person_emp_length,
            loan_amnt,
            loan_int_rate,
            loan_percent_income,
            cb_person_cred_hist_length,
            person_home_ownership_MORTGAGE,
            person_home_ownership_OTHER,
            person_home_ownership_OWN,
            person_home_ownership_RENT,
            loan_intent_DEBTCONSOLIDATION,
            loan_intent_EDUCATION,
            loan_intent_HOMEIMPROVEMENT,
            loan_intent_MEDICAL,
            loan_intent_PERSONAL,
            loan_intent_VENTURE,
            loan_grade_A,
            loan_grade_B,
            loan_grade_C,
            loan_grade_D,
            loan_grade_E,
            loan_grade_F,
            loan_grade_G,
            cb_person_default_on_file_N,
            cb_person_default_on_file_Y
        ]], columns=columns)


# Global variables for models and scaler
linear_model = None
forest_model = None
scaler = None

def train_linear_model():
    df = pd.read_csv('CreditDataCleanOHEVer.csv')
    df.columns = df.columns.str.strip()

    X = df.drop('loan_status', axis=1)
    y = df['loan_status']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Train logistic regression model
    linear_model = LogisticRegression(solver="saga", max_iter=2000)
    linear_model.fit(X_train, y_train)

    # Predict
    y_pred = linear_model.predict(X_test)

    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)

    return linear_model, scaler, X.columns, accuracy

# Train model at startup
linear_model, scaler, linear_columns, linear_accuracy = train_linear_model()

def train_forest_model():
    crdata = pd.read_csv('CreditDataCleanOHEVer.csv')
    crdata.columns = crdata.columns.str.strip()

    crdata['loan_grade'] = (crdata['loan_grade_A'] * 6 +
                            crdata['loan_grade_B'] * 5 +
                            crdata['loan_grade_C'] * 4 +
                            crdata['loan_grade_D'] * 3 +
                            crdata['loan_grade_E'] * 2 +
                            crdata['loan_grade_F'] * 1 +
                            crdata['loan_grade_G'] * 0)
    crdata = crdata.drop(['loan_grade_A',
                      'loan_grade_B',
                      'loan_grade_C',
                      'loan_grade_D',
                      'loan_grade_E',
                      'loan_grade_F',
                      'loan_grade_G',], axis=1)
    crdata = crdata.drop('cb_person_default_on_file_Y', axis=1)
    
    Xb = crdata.drop('loan_status', axis=1)

    yb = crdata['loan_status']

    Xb_train, Xb_test, yb_train, yb_test = train_test_split(
        Xb,
        yb,
        test_size=0.2,
        random_state=42)

    forest_model = RandomForestClassifier(random_state=42)
    forest_model.fit(Xb_train, yb_train)

    yb_pred = forest_model.predict(Xb_test)
    baccuracy = accuracy_score(yb_test, yb_pred)
    print(f"Accuracy: {baccuracy}")

    return forest_model, Xb.columns, baccuracy

# Train model at startup
forest_model, forest_columns, forest_accuracy = train_forest_model()

def predict_linear_model(loan: Loan):
    global linear_model, scaler, linear_columns, linear_accuracy

    # If model/scaler not loaded for some reason, train again
    if linear_model is None or scaler is None or linear_columns is None:
        linear_model, scaler, linear_columns, linear_accuracy = train_linear_model()

    # Accuracy
    accuracy = linear_accuracy
    # Name of Model
    name = "Logistic Regression"
    
    example = covertFormData(loan,linear_columns,"linear")

    # Scale the form data
    example_scaled = scaler.transform(example)

    # Predict
    predicted_status = linear_model.predict(example_scaled)[0]

    return {
        "name": name,
        "result": "Approve" if int(predicted_status) == 0 else "Rejected",
        "accuracy": float(accuracy) * 100
        }

def predict_forest_model(loan: Loan):
    global forest_model, scaler, forest_columns, forest_accuracy

    # If model/scaler not loaded for some reason, train again
    if forest_model is None or forest_columns is None:
        forest_model, forest_columns, forest_accuracy = train_forest_model()

    # Accuracy
    accuracy = forest_accuracy
    # Name of Model
    name = "Random Forest"
    
    example = covertFormData(loan,forest_columns,"forest")

    # Predict
    predicted_status = forest_model.predict(example)[0]

    return {
        "name": name,
        "result": "Approve" if int(predicted_status) == 0 else "Rejected",
        "accuracy": float(accuracy) * 100
        }

@app.post("/predict/models")
def predict_models(loan: Loan):
    linear=predict_linear_model(loan)
    forest=predict_forest_model(loan)
    return [linear,forest]
