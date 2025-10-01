// frontend/src/components/canvas/PieChartCanvas.tsx
import React from 'react';
import { Pie } from 'react-chartjs-2';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
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
  const defaultColors = [
    '#4CAF50', // Green
    '#2196F3', // Blue
    '#FFC107', // Amber
    '#F44336', // Red
    '#9C27B0', // Purple
    '#FF9800', // Orange
    '#00BCD4', // Cyan
    '#E91E63', // Pink
    '#607D8B', // Blue Grey
    '#795548', // Brown
  ];
  const backgroundColors = data.map((item: any, index: number) => item.color || defaultColors[index % defaultColors.length]);

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
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: config?.show_legends ?? true,
        position: config?.legendPosition || 'top',
      },
      title: {
        display: false, // Title is handled by CardTitle
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
              label += new Intl.NumberFormat('fr-FR', { style: 'decimal' }).format(context.parsed);
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
    <Card className="w-full h-96">
      {title && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent className="h-[calc(100%-4rem)] p-4">
        <Pie data={chartData} options={chartOptions} />
      </CardContent>
    </Card>
  );
};

export default PieChartCanvas;