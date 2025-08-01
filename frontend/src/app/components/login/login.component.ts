import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { CarouselModule } from 'primeng/carousel';
import { CheckboxModule } from 'primeng/checkbox';
import { DividerModule } from 'primeng/divider';
import { InputTextModule } from 'primeng/inputtext';
import { RippleModule } from 'primeng/ripple';
import { ToastModule } from 'primeng/toast';

import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';

import { AuthService } from '../../services/auth-service.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    HttpClientModule,
    InputTextModule,
    ButtonModule,
    CarouselModule,
    DividerModule,
    RippleModule,
    CheckboxModule,
    RouterModule,
    ReactiveFormsModule,
    ToastModule,
  ],
  providers: [MessageService, AuthService],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  formGroup: FormGroup;

  constructor(
    private authService: AuthService,
    private messageService: MessageService,
    private router: Router
  ) {
    this.formGroup = new FormGroup({
      username: new FormControl<string | null>(null),
      password: new FormControl<string | null>(null),
    });
  }

  login() {
    if (this.authService.isLocalStorageAvailable()) {
      this.authService.login(this.formGroup.value).subscribe({
        next: (response) => {
          this.messageService.add({
            severity: 'success',
            summary: 'Success',
            detail: response.message,
          });

          localStorage.setItem('token', response.token);
          localStorage.setItem('user', JSON.stringify(response.user));

          this.router.navigate(['/home']);
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
}
