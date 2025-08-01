import { Observable } from 'rxjs';

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private baseUrl = 'http://127.0.0.1:5000'; // Replace with your backend URL

  constructor(private http: HttpClient) {}

  login(credentials: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/login`, credentials);
  }

  logout(): void {
    if (this.isLocalStorageAvailable()) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }

  isLoggedIn(): boolean {
    if (this.isLocalStorageAvailable()) {
      return !!localStorage.getItem('token');
    }
    return false;
  }

  getToken(): string | null {
    if (this.isLocalStorageAvailable()) {
      return localStorage.getItem('token');
    }
    return null;
  }

  getUser(): any {
    if (this.isLocalStorageAvailable()) {
      const user = localStorage.getItem('user');
      return user ? JSON.parse(user) : null;
    }
    return null;
  }

  isLocalStorageAvailable(): boolean {
    return typeof localStorage !== 'undefined';
  }
}
