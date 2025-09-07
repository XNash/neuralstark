// frontend/src/components/canvas/KpiDashboardCanvas.tsx
import React from 'react';

interface KpiDashboardCanvasProps {
  canvasData: any; // This will be the 'canvas' object from the backend response
}

const KpiDashboardCanvas: React.FC<KpiDashboardCanvasProps> = ({ canvasData }) => {
  const { title, kpis, config } = canvasData;

  const formatValue = (value: any, format: string, max?: number) => {
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'EUR' }).format(value);
      case 'percentage':
        return `${value}%`;
      case 'rating':
        return `${value}/${max || 5}`;
      case 'number':
      default:
        return new Intl.NumberFormat('en-US').format(value);
    }
  };

  const getChangeIndicator = (change: number, changeType: string) => {
    if (change === undefined || change === null) return null;
    const isPositive = change > 0;
    const arrow = isPositive ? '▲' : '▼';
    const color = isPositive ? 'green' : 'red';
    const formattedChange = changeType === 'percentage' ? `${Math.abs(change)}%` : Math.abs(change);
    return <span style={{ color }}>{arrow} {formattedChange}</span>;
  };

  return (
    <div style={{ width: config?.width || '100%', padding: '16px', border: '1px solid #eee', borderRadius: '8px' }}>
      {title && <h3 style={{ textAlign: 'center', marginBottom: '20px' }}>{title}</h3>}
      <div style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${config?.columns || 2}, 1fr)`,
        gap: '20px',
      }}>
        {kpis.map((kpi: any) => (
          <div key={kpi.id} style={{
            border: '1px solid #ddd',
            borderRadius: '8px',
            padding: '16px',
            textAlign: 'center',
            backgroundColor: '#fff',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}>
            <div style={{ fontSize: '1.2em', fontWeight: 'bold', color: kpi.color || '#333' }}>{kpi.title}</div>
            <div style={{ fontSize: '2em', margin: '10px 0' }}>
              {formatValue(kpi.value, kpi.format, kpi.max)}
            </div>
            {kpi.change !== undefined && kpi.change !== null && (
              <div style={{ fontSize: '0.9em', color: '#666' }}>
                {getChangeIndicator(kpi.change, kpi.change_type)} {kpi.period}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default KpiDashboardCanvas;