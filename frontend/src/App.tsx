import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { Chat } from './components/Chat';
import { Files } from './components/Files';
import { ScrollArea } from './components/ui/scroll-area';

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'chat' | 'files'>('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'chat':
        return (
          <Chat />
        );
      case 'files':
        return (
          <Files />
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        {/* Sidebar */}
        <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
          <div className="flex-1 flex flex-col min-h-0 border-r bg-card">
            <ScrollArea className="flex-1">
              <Sidebar
                activeTab={activeTab}
                onTabChange={setActiveTab}
              />
            </ScrollArea>
          </div>
        </div>

        {/* Main content */}
        <div className="flex flex-col flex-1 pl-0 md:pl-64">
          <main className="flex-1">
            {renderContent()}
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
