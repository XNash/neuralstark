import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';

interface TableCanvasProps {
  canvasData: any; // This will be the 'canvas' object from the backend response
}

const TableCanvas: React.FC<TableCanvasProps> = ({ canvasData }) => {
  const { title, columns, data } = canvasData;

  return (
    <Card className="w-full">
      {title && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                {columns.map((col: any) => (
                  <TableHead key={col.field}>{col.title}</TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((row: any, rowIndex: number) => (
                <TableRow key={rowIndex}>
                  {columns.map((col: any) => (
                    <TableCell key={col.field}>{row[col.field]}</TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

export default TableCanvas;