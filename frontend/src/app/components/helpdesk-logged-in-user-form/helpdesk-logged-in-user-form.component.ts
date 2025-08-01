import { ButtonModule } from 'primeng/button';
import { ChartModule } from 'primeng/chart';
import { DropdownModule } from 'primeng/dropdown';
import { TableModule } from 'primeng/table';

import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth-service.service';

@Component({
  selector: 'helpdesk-logged-in-user-form',
  templateUrl: './helpdesk-logged-in-user-form.component.html',
  styleUrls: ['./helpdesk-logged-in-user-form.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    ButtonModule,
    DropdownModule,
    ChartModule,
    TableModule,
  ],
  providers: [AuthService, ApiService],
})
export class HelpdeskLoggedInUserFormComponent implements OnInit {
  helpdeskData: any;
  private baseUrl = 'http://127.0.0.1:5000';
  user: any;

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.user = this.authService.getUser();
    this.fetchHelpdeskIssues();
  }

  fetchHelpdeskIssues(): void {
    const user_email = this.user?.email;

    this.http.get<any[]>(`${this.baseUrl}/helpdesk/${user_email}`).subscribe(
      (helpdeskData) => {
        this.helpdeskData = helpdeskData;
      },
      (error) => console.error('Error fetching helpdesk issues:', error)
    );
  }
}
