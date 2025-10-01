import React, { useState, useEffect } from 'react';
import { apiClient, type ScheduledReport } from '../lib/api-client';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';

export const Scheduling: React.FC = () => {
  const [schedules, setSchedules] = useState<ScheduledReport[]>([]);
  const [newSchedule, setNewSchedule] = useState({
    name: '',
    tool_name: '',
    tool_input: '{}',
    interval_minutes: 60,
  });

  useEffect(() => {
    fetchSchedules();
  }, []);

  const fetchSchedules = async () => {
    const fetchedSchedules = await apiClient.getScheduledReports();
    setSchedules(fetchedSchedules);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewSchedule({ ...newSchedule, [name]: value });
  };

  const handleCreateSchedule = async () => {
    try {
      const toolInput = JSON.parse(newSchedule.tool_input);
      await apiClient.createScheduledReport({ ...newSchedule, tool_input: toolInput });
      fetchSchedules();
    } catch (error) {
      console.error("Error creating schedule:", error);
      // Handle error in UI
    }
  };

  return (
    <div className="p-4 md:p-8 pt-6">
      <h2 className="text-3xl font-bold tracking-tight mb-4">Planification des rapports</h2>
      <div className="grid gap-8 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Créer un nouveau rapport planifié</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="name">Nom du rapport</Label>
              <Input id="name" name="name" value={newSchedule.name} onChange={handleInputChange} />
            </div>
            <div>
              <Label htmlFor="tool_name">Nom de l'outil</Label>
              <Input id="tool_name" name="tool_name" value={newSchedule.tool_name} onChange={handleInputChange} />
            </div>
            <div>
              <Label htmlFor="tool_input">Paramètres de l'outil (JSON)</Label>
              <Input id="tool_input" name="tool_input" value={newSchedule.tool_input} onChange={handleInputChange} />
            </div>
            <div>
              <Label htmlFor="interval_minutes">Intervalle (minutes)</Label>
              <Input id="interval_minutes" name="interval_minutes" type="number" value={newSchedule.interval_minutes} onChange={handleInputChange} />
            </div>
            <Button onClick={handleCreateSchedule}>Planifier le rapport</Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Rapports planifiés</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nom</TableHead>
                  <TableHead>Outil</TableHead>
                  <TableHead>Intervalle (min)</TableHead>
                  <TableHead>Dernière exécution</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {schedules.map((schedule) => (
                  <TableRow key={schedule.name}>
                    <TableCell>{schedule.name}</TableCell>
                    <TableCell>{schedule.tool_name}</TableCell>
                    <TableCell>{schedule.interval_minutes}</TableCell>
                    <TableCell>{schedule.last_run ? new Date(schedule.last_run).toLocaleString() : 'Jamais'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};