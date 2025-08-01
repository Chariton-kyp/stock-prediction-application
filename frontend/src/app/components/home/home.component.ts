import { MessageService } from 'primeng/api';
import { AvatarModule } from 'primeng/avatar';
import { ButtonModule } from 'primeng/button';
import { InputSwitchModule } from 'primeng/inputswitch';
import { InputTextModule } from 'primeng/inputtext';
import { InputTextareaModule } from 'primeng/inputtextarea';
import { RippleModule } from 'primeng/ripple';
import { StyleClassModule } from 'primeng/styleclass';
import { ToastModule } from 'primeng/toast';

import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';

import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth-service.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    InputTextModule,
    InputTextareaModule,
    AvatarModule,
    InputSwitchModule,
    StyleClassModule,
    ButtonModule,
    RippleModule,
    RouterModule,
    HttpClientModule,
    RouterModule,
    ReactiveFormsModule,
    ToastModule,
  ],
  providers: [AuthService, ApiService, MessageService],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements OnInit {
  user: any;
  formGroup: FormGroup;

  constructor(
    private authService: AuthService,
    private apiService: ApiService,
    private messageService: MessageService,
    public router: Router
  ) {
    this.formGroup = new FormGroup({
      firstname: new FormControl<string | null>(null),
      lastname: new FormControl<string | null>(null),
      email: new FormControl<string | null>(null),
      message: new FormControl<string | null>(null),
    });
  }

  ngOnInit(): void {}

  isUserLoggedIn(): boolean {
    return this.authService.isLoggedIn();
  }

  logout(): void {
    this.authService.logout();
  }

  submitHelpdesk() {
    if (!this.formGroup.valid) {
      return;
    }

    if (this.isUserLoggedIn()) {
      this.formGroup.addControl(
        'user_id',
        new FormControl<string | null>(this.authService.getUser().id)
      );
    }

    this.apiService.helpdeskSubmit(this.formGroup.value).subscribe({
      next: (response) => {
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: response.message,
        });

        this.formGroup.reset();
      },
      error: (error) => {
        let errorMessage = 'An error occurred. Please try again.';
        if (error.error && error.error.message) {
          errorMessage = error.error.message;
        }
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: errorMessage,
        });
      },
    });
  }
}
