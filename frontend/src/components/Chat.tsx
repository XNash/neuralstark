import React, { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { apiClient, type Personality, type CanvasTemplate } from '../lib/api-client';
import { Send, MessageSquare, Bot, User, AlertTriangle, Mic, Plus } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import ReactMarkdown from 'react-markdown';
import BarChartCanvas from './canvas/BarChartCanvas';
import PieChartCanvas from './canvas/PieChartCanvas';
import TableCanvas from './canvas/TableCanvas';
import KpiDashboardCanvas from './canvas/KpiDashboardCanvas';
import ComboChartCanvas from './canvas/ComboChartCanvas';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { AdvancedFilterUI } from './AdvancedFilterUI';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  content: string | { canvas: CanvasTemplate };
  timestamp: Date;
}

function isCanvasContent(content: any): content is { canvas: CanvasTemplate } {
    return typeof content === 'object' && content !== null && 'canvas' in content;
}

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [availablePersonalities, setAvailablePersonalities] = useState<{ [key: string]: Personality }>({});
  const [currentPersonalityKey, setCurrentPersonalityKey] = useState<string>('default');
  const [defaultCanvasTemplates, setDefaultCanvasTemplates] = useState<{ [key: string]: any }>({});
  const [userCanvasTemplates, setUserCanvasTemplates] = useState<{ [key: string]: any }>({});
  const [selectedCanvasTemplate, setSelectedCanvasTemplate] = useState<string | null>(null);
  const [newTemplateName, setNewTemplateName] = useState('');
  const [isSavingTemplate, setIsSavingTemplate] = useState(false);
  const [advancedFilters, setAdvancedFilters] = useState({});

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [p, t] = await Promise.all([
          apiClient.getPersonalities(),
          apiClient.getCanvasTemplates(),
        ]);
        setAvailablePersonalities(p.available_personalities);
        setCurrentPersonalityKey(p.current_personality);
        setDefaultCanvasTemplates(t.default_templates);
        setUserCanvasTemplates(t.user_templates);
      } catch (error) {
        console.error("Error fetching initial data:", error);
        setChatError("Impossible de charger les données initiales.");
      }
    };
    fetchInitialData();
  }, []);

  const handleFilterChange = (filters: any) => {
    setAdvancedFilters(filters);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        audioChunksRef.current = [];
        await sendAudioForTranscription(audioBlob);
      };
      mediaRecorderRef.current.start();
      setIsRecording(true);
      setChatError(null);
    } catch (error) {
      console.error("Error starting recording:", error);
      setChatError("Impossible de démarrer l'enregistrement. Assurez-vous que le microphone est autorisé.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendAudioForTranscription = async (audioBlob: Blob) => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'audio.webm');
      const response = await apiClient.stt(formData);
      if (response.text) {
        setInputValue(response.text);
      }
    } catch (error) {
      console.error("Error sending audio for transcription:", error);
      setChatError(error instanceof Error ? error.message : 'Une erreur est survenue lors de la transcription.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveTemplate = async () => {
    if (!newTemplateName.trim()) {
      setChatError("Le nom du modèle ne peut pas être vide.");
      return;
    }
    const lastMessage = messages[messages.length - 1];
    if (!lastMessage || !isCanvasContent(lastMessage.content)) {
      setChatError("Aucun canevas récent à enregistrer comme modèle.");
      return;
    }

    setIsSavingTemplate(true);
    try {
      await apiClient.saveCanvasTemplate(newTemplateName, lastMessage.content.canvas);
      setNewTemplateName('');
      const templates = await apiClient.getCanvasTemplates();
      setUserCanvasTemplates(templates.user_templates);
    } catch (error) {
      console.error("Error saving template:", error);
      setChatError(error instanceof Error ? error.message : "Une erreur est survenue lors de l\u0027enregistrement du modèle.");
    } finally {
      setIsSavingTemplate(false);
    }
  };

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
      const response = await apiClient.chat(inputValue, selectedCanvasTemplate, advancedFilters);
      let processedResponse = response.response;

      if (typeof processedResponse === 'string') {
        const jsonMatch = processedResponse.match(/```json\n([\s\S]*?)\n```/);
        if (jsonMatch && jsonMatch[1]) {
          try {
            processedResponse = JSON.parse(jsonMatch[1]);
          } catch (e) {
            console.error("Failed to parse JSON from markdown block:", e);
          }
        }
      }

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: processedResponse as Message['content'],
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);

    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: `Erreur : ${error instanceof Error ? error.message : 'Erreur inconnue'}`, 
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

  const handlePersonalityChange = async (newPersonalityKey: string) => {
    setIsLoading(true);
    try {
      await apiClient.setPersonality(newPersonalityKey);
      setCurrentPersonalityKey(newPersonalityKey);
    } catch (error) {
      console.error("Error setting personality:", error);
      setChatError(error instanceof Error ? error.message : 'Une erreur est survenue lors du changement de personnalité.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <div className="p-4 md:p-8 pt-6 flex flex-col flex-1">
        <div className="flex items-center justify-between space-y-2 mb-4">
          <div className="flex items-center space-x-2">
            <MessageSquare className="h-6 w-6" />
            <h2 className="text-3xl font-bold tracking-tight">Chat IA</h2>
          </div>
          <div className="flex items-center space-x-2">
            <Select onValueChange={handlePersonalityChange} value={currentPersonalityKey} disabled={isLoading}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Sélectionner une personnalité" />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(availablePersonalities).map(([key, personality]) => (
                  <SelectItem key={key} value={key}>{personality.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select onValueChange={setSelectedCanvasTemplate} value={selectedCanvasTemplate === null ? undefined : selectedCanvasTemplate} disabled={isLoading}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Sélectionner un modèle" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={null}>-- Aucun --</SelectItem>
                <optgroup label="Défaut">
                  {Object.entries(defaultCanvasTemplates).map(([key, template]) => (
                    <SelectItem key={key} value={key}>{template.name || key}</SelectItem>
                  ))}
                </optgroup>
                <optgroup label="Utilisateur">
                  {Object.entries(userCanvasTemplates).map(([key, template]) => (
                    <SelectItem key={key} value={key}>{template.name || key}</SelectItem>
                  ))}
                </optgroup>
              </SelectContent>
            </Select>
            <Dialog>
              <DialogTrigger asChild>
                <Button variant="outline" size="icon" disabled={isLoading || !messages.length || !isCanvasContent(messages[messages.length - 1].content)}>
                  <Plus className="h-4 w-4" />
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Enregistrer le canevas comme modèle</DialogTitle>
                  <DialogDescription>Donnez un nom à votre modèle.</DialogDescription>
                </DialogHeader>
                <Input value={newTemplateName} onChange={(e) => setNewTemplateName(e.target.value)} placeholder="Nom du modèle" />
                <DialogFooter>
                  <Button onClick={handleSaveTemplate} disabled={isSavingTemplate}>{isSavingTemplate ? 'Enregistrement...' : 'Enregistrer'}</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
            <Badge variant="secondary"><Bot className="h-3 w-3 mr-1" />NeuralStark IA</Badge>
          </div>
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
                  <p className="text-muted-foreground max-w-sm">Demandez à NeuralStark IA tout sur vos documents ou demandez des visualisations de données.</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div key={message.id} className={`flex gap-3 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}> 
                    {message.sender === 'ai' && <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center flex-shrink-0"><Bot className="h-4 w-4 text-primary-foreground" /></div>}
                    <div className={`max-w-[80%] p-3 rounded-xl shadow-md ${message.sender === 'user' ? 'bg-primary text-primary-foreground ml-auto rounded-br-none' : 'bg-muted rounded-bl-none'}`}> 
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium">{message.sender === 'user' ? 'Vous' : 'NeuralStark'}</span>
                        <span className="text-xs text-muted-foreground">{message.timestamp.toLocaleTimeString()}</span>
                      </div>
                      <div className="whitespace-pre-wrap text-sm">
                        {isCanvasContent(message.content) ? (
                          (() => {
                            const canvasData = message.content.canvas;
                            switch (canvasData.type) {
                              case 'bar_chart': return <BarChartCanvas canvasData={canvasData} />;
                              case 'pie_chart': return <PieChartCanvas canvasData={canvasData} />;
                              case 'table': return <TableCanvas canvasData={canvasData} />;
                              case 'kpi_dashboard': return <KpiDashboardCanvas canvasData={canvasData} />;
                              case 'combo_chart': return <ComboChartCanvas canvasData={canvasData} />;
                              default: return <div>Unsupported visualization type: {canvasData.type}</div>;
                            }
                          })()
                        ) : (
                          <div className="prose prose-sm max-w-none"><ReactMarkdown>{message.content as string}</ReactMarkdown></div>
                        )}
                      </div>
                    </div>
                    {message.sender === 'user' && <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0"><User className="h-4 w-4 text-secondary-foreground" /></div>}
                  </div>
                )) 
              )}
              {isLoading && <div className="flex gap-3 justify-start"><div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center flex-shrink-0"><Bot className="h-4 w-4 text-muted-foreground" /></div><div className="bg-muted max-w-[70%] p-3 rounded-xl rounded-bl-none shadow-md"><div className="flex items-center gap-2"><span className="text-xs font-medium">NeuralStark réfléchit...</span></div></div></div>}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
          <div className="border-t p-4">
            <AdvancedFilterUI onFilterChange={handleFilterChange} />
            <div className="flex gap-2 mt-4">
              <Input value={inputValue} onChange={(e) => setInputValue(e.target.value)} onKeyPress={handleKeyPress} placeholder="Tapez votre message ici..." className="flex-1" disabled={isLoading} />
              <Button onClick={handleSendMessage} disabled={isLoading || !inputValue.trim()} size="icon"><Send className="h-4 w-4" /></Button>
              <Button onClick={isRecording ? stopRecording : startRecording} disabled={isLoading} size="icon" variant={isRecording ? "destructive" : "outline"}><Mic className={`h-4 w-4 ${isRecording ? 'animate-pulse' : ''}`} /></Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">Appuyez sur Entrée pour envoyer.</p>
          </div>
        </div>
      </div>
    </div>
  );
};