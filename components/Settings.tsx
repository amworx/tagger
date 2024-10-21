import React from 'react';
import { useTheme } from 'next-themes';
import { Switch } from '@/components/ui/switch';
import { Sun, Moon } from 'lucide-react';

export function Settings() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold mb-4">Settings</h2>
      <div className="flex items-center space-x-2">
        <Sun className="h-4 w-4" />
        <Switch
          checked={theme === 'dark'}
          onCheckedChange={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        />
        <Moon className="h-4 w-4" />
        <span className="ml-2">{theme === 'dark' ? 'Dark' : 'Light'} Mode</span>
      </div>
    </div>
  );
}
