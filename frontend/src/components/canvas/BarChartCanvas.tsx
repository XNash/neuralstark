import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';

interface BarChartCanvasProps {
  canvasData: any; // This will be the 'canvas' object from the backend response
}

const BarChartCanvas: React.FC<BarChartCanvasProps> = ({ canvasData }) => {
  const { title, data, config } = canvasData;

  const chartData = {
    labels: data.map((item: any) => item.category),
    datasets: [
      {
        label: config?.label || 'Valeur',
        data: data.map((item: any) => item.value),
        backgroundColor: config?.backgroundColor || 'rgba(75, 192, 192, 0.6)',
        borderColor: config?.borderColor || 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: config?.legendPosition || 'top',
      },
      title: {
        display: false, // Title is handled by CardTitle
        text: title,
      },
      tooltip: {
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
      }
    },
    scales: {
      x: {
        title: {
          display: config?.xAxisTitle !== undefined,
          text: config?.xAxisTitle || '',
        },
      },
      y: {
        title: {
          display: config?.yAxisTitle !== undefined,
          text: config?.yAxisTitle || '',
        },
        beginAtZero: true,
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
        <Bar data={chartData} options={options} />
      </CardContent>
    </Card>
  );
};

export default BarChartCanvas;