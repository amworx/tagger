import React from 'react'
import { cn } from '@/lib/utils'

export const Sidebar = ({ className, children }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('bg-gray-900 text-white', className)}>{children}</div>
)

export const SidebarHeader = ({ className, children }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('p-4', className)}>{children}</div>
)

export const SidebarContent = ({ className, children }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('flex-1', className)}>{children}</div>
)

export const SidebarFooter = ({ className, children }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('p-4', className)}>{children}</div>
)

export const SidebarMenu = ({ className, children }: React.HTMLAttributes<HTMLUListElement>) => (
  <ul className={cn('space-y-2', className)}>{children}</ul>
)

export const SidebarMenuItem = ({ className, children }: React.HTMLAttributes<HTMLLIElement>) => (
  <li className={cn('', className)}>{children}</li>
)

export const SidebarMenuButton = ({ 
  className, 
  children, 
  active, 
  ...props 
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { active?: boolean }) => (
  <button
    className={cn(
      'w-full text-left px-4 py-2 rounded transition-colors',
      active ? 'bg-gray-800' : 'hover:bg-gray-800',
      className
    )}
    {...props}
  >
    {children}
  </button>
)

export const SidebarProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <>{children}</>
)
