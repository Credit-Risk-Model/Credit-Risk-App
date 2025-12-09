
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Api } from '../../services/api';
import { Loan } from '../../interface/loan';
import { HomeOwnership, LoanIntent, LoanGrade } from '../../models/enums';
import { CommonModule } from '@angular/common';
import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';
import { CardFooter } from "../card-footer/card-footer";
declare var bootstrap: any;

@Component({
  selector: 'app-form',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule, CardFooter],
  templateUrl: './form.html',
  styleUrl: './form.css'
})
export class Form implements OnInit {

  loanForm!: FormGroup;

  // Enum options for dropdowns
  homeOwnershipOptions = Object.values(HomeOwnership);
  loanIntentOptions = Object.values(LoanIntent);
  loanGradeOptions = Object.values(LoanGrade);

  inputGroups: any[] = []; 
  
  model1Result: any = null;
  model2Result: any = null;
  modelResults: any[] = [];
  hideResults: boolean = true;
  
  constructor(private fb: FormBuilder, private api: Api) {}

  ngAfterViewInit() {
    const tooltipTriggerList = [].slice.call(
      document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl));
  }

  ngOnInit() {  
    this.inputGroups = [
      {
        name: 'Personal Info',
        inputs: [
          { name: 'person_age',
            type: 'number', 
            label: 'Age', 
            step: 1, 
            min: 0,
            unit: "yrs" 
          },
          { name: 'person_income', type: 'number', label: 'Annual Income', step: 1, min: 0, unit: '$'},
          { 
            name: 'person_homeownership', 
            type: 'enum', 
            label: 'Home Ownership', 
            options: this.homeOwnershipOptions 
          },
          { 
            name: 'person_emplength', 
            type: 'number', 
            label: 'Employment Length', 
            step: 1, 
            min: 0,
            unit: "yrs",
            tooltip: 'Total number of years applicant has been employed.'
          }
        ]
      },
      {
        name: 'Loan Info',
        inputs: [
          { name: 'loan_intent', type: 'enum', label: 'Loan Intent', options: this.loanIntentOptions },
          { 
            name: 'loan_grade', 
            type: 'enum', 
            label: 'Loan Grade', 
            options: this.loanGradeOptions,
            tooltip: "The credit quality category assigned to applicant's loan, based on risk and creditworthiness. Higher grades indicate lower risk."
          },
          { name: 'loan_amnt', type: 'number', label: 'Loan Amount', step: 1, min: 1 },
          { name: 'loan_intrate', type: 'number', label: 'Interest Rate', step: 0.01, min: 0, unit: '%' },
          { 
            name: 'loan_percentincome', 
            type: 'number', 
            label: 'Percent of Income', 
            step: 1, 
            min: 0, 
            unit: '%',
            tooltip: 'Automatically calculated as (Loan Amount ÷ Annual Income) × 100.',
          }
        ]
      },
      {
        name: 'Credit Info',
        inputs: [
          { name: 'defaultonfile', type: 'binary', label: 'Historical Default', tooltip: 'Has applicant ever defaulted on a loan before?' },
          { 
            name: 'credhistlength', 
            type: 'number', 
            label: 'Credit History Length', 
            step: 1, 
            min: 0, 
            unit: 'yrs',
            tooltip: 'The number of years the applicant has maintained an active credit history. Longer histories typically indicate more reliable borrowers.'
          }
        ]
      }
    ];
    
    this.loanForm = this.fb.group({
      person_age: [null, [Validators.required, Validators.min(0), Validators.pattern(/^\d+$/)]],
      person_income: [null, [Validators.required, Validators.min(0), Validators.pattern(/^\d+$/)]],
      person_homeownership: [null, Validators.required],
      person_emplength: [
        null,
        [
          Validators.required,
          Validators.min(0),
          Validators.pattern(/^\d+$/),
          this.lengthValidator('person_age') 
        ]
      ],
      loan_intent: [null, Validators.required],
      loan_grade: [null, Validators.required],
      loan_amnt: [null, [Validators.required, Validators.min(0), Validators.pattern(/^\d+$/)]],
      loan_intrate: [null, [Validators.required, Validators.min(0)]],
      loan_percentincome: [null, [Validators.required, Validators.min(0)]],
      defaultonfile: [false, Validators.required],
      credhistlength: [
        null, 
        [
          Validators.required, 
          Validators.min(0),
          Validators.pattern(/^\d+$/),
          this.lengthValidator('person_age') 
        ]
      ]
    });

    this.loanForm.get('loan_percentincome')?.disable();

    this.loanForm.get('loan_amnt')?.valueChanges.subscribe(() => this.updateLoanPercentIncome());
    this.loanForm.get('person_income')?.valueChanges.subscribe(() => this.updateLoanPercentIncome());
  }
  updateLoanPercentIncome() {
    const loanAmount = this.loanForm.get('loan_amnt')?.value;
    const income = this.loanForm.get('person_income')?.value;
  
    if (loanAmount != null && income > 0) {
      const percent = (loanAmount / income) * 100;
      this.loanForm.get('loan_percentincome')?.setValue(Number(percent.toFixed(0)), { emitEvent: false });
    } else {
      this.loanForm.get('loan_percentincome')?.setValue(null, { emitEvent: false });
    }
  } 

  formatEnum(value: string): string {
    return value
      .toLowerCase()
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  lengthValidator(ageControlName: string): ValidatorFn {
    let subscribed = false;

    return (control: AbstractControl): ValidationErrors | null => {
      if (!control.parent) return null;

      const ageControl = control.parent.get(ageControlName);
      if (!ageControl) return null;

      const age = ageControl.value;
      const emplength = control.value;

      if (!subscribed) {
        subscribed = true;
        ageControl.valueChanges.subscribe(() => {
          control.updateValueAndValidity({ onlySelf: true });
        });
      }

      if (emplength != null && age != null && emplength > age) {
        return { greaterThanAge: true };
      }
      return null;
    };
  }

  submitLoan() {
    this.modelResults = [];
    this.hideResults = false;
    if (this.loanForm.valid) {
      console.log(this.loanForm.value);
    
      const loan: Loan = this.loanForm.getRawValue();
      this.api.getModelPredictions(loan).subscribe({
        next: res => this.modelResults=res,
        error: err => console.error(err)
      });
    } else {
      console.warn('Form is invalid');
      this.loanForm.markAllAsTouched();
    }
  }
}
