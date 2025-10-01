import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { ArrowUp, ArrowDown } from 'lucide-react';

interface KpiDashboardCanvasProps {
  canvasData: any; // This will be the 'canvas' object from the backend response
}

const KpiDashboardCanvas: React.FC<KpiDashboardCanvasProps> = ({ canvasData }) => {
  const { title, kpis, config } = canvasData;

  const formatValue = (value: any, format: string, max?: number) => {
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value);
      case 'percentage':
        return `${new Intl.NumberFormat('fr-FR').format(value)}%`;
      case 'rating':
        return `${new Intl.NumberFormat('fr-FR').format(value)}/${max || 5}`;
      case 'number':
      default:
        return new Intl.NumberFormat('fr-FR').format(value);
    }
  };

  const getChangeIndicator = (change: number, changeType: string) => {
    if (change === undefined || change === null) return null;
    const isPositive = change > 0;
    const Icon = isPositive ? ArrowUp : ArrowDown;
    const colorClass = isPositive ? 'text-green-500' : 'text-red-500';
    const formattedChange = changeType === 'percentage' ? `${Math.abs(change)}%` : new Intl.NumberFormat('fr-FR').format(Math.abs(change));
    
    return (
      <span className={`flex items-center gap-1 ${colorClass}`}>
        <Icon className="h-4 w-4" />
        {formattedChange}
      </span>
    );
  };

  return (
    <Card className="w-full">
      {title && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent>
        <div
          className="grid gap-4"
          style={{
            gridTemplateColumns: `repeat(${config?.columns || 2}, 1fr)`,
          }}
        >
          {kpis.map((kpi: any) => (
            <div
              key={kpi.id}
              className="flex flex-col items-center justify-center p-4 border rounded-lg shadow-sm bg-background"
            >
              <div className="text-sm font-medium text-muted-foreground">{kpi.title}</div>
              <div className="text-3xl font-bold mt-2" style={{ color: kpi.color || '#333' }}>
                {formatValue(kpi.value, kpi.format, kpi.max)}
              </div>
              {kpi.change !== undefined && kpi.change !== null && (
                <div className="text-sm mt-2 flex items-center gap-1">
                  {getChangeIndicator(kpi.change, kpi.change_type)} {kpi.period && <span className="text-muted-foreground">({kpi.period})</span>}
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default KpiDashboardCanvas;