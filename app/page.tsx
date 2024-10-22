"use client"

import React, { useState } from 'react'
import { ThemeProvider } from 'next-themes'
import { SidebarComponent } from '@/components/SidebarComponent'
import { Dashboard } from '@/components/Dashboard'
import { DatabaseManagement } from '@/components/DatabaseManagement'
import { TableCRUD } from '@/components/TableCRUD'
import { Settings } from '@/components/Settings'
import { AssetTagGenerator } from '@/components/AssetTagGenerator'
import { SidebarProvider } from '@/components/ui/sidebar'

export default function Tagger() {
  const [activeSection, setActiveSection] = useState('dashboard')

  const renderContent = () => {
    if (activeSection === 'dashboard') {
      return <Dashboard setActiveSection={setActiveSection} />
    } else if (activeSection === 'databaseManagement') {
      return <DatabaseManagement setActiveSection={setActiveSection} />
    } else if (activeSection.startsWith('databaseManagement.')) {
      const tableName = activeSection.split('.')[1]
      const initialRecords = [
        { id: 1, name: 'Example 1', code: 'EX1' },
        { id: 2, name: 'Example 2', code: 'EX2' },
      ]
      return <TableCRUD tableName={tableName} initialRecords={initialRecords} />
    } else if (activeSection === 'settings') {
      return <Settings />
    } else if (activeSection === 'assetTagGenerator') {
      return <AssetTagGenerator />
    } else {
      return (
        <div className="text-center text-gray-500 mt-20">
          Content for {activeSection} goes here.
        </div>
      )
    }
  }

  return (
    <ThemeProvider attribute="class" defaultTheme="dark">
      <SidebarProvider>
        <div className="flex h-screen bg-background text-foreground">
          <SidebarComponent setActiveSection={setActiveSection} activeSection={activeSection} />
          <main className="flex-1 overflow-y-auto p-6">
            <h2 className="text-3xl font-bold mb-6">
              {activeSection === 'dashboard' && 'Dashboard'}
              {activeSection === 'assetTagGenerator' && 'Asset Tag Generator'}
              {activeSection === 'databaseManagement' && 'Database Management'}
              {activeSection.startsWith('databaseManagement.') && `${activeSection.split('.')[1]} Management`}
              {activeSection === 'userManagement' && 'User Management'}
              {activeSection === 'settings' && 'Settings'}
            </h2>
            {renderContent()}
          </main>
        </div>
      </SidebarProvider>
    </ThemeProvider>
  )
}
