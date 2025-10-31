import { Component, Input, OnChanges, SimpleChanges, AfterViewInit, OnInit, OnDestroy } from '@angular/core';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-charts',
  templateUrl: './charts.component.html',
  styleUrls: ['./charts.component.css']
})
export class ChartsComponent implements OnChanges, OnInit, OnDestroy {
  @Input() data: any[] = [];
  @Input() type: 'line' | 'bar' | 'pie' | 'doughnut' = 'line';
  @Input() title: string = '';
  @Input() chartId: string = '';
  @Input() fuelChartData: any;
  @Input() productionChartData: any;

  chartInstance: any;

  ngOnInit(): void {
    setTimeout(() => {
      this.renderChart();
    }, 100);
  }

  ngOnChanges(changes: SimpleChanges): void {
    if ((changes['data'] || changes['type']) && this.data && this.data.length) {
      setTimeout(() => {
        this.renderChart();
      }, 100);
    }
  }

  ngOnDestroy(): void {
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }
  }

  renderChart() {
    const chartId = this.chartId || this.title;
    const canvas = document.getElementById(chartId + '_chart') as HTMLCanvasElement;

    if (!canvas) {
      console.warn('Canvas element not found for:', chartId);
      return;
    }

    // CRITICAL FIX: Destroy any existing chart on this canvas
    // Check both instance and Chart.js registry
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }

    // Get chart from Chart.js registry and destroy it
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
      existingChart.destroy();
    }

    // Enhanced data processing for different chart types
    let labels = [];
    let datasets = [];

    if (this.type === 'pie' || this.type === 'doughnut') {
      labels = this.data.map(d => d.status || d.type || d.name || d.label || 'Unknown');
      datasets = [{
        data: this.data.map(d => d.count || d.value || d.percentage || 0),
        backgroundColor: this.generateColors(labels.length, 0.7),
        borderColor: this.generateColors(labels.length, 1),
        borderWidth: 2
      }];
    } else {
      labels = Array.from(new Set(this.data.map(d => d.month || d.date || d.period || ''))).filter(Boolean);

      const numericFields = Object.keys(this.data[0] || {}).filter(k =>
        k !== 'month' && k !== 'date' && k !== 'period' && k !== 'label'
      );

      datasets = numericFields.map((key, idx) => ({
        label: this.formatLabel(key),
        data: this.data.map(d => d[key] || 0),
        borderColor: this.getColor(idx),
        backgroundColor: this.type === 'bar' ? this.getColor(idx, 0.7) : this.getColor(idx, 0.1),
        fill: this.type === 'line',
        tension: 0.3,
        borderWidth: 2
      }));
    }

    this.chartInstance = new Chart(canvas, {
      type: this.type,
      data: { labels, datasets },
      options: this.getChartOptions()
    });
  }

  private getChartOptions(): any {
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: true,
          position: 'top' as const
        },
        title: {
          display: !!this.title,
          text: this.title,
          font: { size: 14 }
        } 
      }
    };

    if (this.type === 'line' || this.type === 'bar') {
      return {
        ...baseOptions,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      };
    }

    return baseOptions;
  }

  private generateColors(count: number, alpha: number = 1): string[] {
    const colors = [
      `rgba(76, 175, 80, ${alpha})`,
      `rgba(33, 150, 243, ${alpha})`,
      `rgba(255, 193, 7, ${alpha})`,
      `rgba(244, 67, 54, ${alpha})`,
      `rgba(156, 39, 176, ${alpha})`,
      `rgba(0, 188, 212, ${alpha})`,
      `rgba(255, 152, 0, ${alpha})`,
      `rgba(121, 85, 72, ${alpha})`
    ];

    if (count > colors.length) {
      const additionalColors = [];
      for (let i = colors.length; i < count; i++) {
        const hue = (i * 137.508) % 360;
        additionalColors.push(`hsla(${hue}, 70%, 65%, ${alpha})`);
      }
      return [...colors, ...additionalColors].slice(0, count);
    }

    return colors.slice(0, count);
  }

  private formatLabel(key: string): string {
    return key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
  }

  getColor(index: number, alpha = 1) {
    const colors = [
      `rgba(76, 175, 80, ${alpha})`,
      `rgba(33, 150, 243, ${alpha})`,
      `rgba(255, 193, 7, ${alpha})`,
      `rgba(244, 67, 54, ${alpha})`,
      `rgba(156, 39, 176, ${alpha})`,
      `rgba(0, 188, 212, ${alpha})`
    ];
    return colors[index % colors.length];
  }
}