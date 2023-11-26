import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { RippleModule } from 'primeng/ripple';

@Component({
  selector: 'app-stock-form',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    InputTextModule,
    ButtonModule,
    RippleModule,
  ],
  templateUrl: './stock-form.component.html',
  styleUrl: './stock-form.component.css',
})
export class StockFormComponent {
  stockName: string = '';

  onSubmit() {
    console.log(this.stockName);
  }
}
