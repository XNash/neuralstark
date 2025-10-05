// frontend/src/components/canvas/ComboChartCanvas.tsx
import React from 'react';
import { Bar } from 'react-chartjs-2';
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
  const { series, options, plugins, axes } = canvasData; // Destructure 'series' and 'axes'

  // Extract labels from the first series (assuming all series share the same labels)
  const chartLabels = series[0]?.data.map((item: any) => item.x) || [];

  // Construct datasets for Chart.js
  const chartDatasets = series.map((s: any) => ({
    type: s.type === 'column' ? 'bar' : 'line', // Map to Chart.js types
    label: s.name, // Use 'name' from series as label
    backgroundColor: s.color,
    borderColor: s.color,
    borderWidth: s.borderWidth,
    fill: s.fill,
    tension: s.tension,
    yAxisID: s.axis, // Assign to specific Y-axis (y1 or y2)
    data: s.data.map((item: any) => item.y), // Extract 'y' values for data
  }));

  const chartData = {
    labels: chartLabels,
    datasets: chartDatasets,
  };

  // Chart.js options structure
  const chartOptions = {
    responsive: options?.responsive ?? true,
    maintainAspectRatio: false,
    interaction: options?.interaction ?? { mode: 'index', intersect: false },
    stacked: options?.stacked ?? false,
    plugins: {
      title: {
        display: plugins?.title?.display ?? true,
        text: plugins?.title?.text || '',
      },
      legend: {
        display: plugins?.legend?.display ?? true,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      y: { // This corresponds to y1 in the JSON (first y-axis)
        type: axes?.y1?.type || 'linear',
        display: axes?.y1?.display ?? true,
        position: axes?.y1?.position || 'left',
        title: {
          display: axes?.y1?.title?.display ?? true,
          text: axes?.y1?.title?.text || '',
        },
      },
      y1: { // This corresponds to y2 in the JSON (second y-axis)
        type: axes?.y2?.type || 'linear',
        display: axes?.y2?.display ?? true,
        position: axes?.y2?.position || 'right',
        grid: {
          drawOnChartArea: axes?.y2?.grid?.drawOnChartArea ?? false,
        },
        title: {
          display: axes?.y2?.title?.display ?? true,
          text: axes?.y2?.title?.text || '',
        },
      },
    },
  };

  return (
    <div style={{ width: options?.width || '100%', height: options?.height || '400px' }}>
      <Bar data={chartData} options={chartOptions} />
    </div>
  );
};

export default ComboChartCanvas;