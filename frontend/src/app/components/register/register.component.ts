import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { CheckboxModule } from 'primeng/checkbox';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { StyleClassModule } from 'primeng/styleclass';
import { ToastModule } from 'primeng/toast';

import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';

import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    PasswordModule,
    InputTextModule,
    ButtonModule,
    CommonModule,
    RouterModule,
    CheckboxModule,
    CommonModule,
    StyleClassModule,
    ReactiveFormsModule,
    HttpClientModule,
    ToastModule,
  ],
  providers: [ApiService, MessageService],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss',
})
export class RegisterComponent {
  formGroup: FormGroup;

  constructor(
    private apiService: ApiService,
    private messageService: MessageService,
    public router: Router
  ) {
    this.formGroup = new FormGroup({
      username: new FormControl<string | null>(null),
      email: new FormControl<string | null>(null),
      password: new FormControl<string | null>(null),
      confirmPassword: new FormControl<string | null>(null),
      termsAccepted: new FormControl<boolean | null>(null),
    });
  }

  register() {
    if (!this.formGroup.valid) {
      return;
    }

    this.apiService.register(this.formGroup.value).subscribe({
      next: (response) => {
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: response.message,
        });
        this.router.navigate(['/login']);
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
