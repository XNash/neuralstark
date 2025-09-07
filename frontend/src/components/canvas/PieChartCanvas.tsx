// frontend/src/components/canvas/PieChartCanvas.tsx
import React from 'react';
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
);

interface PieChartCanvasProps {
  canvasData: any; // This will be the 'canvas' object from the backend response
}

const PieChartCanvas: React.FC<PieChartCanvasProps> = ({ canvasData }) => {
  const { title, data, config } = canvasData;

  // --- Data Transformation for Chart.js ---
  const chartLabels = data.map((item: any) => item.label);
  const chartValues = data.map((item: any) => item.value);
  const backgroundColors = data.map((item: any) => item.color || `#${Math.floor(Math.random()*16777215).toString(16)}`); // Use color from data or random

  const chartData = {
    labels: chartLabels,
    datasets: [
      {
        label: title || 'Valeur',
        data: chartValues,
        backgroundColor: backgroundColors,
        borderColor: backgroundColors.map((color: string) => color.replace('0.6', '1')),
        borderWidth: 1,
      },
    ],
  };

  // --- Chart.js Options Configuration ---
  const chartOptions = {
    responsive: config?.responsive ?? true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: config?.show_legends ?? true,
        position: 'top' as const,
      },
      title: {
        display: true,
        text: title,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            let label = context.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed !== null) {
              label += new Intl.NumberFormat('en-US', { style: 'decimal' }).format(context.parsed);
              if (config?.show_percentages) {
                const total = context.dataset.data.reduce((sum: number, val: number) => sum + val, 0);
                const percentage = (context.parsed / total * 100).toFixed(2) + '%';
                label += ` (${percentage})`;
              }
            }
            return label;
          }
        }
      }
    },
    // For donut chart, set cutout percentage
    cutout: config?.donut ? (config?.inner_radius * 100 || 50) : 0,
  };

  return (
    <div style={{ width: config?.width || '100%', height: config?.height || '400px' }}>
      <Pie data={chartData} options={chartOptions} />
    </div>
  );
};

export default PieChartCanvas;