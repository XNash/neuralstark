// frontend/src/components/canvas/TableCanvas.tsx
import React from 'react';

interface TableCanvasProps {
  canvasData: any; // This will be the 'canvas' object from the backend response
}

const TableCanvas: React.FC<TableCanvasProps> = ({ canvasData }) => {
  const { title, columns, data, config } = canvasData;

  return (
    <div style={{ width: config?.width || '100%', height: config?.height || 'auto', overflowX: 'auto' }}>
      {title && <h3>{title}</h3>}
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            {columns.map((col: any) => (
              <th key={col.field} style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>
                {col.title}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row: any, rowIndex: number) => (
            <tr key={rowIndex}>
              {columns.map((col: any) => (
                <td key={col.field} style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {row[col.field]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TableCanvas;