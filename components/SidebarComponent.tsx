import { useState } from 'react'
import { Home, Tag, Database, Users, Settings, LogOut, User, ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from '@/components/ui/sidebar'

export function SidebarComponent({ setActiveSection, activeSection }: { setActiveSection: (section: string) => void, activeSection: string }) {
  const [collapsed, setCollapsed] = useState(false)

  const menuItems = [
    { icon: <Home className="h-5 w-5" />, label: 'Dashboard', section: 'dashboard' },
    { icon: <Tag className="h-5 w-5" />, label: 'Asset Tag Generator', section: 'assetTagGenerator' },
    { icon: <Database className="h-5 w-5" />, label: 'Database Management', section: 'databaseManagement' },
    { icon: <Users className="h-5 w-5" />, label: 'User Management', section: 'userManagement' },
    { icon: <Settings className="h-5 w-5" />, label: 'Settings', section: 'settings' },
  ]

  return (
    <Sidebar className={`transition-all duration-300 ${collapsed ? 'w-16' : 'w-64'}`}>
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

function UserProfile({ collapsed }: { collapsed: boolean }) {
  const [isOpen, setIsOpen] = useState(false)
  const [userInfo, setUserInfo] = useState({
    name: 'John Doe',
    email: 'john@example.com',
  })

  const handleSave = (e: React.FormEvent) => {
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
