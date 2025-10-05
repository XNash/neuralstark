import { cn } from '@/lib/utils';
import { Button } from './ui/button';
import { Separator } from './ui/separator';
import {
  MessageSquare,
  FileText,
  Home,
  Settings,
  User,
  BarChart3,
  Database,
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

const quickActions = [
  {
    id: 'analytics',
    label: 'Analytics',
    icon: BarChart3,
  },
  {
    id: 'database',
    label: 'Database',
    icon: Database,
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
  },
];

export const Sidebar: React.FC<SidebarProps> = ({
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
        <Separator />
        <div className="px-3 py-2">
          <h3 className="mb-2 px-4 text-sm font-semibold tracking-tight text-muted-foreground">
            Actions Rapides
          </h3>
          <div className="space-y-1">
            {quickActions.map((item) => (
              <Button
                key={item.id}
                variant="ghost"
                className="w-full justify-start"
                disabled
              >
                <item.icon className="mr-2 h-4 w-4" />
                {item.id === 'analytics' ? 'Analytique' : item.id === 'database' ? 'Base de Données' : 'Paramètres'}
              </Button>
            ))}
          </div>
        </div>
        <Separator />
        <div className="px-3 py-2">
          <div className="flex items-center">
            <User className="mr-2 h-4 w-4" />
            <span className="text-sm font-medium">Profil Utilisateur</span>
          </div>
        </div>
      </div>
    </div>
  );
};