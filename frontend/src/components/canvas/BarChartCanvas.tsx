// frontend/src/components/canvas/BarChartCanvas.tsx
import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components (do this once in your app, e.g., in main.tsx or a central chart config file)
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface BarChartCanvasProps {
  canvasData: any; // This will be the 'canvas' object from the backend response
}

const BarChartCanvas: React.FC<BarChartCanvasProps> = ({ canvasData }) => {
  const { title, data, axes, config } = canvasData;

  // --- Data Transformation for Chart.js ---
  const chartLabels = data.map((item: any) => item.category);
  const chartValues = data.map((item: any) => item.value);
  const backgroundColors = data.map((item: any) => item.color || 'rgba(75, 192, 192, 0.6)');

  const chartData = {
    labels: chartLabels,
    datasets: [
      {
        label: axes?.y?.label || 'Valeur', // Use y-axis label from canvasData or a default
        data: chartValues,
        backgroundColor: backgroundColors,
        borderColor: backgroundColors.map((color: string) => color.replace('0.6', '1')), // Make border opaque
        borderWidth: 1,
      },
    ],
  };

  // --- Chart.js Options Configuration ---
  const chartOptions = {
    responsive: config?.responsive ?? true,
    maintainAspectRatio: false, // Allows custom width/height from config
    plugins: {
      legend: {
        display: config?.legend ?? true,
      },
      title: {
        display: true,
        text: title,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: axes?.x?.label || '',
        },
      },
      y: {
        title: {
          display: true,
          text: axes?.y?.label || '',
        },
        beginAtZero: true, // Common for bar charts
      },
    },
    // You can add more Chart.js options based on the 'config' object in canvasData
  };

  return (
    <div style={{ width: config?.width || '100%', height: config?.height || '400px' }}>
      <Bar data={chartData} options={chartOptions} />
    </div>
  );
};

export default BarChartCanvas;