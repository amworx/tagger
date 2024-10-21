"use client"

import { useState } from 'react'
import { ThemeProvider, useTheme } from 'next-themes'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Switch } from '@/components/ui/switch'
import { Home, Tag, Database, Users, Building, Settings, LogOut, User, Moon, Sun, ChevronLeft, ChevronRight } from 'lucide-react'
import {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarProvider,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarTrigger,
} from '@/components/ui/sidebar'

function SidebarComponent({ setActiveSection, activeSection }) {
  const [collapsed, setCollapsed] = useState(false)

  const menuItems = [
    { icon: <Home className="h-5 w-5" />, label: 'Dashboard', section: 'dashboard' },
    { icon: <Tag className="h-5 w-5" />, label: 'Asset Tag Generator', section: 'assetTagGenerator' },
    { icon: <Database className="h-5 w-5" />, label: 'Database Management', section: 'databaseManagement' },
    { icon: <Users className="h-5 w-5" />, label: 'User Management', section: 'userManagement' },
    { icon: <Settings className="h-5 w-5" />, label: 'Settings', section: 'settings' },
  ]

  return (
    <Sidebar collapsed={collapsed}>
      <SidebarHeader>
        <h1 className={`text-xl font-bold p-4 ${collapsed ? 'hidden' : ''}`}>Tagger</h1>
      </SidebarHeader>
      <SidebarContent>
        <SidebarMenu>
          {menuItems.map((item) => (
            <SidebarMenuItem key={item.section}>
              <SidebarMenuButton 
                onClick={() => setActiveSection(item.section)}
                active={activeSection === item.section}
              >
                {item.icon}
                {!collapsed && <span className="ml-2">{item.label}</span>}
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>
      <SidebarFooter>
        <UserProfile collapsed={collapsed} />
        <Button variant="ghost" className="w-full justify-start" onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          {!collapsed && <span className="ml-2">Collapse</span>}
        </Button>
      </SidebarFooter>
    </Sidebar>
  )
}

function UserProfile({ collapsed }) {
  const [isOpen, setIsOpen] = useState(false)
  const [userInfo, setUserInfo] = useState({
    name: 'John Doe',
    email: 'john@example.com',
  })

  const handleSave = (e) => {
    e.preventDefault()
    // Implement save logic here
    setIsOpen(false)
  }

  const handleLogout = () => {
    // Implement logout logic here
    console.log('Logging out...')
  }

  return (
    <>
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogTrigger asChild>
          <Button variant="ghost" className="w-full justify-start">
            <User className="h-4 w-4" />
            {!collapsed && <span className="ml-2">{userInfo.name}</span>}
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Profile</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSave} className="space-y-4">
            <div>
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={userInfo.name}
                onChange={(e) => setUserInfo({ ...userInfo, name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={userInfo.email}
                onChange={(e) => setUserInfo({ ...userInfo, email: e.target.value })}
              />
            </div>
            <div className="flex justify-between">
              <Button type="submit">Save</Button>
              <Button variant="outline" onClick={() => setIsOpen(false)}>Cancel</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
      <Button variant="ghost" className="w-full justify-start" onClick={handleLogout}>
        <LogOut className="h-4 w-4" />
        {!collapsed && <span className="ml-2">Logout</span>}
      </Button>
    </>
  )
}

function Dashboard({ setActiveSection }) {
  const cards = [
    { title: 'Buildings', icon: <Building className="h-6 w-6" />, value: '12' },
    { title: 'Departments', icon: <Database className="h-6 w-6" />, value: '8' },
    { title: 'Users', icon: <Users className="h-6 w-6" />, value: '56' },
  ]

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
  )
}

function DatabaseManagement({ setActiveSection }) {
  const tables = [
    { name: 'Asset Types', records: 15, section: 'assetTypes' },
    { name: 'Buildings', records: 12, section: 'buildings' },
    { name: 'Departments', records: 8, section: 'departments' },
  ]

  const handleClear = (tableName) => {
    console.log(`Clearing ${tableName} table`)
    // Implement actual clearing logic here
  }

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
  )
}

function TableCRUD({ tableName, initialRecords }) {
  const [records, setRecords] = useState(initialRecords)
  const [newRecord, setNewRecord] = useState({ name: '', code: '' })

  const addRecord = () => {
    setRecords([...records, { id: records.length + 1, ...newRecord }])
    setNewRecord({ name: '', code: '' })
  }

  const updateRecord = (id, updatedRecord) => {
    setRecords(records.map(record => record.id === id ? { ...record, ...updatedRecord } : record))
  }

  const deleteRecord = (id) => {
    setRecords(records.filter(record => record.id !== id))
  }

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
  )
}

function Settings() {
  const { theme, setTheme } = useTheme()

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
  )
}

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