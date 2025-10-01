// frontend/src/components/canvas/ComboChartCanvas.tsx
import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface ComboChartCanvasProps {
  canvasData: any; // This will be the 'canvas' object from the backend response
}

const ComboChartCanvas: React.FC<ComboChartCanvasProps> = ({ canvasData }) => {
  const { title, series, options, axes } = canvasData; // Destructure 'title', 'series' and 'axes'

  // Extract labels from the first series (assuming all series share the same labels)
  const chartLabels = series[0]?.data.map((item: any) => item.x) || [];

  // Define a set of consistent colors
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

  // Construct datasets for Chart.js
  const chartDatasets = series.map((s: any, index: number) => ({
    type: s.type === 'column' ? 'bar' : 'line', // Map to Chart.js types
    label: s.name, // Use 'name' from series as label
    backgroundColor: s.color || defaultColors[index % defaultColors.length],
    borderColor: s.color || defaultColors[index % defaultColors.length],
    borderWidth: s.borderWidth || 2,
    fill: s.fill || false,
    tension: s.tension || 0.4,
    yAxisID: s.axis, // Assign to specific Y-axis (y1 or y2)
    data: s.data.map((item: any) => item.y), // Extract 'y' values for data
  }));

  const chartData = {
    labels: chartLabels,
    datasets: chartDatasets,
  };

  // Chart.js options structure
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: options?.interaction ?? { mode: 'index', intersect: false },
    stacked: options?.stacked ?? false,
    plugins: {
      title: {
        display: false, // Title is handled by CardTitle
      },
      legend: {
        display: options?.legend?.display ?? true,
        position: options?.legend?.position || 'top',
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          label: function(context: any) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += new Intl.NumberFormat('fr-FR', { style: 'decimal' }).format(context.parsed.y);
            }
            return label;
          }
        }
      },
    },
    scales: {
      x: {
        title: {
          display: axes?.x?.title?.display ?? false,
          text: axes?.x?.title?.text || '',
        },
      },
      y: { // This corresponds to y1 in the JSON (first y-axis)
        type: axes?.y1?.type || 'linear',
        display: axes?.y1?.display ?? true,
        position: axes?.y1?.position || 'left',
        title: {
          display: axes?.y1?.title?.display ?? false,
          text: axes?.y1?.title?.text || '',
        },
        grid: {
          drawOnChartArea: true,
        },
      },
      y1: { // This corresponds to y2 in the JSON (second y-axis)
        type: axes?.y2?.type || 'linear',
        display: axes?.y2?.display ?? true,
        position: axes?.y2?.position || 'right',
        grid: {
          drawOnChartArea: axes?.y2?.grid?.drawOnChartArea ?? false, // Only draw grid for one axis by default
        },
        title: {
          display: axes?.y2?.title?.display ?? false,
          text: axes?.y2?.title?.text || '',
        },
      },
    },
  };

  return (
    <Card className="w-full h-96">
      {title && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent className="h-[calc(100%-4rem)] p-4">
        <Bar data={chartData} options={chartOptions} />
      </CardContent>
    </Card>
  );
};

export default ComboChartCanvas;