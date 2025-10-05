import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { apiClient } from '../lib/api';
import {
  MessageSquare,
  FileText,
  Activity,
  Users,
  TrendingUp,
  RefreshCw,
  Bot,
  Database
} from 'lucide-react';

interface DashboardStats {
  totalChats: number;
  totalDocuments: number;
  activeSessions: number;
  systemStatus: 'online' | 'offline' | 'maintenance';
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalChats: 0,
    totalDocuments: 0,
    activeSessions: 1,
    systemStatus: 'online',
  });
  const [documents, setDocuments] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      const [documentsResponse, healthResponse] = await Promise.all([
        apiClient.getDocuments(),
        apiClient.healthCheck(),
      ]);

      // Ensure documentsResponse has the expected structure
      const documents = documentsResponse?.indexed_documents || [];
      setDocuments(documents);
      setStats(prev => ({
        ...prev,
        totalDocuments: documents.length,
        systemStatus: healthResponse.status === 'ok' ? 'online' : 'offline',
      }));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setDocuments([]);
      setStats(prev => ({ ...prev, systemStatus: 'offline', totalDocuments: 0 }));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const statCards = [
    {
      title: "Documents Totaux",
      value: stats.totalDocuments,
      description: "Documents indexés dans la base de connaissances",
      icon: FileText,
      color: "text-blue-600",
    },
    {
      title: "Sessions Actives",
      value: stats.activeSessions,
      description: "Sessions utilisateur actives actuelles",
      icon: Users,
      color: "text-green-600",
    },
    {
      title: "Statut du Système",
      value: stats.systemStatus,
      description: "Statut de l'API NeuralStark",
      icon: Activity,
      color: stats.systemStatus === 'online' ? "text-green-600" : "text-red-600",
      isStatus: true,
    },
    {
      title: "Interactions IA",
      value: stats.totalChats,
      description: "Interactions de chat totales",
      icon: MessageSquare,
      color: "text-purple-600",
    },
  ];

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Tableau de Bord</h2>
        <div className="flex items-center space-x-2">
          <Button
            onClick={fetchDashboardData}
            disabled={isLoading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Actualiser
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {card.title}
              </CardTitle>
              <card.icon className={`h-4 w-4 ${card.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {card.isStatus ? (
                  <Badge variant={card.value === 'online' ? 'default' : 'destructive'}>
                    {card.value === 'online' ? 'en ligne' : 'hors ligne'}
                  </Badge>
                ) : (
                  card.value
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                {card.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Documents Récents</CardTitle>
            <CardDescription>
              Derniers documents indexés dans votre base de connaissances
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px]">
              {documents.length > 0 ? (
                <div className="space-y-4">
                  {documents.slice(0, 10).map((doc, index) => (
                    <div
                      key={index}
                      className="flex items-center space-x-4 p-3 border rounded-lg hover:bg-muted/50"
                    >
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <div className="flex-1 space-y-1">
                        <p className="text-sm font-medium leading-none">
                          {doc}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Document indexé
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-[200px] text-center">
                  <Database className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">Aucun document indexé pour l'instant</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Les documents apparaîtront ici une fois indexés
                  </p>
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Aperçu du Système</CardTitle>
            <CardDescription>
              Statut et capacités du système NeuralStark IA
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <Bot className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-sm font-medium">Agent IA</p>
                  <p className="text-xs text-muted-foreground">
                    Propulsé par Google Gemini
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <Database className="h-8 w-8 text-blue-600" />
                <div>
                  <p className="text-sm font-medium">Base de Connaissances</p>
                  <p className="text-xs text-muted-foreground">
                    {documents.length} documents indexés
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <TrendingUp className="h-8 w-8 text-green-600" />
                <div>
                  <p className="text-sm font-medium">Performance</p>
                  <p className="text-xs text-muted-foreground">
                    Traitement en temps réel
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};