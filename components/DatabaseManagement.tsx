import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export function DatabaseManagement({ setActiveSection }: { setActiveSection: (section: string) => void }) {
  const tables = [
    { name: 'Asset Types', records: 15, section: 'assetTypes' },
    { name: 'Buildings', records: 12, section: 'buildings' },
    { name: 'Departments', records: 8, section: 'departments' },
  ];

  const handleClear = (tableName: string) => {
    console.log(`Clearing ${tableName} table`);
    // Implement actual clearing logic here
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        {tables.map((table) => (
          <Card key={table.name}>
            <CardHeader>
              <CardTitle>{table.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-2">Records: {table.records}</p>
              <div className="flex space-x-2">
                <Button size="sm" onClick={() => setActiveSection(`databaseManagement.${table.section}`)}>View</Button>
                <Button size="sm">Export</Button>
                <Button size="sm">Import</Button>
                <Button size="sm" variant="destructive" onClick={() => handleClear(table.name)}>Clear</Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
