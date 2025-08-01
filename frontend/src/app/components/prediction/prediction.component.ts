import { ButtonModule } from 'primeng/button';
import { ChartModule } from 'primeng/chart';
import { DropdownModule } from 'primeng/dropdown';
import { TableModule } from 'primeng/table';

import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-prediction',
  templateUrl: './prediction.component.html',
  styleUrls: ['./prediction.component.scss'],
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
})
export class PredictionComponent implements OnInit {
  stocks: any[] = [];
  selectedStock: string = '';
  historicalData: any;
  predictionData: any;
  chartData: any;
  chartOptions: any;
  predictionChart: any;
  predictionOptions: any;
  private baseUrl = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchAvailableStocks();
  }

  fetchAvailableStocks(): void {
    this.http.get<any[]>(`${this.baseUrl}/stocks`).subscribe(
      (stocks) => {
        this.stocks = stocks.map((stock) => ({
          name: stock.name,
          code: stock.code,
        }));
      },
      (error) => console.error('Error fetching available stocks:', error)
    );
  }

  onStockSelected(): void {
    this.http
      .get<any>(`${this.baseUrl}/stocks/${this.selectedStock}`)
      .subscribe(
        (data) => {
          this.updateChart(data);
        },
        (error) => console.error('Error fetching stock data:', error)
      );
  }

  updateChart(stockData: any): void {
    this.chartData = {
      labels: stockData.labels,
      datasets: [
        {
          label: `${this.selectedStock} - Historical Prices`,
          data: stockData.prices,
          borderColor: 'blue',
          fill: false,
        },
      ],
    };

    this.chartOptions = {
      responsive: true,
    };
  }

  predictPrice(): void {
    this.http
      .get<any>(`${this.baseUrl}/stocks/${this.selectedStock}/predict`)
      .subscribe(
        (response) => {
          this.updatePredictionChart(
            response.historical_prices,
            response.historical_dates, // Make sure this data is available
            response.predicted_prices
          );
          this.predictionData = response.predicted_prices.map(
            (price: number, index: number) => ({
              date: new Date(new Date().setDate(new Date().getDate() + index))
                .toISOString()
                .split('T')[0],
              price,
            })
          );
        },
        (error) => console.error('Error predicting prices:', error)
      );
  }

  updatePredictionChart(
    historicalPrices: number[],
    historicalDates: string[], // Include dates in the historical data
    predictedPrices: number[]
  ): void {
    // Continue the dates for predictions
    const lastHistoricalDate = new Date(
      historicalDates[historicalDates.length - 1]
    );
    const predictedDates = predictedPrices.map((_, index) => {
      const date = new Date(lastHistoricalDate);
      date.setDate(date.getDate() + index + 1); // starts the day after the last historical date
      return date.toISOString().split('T')[0];
    });

    const allDates = [...historicalDates, ...predictedDates];
    // Include the last historical price as the start of the predicted prices
    const connectedPredictedPrices = [
      historicalPrices[historicalPrices.length - 1],
      ...predictedPrices,
    ];
    const allPrices = [
      ...historicalPrices,
      ...connectedPredictedPrices.slice(1),
    ]; // slice to avoid duplicating the connecting point

    this.predictionChart = {
      labels: allDates,
      datasets: [
        {
          label: `${this.selectedStock} - Historical Prices`,
          data: historicalPrices,
          borderColor: 'blue',
          fill: false,
          lineTension: 0,
        },
        {
          label: `${this.selectedStock} - Predicted Prices`,
          data: [
            ...Array(historicalPrices.length).fill(null), // Fill with null up to the last historical point
            ...connectedPredictedPrices,
          ],
          borderColor: 'red',
          fill: false,
          lineTension: 0,
        },
      ],
    };

    this.predictionOptions = {
      responsive: true,
      tooltips: {
        mode: 'index',
        intersect: false,
      },
      hover: {
        mode: 'nearest',
        intersect: true,
      },
      scales: {
        xAxes: [
          {
            type: 'time',
            time: {
              unit: 'day',
              tooltipFormat: 'YYYY-MM-DD',
              displayFormats: {
                day: 'YYYY-MM-DD',
              },
            },
            display: true,
            scaleLabel: {
              display: true,
              labelString: 'Date',
            },
          },
        ],
        yAxes: [
          {
            display: true,
            scaleLabel: {
              display: true,
              labelString: 'Price',
            },
          },
        ],
      },
    };
  }
}
