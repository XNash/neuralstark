import { Sidebar } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { Chat } from './components/Chat';
import { Files } from './components/Files';
import { ScrollArea } from './components/ui/scroll-area';
import { Scheduling } from './components/Scheduling';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';

function App() {
  return (
    <div className="flex h-screen bg-background text-foreground">
      <Sidebar />
      <main className="flex-1 flex flex-col">
        <ScrollArea className="flex-1">
          <Tabs defaultValue="dashboard" className="flex-1">
            <div className="border-b">
              <TabsList className="bg-transparent px-4">
                <TabsTrigger value="dashboard">Tableau de Bord</TabsTrigger>
                <TabsTrigger value="chat">Chat</TabsTrigger>
                <TabsTrigger value="documents">Documents</TabsTrigger>
                <TabsTrigger value="scheduling">Planification</TabsTrigger>
              </TabsList>
            </div>
            <TabsContent value="dashboard">
              <Dashboard />
            </TabsContent>
            <TabsContent value="chat">
              <Chat />
            </TabsContent>
            <TabsContent value="documents">
              <Files />
            </TabsContent>
            <TabsContent value="scheduling">
              <Scheduling />
            </TabsContent>
          </Tabs>
        </ScrollArea>
      </main>
    </div>
  );
}

export default App;
