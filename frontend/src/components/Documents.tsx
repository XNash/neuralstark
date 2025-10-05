import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input'; // Add this line
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card'; // Re-add this line
import { Alert, AlertTitle, AlertDescription } from './ui/alert';
import { apiClient } from '../lib/api';
import { FileText, RefreshCw, Database, Search, AlertCircle, Upload, Trash2, CheckCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

interface DocumentContentModalProps {
  showContentModal: boolean;
  setShowContentModal: (open: boolean) => void;
  documentContent: string | null;
}

const DocumentContentModal: React.FC<DocumentContentModalProps> = ({
  showContentModal,
  setShowContentModal,
  documentContent,
}) => {
  return (
    <Dialog open={showContentModal} onOpenChange={setShowContentModal}>
      <DialogContent className="sm:max-w-[800px] h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Contenu du Document</DialogTitle>
          <DialogDescription>
            Contenu textuel extrait du document sélectionné.
          </DialogDescription>
        </DialogHeader>
        <ScrollArea className="flex-1 p-4 border rounded-md bg-muted/20">
          <p className="whitespace-pre-wrap text-sm">{documentContent}</p>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};

export const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [selectedSourceType, setSelectedSourceType] = useState<'internal' | 'external'>('internal'); // Default to internal
  const [documentContent, setDocumentContent] = useState<string | null>(null);
  const [showContentModal, setShowContentModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchDocuments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.getDocuments();
      setDocuments(response.indexed_documents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Échec du chargement des documents');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setUploadError('Veuillez sélectionner un fichier à télécharger.');
      return;
    }

    setUploading(true);
    setUploadError(null);
    try {
      // Assuming 'internal' as default source_type for now
      await apiClient.uploadDocument(selectedFile, selectedSourceType);
      setSelectedFile(null); // Clear selected file
      fetchDocuments(); // Refresh document list
      setSuccessMessage('Document téléchargé avec succès !');
      setTimeout(() => setSuccessMessage(null), 3000); // Clear after 3 seconds
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Échec du téléchargement du document.');
    } finally {
      setUploading(false);
    }
  };

  const handleViewContent = async (filePath: string) => {
    try {
      const response = await apiClient.getDocumentContent(filePath);
      setDocumentContent(response.content);
      setShowContentModal(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Échec de la récupération du contenu du document.');
    }
  };

  const handleDeleteDocument = async (filePath: string) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer "${filePath}"?`)) {
      try {
        await apiClient.deleteDocument(filePath);
        fetchDocuments(); // Refresh document list
        setSuccessMessage('Document supprimé avec succès !');
        setTimeout(() => setSuccessMessage(null), 3000); // Clear after 3 seconds
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Échec de la suppression du document.');
      }
    }
  };

  return (
    <>
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2 mb-4"> {/* Title section */}
        <div className="flex items-center space-x-2">
          <Database className="h-6 w-6" />
          <h2 className="text-3xl font-bold tracking-tight">Documents</h2>
        </div>
      </div>
      <Tabs defaultValue="list" className="w-full">
        <TabsList>
          <TabsTrigger value="list">Lister les Documents</TabsTrigger>
          <TabsTrigger value="import">Importer un Document</TabsTrigger>
        </TabsList>
        <TabsContent value="list">
          <div className="flex items-center space-x-2 mt-4">
            <Badge variant="secondary" className="flex items-center gap-1">
              <FileText className="h-3 w-3" />
              {documents.length} indexés
            </Badge>
            <Button
              onClick={fetchDocuments}
              disabled={isLoading}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Actualiser
            </Button>
          </div>
            {uploadError && (
              <div className="flex items-center gap-3 p-4 border border-destructive/50 rounded-lg bg-destructive/5 text-destructive mb-4 mt-4">
                <AlertCircle className="h-5 w-5 flex-shrink-0" />
                <div>
                  <p className="font-medium">Erreur de Téléchargement</p>
                  <p className="text-sm">{uploadError}</p>
                </div>
              </div>
            )}
            {successMessage && (
              <Alert variant="default" className="mb-4 mt-4">
                <CheckCircle className="h-5 w-5" />
                <AlertTitle>Succès</AlertTitle>
                <AlertDescription>{successMessage}</AlertDescription>
              </Alert>
            )}
            {error && (
              <div className="flex items-center gap-3 p-4 border border-destructive/50 rounded-lg bg-destructive/5 text-destructive mt-4">
                <AlertCircle className="h-5 w-5 flex-shrink-0" />
                <div>
                  <p className="font-medium">Erreur lors du chargement des documents</p>
                  <p className="text-sm">{error}</p>
                </div>
              </div>
            )}

            {isLoading && documents.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground mb-4" />
                <p className="text-muted-foreground">Chargement des documents...</p>
              </div>
            ) : documents.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center border border-dashed rounded-lg p-8 mt-4">
                <Database className="h-16 w-16 text-muted-foreground mb-4" />
                <h3 className="text-xl font-semibold mb-2">Aucun Document Indexé pour l'instant</h3>
                <p className="text-muted-foreground max-w-sm mb-4">
                  Il semble que votre base de connaissances soit vide. Téléchargez de nouveaux documents pour commencer !
                </p>
                <Button onClick={() => { fetchDocuments(); /* Optionally switch to import tab here */ }} variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Actualiser la Liste
                </Button>
              </div>
            ) : (
              <ScrollArea className="flex-1 mt-4">
            <div className="space-y-3">
              {documents.map((doc, index) => (
                <div
                  key={index}
                  className="flex items-center gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                      <FileText className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{doc}</p>
                    <p className="text-xs text-muted-foreground">
                      Document indexé • Prêt pour la recherche IA
                    </p>
                  </div>
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewContent(doc)}
                    >
                      <Search className="h-4 w-4 mr-1" />
                      Voir
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDeleteDocument(doc)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
            )}

            {documents.length > 0 && (
              <div className="flex items-center justify-between mt-6 pt-4 border-t">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Database className="h-4 w-4" />
                  <span>Total des documents indexés : {documents.length}</span>
                </div>
                <Badge variant="secondary">
                  Base de Connaissances Active
                </Badge>
              </div>
            )}
          </TabsContent>
          <TabsContent value="import">
            <Card className="mt-4">
              <CardHeader>
                <CardTitle>Télécharger un Nouveau Document</CardTitle>
                <CardDescription>Sélectionnez un document et son type de source à ajouter à votre base de connaissances.</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col space-y-4">
                <Select onValueChange={(value: 'internal' | 'external') => setSelectedSourceType(value)} defaultValue={selectedSourceType}>
                  <SelectTrigger className="w-[240px]"> 
                    <SelectValue placeholder="Sélectionner le Type de Source" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="internal">Base de Connaissances Interne</SelectItem>
                    <SelectItem value="external">Base de Connaissances Externe</SelectItem>
                  </SelectContent>
                </Select>
                <Input
                  type="file"
                  className="max-w-lg"
                  onChange={(e) => setSelectedFile(e.target.files ? e.target.files[0] : null)}
                  disabled={uploading}
                />
                <Button onClick={handleFileUpload} disabled={uploading || !selectedFile}>
                  {uploading ? 'Téléchargement en cours...' : 'Télécharger le Document'}
                </Button>
                {uploadError && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Upload Error</AlertTitle>
                    <AlertDescription>{uploadError}</AlertDescription>
                  </Alert>
                )}
                {successMessage && (
                  <Alert variant="default">
                    <CheckCircle className="h-4 w-4" />
                    <AlertTitle>Succès</AlertTitle>
                    <AlertDescription>{successMessage}</AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    {showContentModal && (
      <DocumentContentModal
        showContentModal={showContentModal}
        setShowContentModal={setShowContentModal}
        documentContent={documentContent}
      />
    )}
    </>
  );
};