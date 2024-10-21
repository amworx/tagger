import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Building, Database, Users, Tag } from 'lucide-react';

export function Dashboard({ setActiveSection }: { setActiveSection: (section: string) => void }) {
  const cards = [
    { title: 'Buildings', icon: <Building className="h-6 w-6" />, value: '12' },
    { title: 'Departments', icon: <Database className="h-6 w-6" />, value: '8' },
    { title: 'Users', icon: <Users className="h-6 w-6" />, value: '56' },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Asset Tag Generator</CardTitle>
          <Tag className="h-6 w-6" />
        </CardHeader>
        <CardContent>
          <Button onClick={() => setActiveSection('assetTagGenerator')} className="w-full">
            Generate Tags
          </Button>
        </CardContent>
      </Card>
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
            {card.icon}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
