import { Observable } from 'rxjs';

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) {}

  register(user: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/register`, user);
  }

  getStockPrediction(stock: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/predict?stock=${stock}`);
  }

  helpdeskSubmit(ticket: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/helpdesk`, ticket);
  }
}
