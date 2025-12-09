import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Loan } from '../interface/loan';

@Injectable({
  providedIn: 'root'
})
export class Api {

  private baseUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getModelPredictions(loan: Loan): Observable<any> {
    return this.http.post(`${this.baseUrl}/predict/models`, loan);
  }

}
