import { HomeOwnership, LoanGrade, LoanIntent } from "../models/enums";

export interface Loan {
    person_age: number;                     // Age
    person_income: number;                  // Annual Income
    person_homeownership: HomeOwnership;    // Home ownership
    person_emplength: number;               // Employment length in years
    loan_intent: LoanIntent;                // Loan intent
    loan_grade: LoanGrade;                  // Loan grade
    loan_amnt: number;                      // Loan amount
    loan_intrate: number;                   // Interest rate
    loan_percentincome: number;             // Percent of income
    defaultonfile: boolean;                 // Historical default (Yes/No)
    credhistlength: number;                 // Credit history length
}
