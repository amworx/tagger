import React, { useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface Record {
  id: number;
  name: string;
  code: string;
}

export function TableCRUD({ tableName, initialRecords }: { tableName: string; initialRecords: Record[] }) {
  const [records, setRecords] = useState(initialRecords);
  const [newRecord, setNewRecord] = useState({ name: '', code: '' });

  const addRecord = () => {
    setRecords([...records, { id: records.length + 1, ...newRecord }]);
    setNewRecord({ name: '', code: '' });
  };

  const updateRecord = (id: number, updatedRecord: Partial<Record>) => {
    setRecords(records.map(record => record.id === id ? { ...record, ...updatedRecord } : record));
  };

  const deleteRecord = (id: number) => {
    setRecords(records.filter(record => record.id !== id));
  };

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">{tableName}</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Code</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {records.map((record) => (
            <TableRow key={record.id}>
              <TableCell>{record.name}</TableCell>
              <TableCell>{record.code}</TableCell>
              <TableCell>
                <Button size="sm" className="mr-2" onClick={() => updateRecord(record.id, { name: 'Updated ' + record.name })}>Edit</Button>
                <Button size="sm" variant="destructive" onClick={() => deleteRecord(record.id)}>Delete</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <div className="mt-4 flex space-x-2">
        <Input
          placeholder="Name"
          value={newRecord.name}
          onChange={(e) => setNewRecord({ ...newRecord, name: e.target.value })}
        />
        <Input
          placeholder="Code"
          value={newRecord.code}
          onChange={(e) => setNewRecord({ ...newRecord, code: e.target.value })}
        />
        <Button onClick={addRecord}>Add Record</Button>
      </div>
    </div>
  );
}
