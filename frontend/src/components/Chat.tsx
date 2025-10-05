import React, { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { apiClient } from '../lib/api';
import { Send, MessageSquare, Bot, User, AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import ReactMarkdown from 'react-markdown';
import BarChartCanvas from './canvas/BarChartCanvas';
import PieChartCanvas from './canvas/PieChartCanvas';
import TableCanvas from './canvas/TableCanvas';
import KpiDashboardCanvas from './canvas/KpiDashboardCanvas';
import ComboChartCanvas from './canvas/ComboChartCanvas';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  TimeScale,
  Filler,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  TimeScale,
  Filler
);

interface Message {
  id: string;
  sender: 'user' | 'ai';
  content: string | { canvas: any }; // Update content type to handle canvas objects
  timestamp: Date;
}

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setChatError(null);

    try {
      const response = await apiClient.chat(inputValue);
      
      let processedResponse = response.response;

      if (typeof processedResponse === 'string') {
        const jsonMatch = processedResponse.match(/```json\n([\s\S]*?)\n```/);
        if (jsonMatch && jsonMatch[1]) {
          try {
            processedResponse = JSON.parse(jsonMatch[1]);
          } catch (e) {
            console.error("Failed to parse JSON from markdown block:", e);
            // Fallback to original string if parsing fails
          }
        }
      }

      // Now use processedResponse instead of response.response in the subsequent logic
      if (typeof processedResponse === 'object' && processedResponse !== null && 'canvas' in processedResponse) {
        setMessages((prevMessages) => [
          ...prevMessages,
          { id: (Date.now() + 1).toString(), sender: 'ai', content: { canvas: processedResponse.canvas }, timestamp: new Date() },
        ]);
      } else {
        // Regular text response (or if JSON parsing failed, it will be the original string)
        setMessages((prevMessages) => [
          ...prevMessages,
          { id: (Date.now() + 1).toString(), sender: 'ai', content: processedResponse as string, timestamp: new Date() },
        ]);
      }

    } catch (error) {
      setChatError(error instanceof Error ? error.message : 'Une erreur inconnue est survenue.');
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `Erreur : ${error instanceof Error ? error.message : 'Erreur inconnue'}`, 
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value);
  };

  

  return (
    <div className="flex-1 flex flex-col">
      <div className="p-4 md:p-8 pt-6 flex flex-col flex-1">
        <div className="flex items-center justify-between space-y-2 mb-4">
          <div className="flex items-center space-x-2">
            <MessageSquare className="h-6 w-6" />
            <h2 className="text-3xl font-bold tracking-tight">Chat IA</h2>
          </div>
          <Badge variant="secondary" className="flex items-center gap-1">
            <Bot className="h-3 w-3" />
            NeuralStark IA
          </Badge>
        </div>

        {chatError && (
          <Alert variant="destructive" className="mb-4">
            <AlertTriangle className="h-5 w-5" />
            <AlertTitle>Erreur du Chat</AlertTitle>
            <AlertDescription>{chatError}</AlertDescription>
          </Alert>
        )}

        <div className="flex flex-col flex-1 justify-between">
          <ScrollArea className="flex-1 px-6">
            <div className="space-y-4 py-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center flex-1 text-center">
                  <Bot className="h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Démarrer une Conversation</h3>
                  <p className="text-muted-foreground max-w-sm">
                    Demandez à NeuralStark IA tout sur vos documents ou demandez des visualisations de données.
                    L'IA peut générer des graphiques, des diagrammes et des tableaux de bord interactifs.
                  </p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${
                      message.sender === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {message.sender !== 'user' && (
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                          <Bot className="h-4 w-4 text-primary-foreground" />
                        </div>
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] p-3 rounded-xl shadow-md ${
                        message.sender === 'user'
                          ? 'bg-primary text-primary-foreground ml-auto rounded-br-none'
                          : 'bg-muted rounded-bl-none'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <div className="flex items-center gap-1">
                          {message.sender === 'user' ? (
                            <User className="h-3 w-3" />
                          ) : (
                            <Bot className="h-3 w-3" />
                          )}
                          <span className="text-xs font-medium">
                            {message.sender === 'user' ? 'Vous' : 'NeuralStark'}
                          </span>
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {message.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="whitespace-pre-wrap text-sm">
                        {typeof message.content === 'object' && 'canvas' in message.content ? (
                          // Render canvas component
                          (() => {
                            const canvasData = message.content.canvas;
                            switch (canvasData.type) {
                              case 'bar_chart':
                                return <BarChartCanvas canvasData={canvasData} />;
                              case 'pie_chart':
                                return <PieChartCanvas canvasData={canvasData} />;
                              case 'table':
                                return <TableCanvas canvasData={canvasData} />;
                              case 'kpi_dashboard':
                                return <KpiDashboardCanvas canvasData={canvasData} />;
                              case 'combo_chart':
                                return <ComboChartCanvas canvasData={canvasData} />;
                              // Add cases for all other canvas types you support
                              default:
                                return <div>Unsupported visualization type: {canvasData.type}</div>;
                            }
                          })()
                        ) : (
                          // Render text/markdown content
                          <div className="prose prose-sm max-w-none"> {/* Apply className to a wrapper div */}
                            <ReactMarkdown>
                              {message.content as string}
                            </ReactMarkdown>
                          </div>
                        )}
                      </div>
                    </div>
                    {message.sender === 'user' && (
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                          <User className="h-4 w-4 text-secondary-foreground" />
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                      <Bot className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </div>
                  <div className="bg-muted max-w-[70%] p-3 rounded-xl rounded-bl-none shadow-md">
                    <div className="flex items-center gap-2">
                      <Bot className="h-3 w-3" />
                      <span className="text-xs font-medium">NeuralStark réfléchit...</span>
                    </div>
                    <div className="flex items-center gap-1 mt-1">
                      <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                      <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
          <div className="border-t p-4">
            <div className="flex gap-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Tapez votre message ici..."
                className="flex-1"
                disabled={isLoading}
              />
              <Button
                onClick={handleSendMessage}
                disabled={isLoading || !inputValue.trim()}
                size="icon"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Appuyez sur Entrée pour envoyer • NeuralStark IA peut générer des graphiques, des tableaux de bord et analyser vos données
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};