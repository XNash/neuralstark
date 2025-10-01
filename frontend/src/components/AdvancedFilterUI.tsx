import React from 'react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Label } from './ui/label';

interface AdvancedFilterUIProps {
  onFilterChange: (filters: any) => void;
}

export const AdvancedFilterUI: React.FC<AdvancedFilterUIProps> = ({ onFilterChange }) => {
  const [filters, setFilters] = React.useState({
    start_date: '',
    end_date: '',
    document_type: '',
    tags: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const handleApplyFilters = () => {
    onFilterChange(filters);
  };

  return (
    <div className="p-4 border-t">
      <h4 className="text-lg font-semibold mb-2">Filtres avancés</h4>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="start_date">Date de début</Label>
          <Input type="date" id="start_date" name="start_date" value={filters.start_date} onChange={handleChange} />
        </div>
        <div>
          <Label htmlFor="end_date">Date de fin</Label>
          <Input type="date" id="end_date" name="end_date" value={filters.end_date} onChange={handleChange} />
        </div>
        <div>
          <Label htmlFor="document_type">Type de document</Label>
          <Input id="document_type" name="document_type" value={filters.document_type} onChange={handleChange} />
        </div>
        <div>
          <Label htmlFor="tags">Tags (séparés par des virgules)</Label>
          <Input id="tags" name="tags" value={filters.tags} onChange={handleChange} />
        </div>
      </div>
      <Button onClick={handleApplyFilters} className="mt-4">Appliquer les filtres</Button>
    </div>
  );
};