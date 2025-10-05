import { cn } from '@/lib/utils';
import { Button } from './ui/button';
import {
  MessageSquare,
  FileText,
  Home,
  Bot
} from 'lucide-react';

interface SidebarProps {
  className?: string;
  activeTab: 'dashboard' | 'chat' | 'files';
  onTabChange: (tab: 'dashboard' | 'chat' | 'files') => void;
}

const sidebarItems = [
  {
    id: 'dashboard' as const,
    label: 'Dashboard',
    icon: Home,
  },
  {
    id: 'chat' as const,
    label: 'Chat',
    icon: MessageSquare,
  },
  {
    id: 'files' as const,
    label: 'Files',
    icon: FileText,
  },
];

export const Sidebar = ({
  className,
  activeTab,
  onTabChange,
}) => {
  return (
    <div className={cn("pb-12 w-64", className)}>
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <div className="flex items-center mb-6">
            <Bot className="h-8 w-8 mr-3 text-primary" />
            <h2 className="text-lg font-semibold tracking-tight">
              NeuralStark
            </h2>
          </div>
          <div className="space-y-1">
            <h3 className="mb-2 px-4 text-sm font-semibold tracking-tight text-muted-foreground">
              Navigation
            </h3>
            {sidebarItems.map((item) => (
              <Button
                key={item.id}
                variant={activeTab === item.id ? "secondary" : "ghost"}
                className="w-full justify-start"
                onClick={() => onTabChange(item.id)}
              >
                <item.icon className="mr-2 h-4 w-4" />
                {item.id === 'dashboard' ? 'Tableau de Bord' : item.id === 'chat' ? 'Chat' : 'Fichiers'}
                {activeTab === item.id && (
                  <div className="ml-auto w-2 h-2 bg-primary rounded-full" />
                )}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};