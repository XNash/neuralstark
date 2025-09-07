import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input'; // Add this line
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card'; // Re-add this line
import { apiClient } from '../lib/api';
import { FileText, RefreshCw, Database, Search, AlertCircle, Upload, Trash2, CheckCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

interface FileContentModalProps {
  showContentModal: boolean;
  setShowContentModal: (open: boolean) => void;
  documentContent: string | null;
}

const FileContentModal: React.FC<FileContentModalProps> = ({
  showContentModal,
  setShowContentModal,
  documentContent,
}) => {
  return (
    <Dialog open={showContentModal} onOpenChange={setShowContentModal}>
      <DialogContent className="sm:max-w-[800px] h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Document Content</DialogTitle>
          <DialogDescription>
            Extracted text content of the selected document.
          </DialogDescription>
        </DialogHeader>
        <ScrollArea className="flex-1 p-4 border rounded-md bg-muted/20">
          <p className="whitespace-pre-wrap text-sm">{documentContent}</p>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};

export const Files: React.FC = () => {
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
  const [isDeleting, setIsDeleting] = useState(false); // State for delete loading
  const [isResetting, setIsResetting] = useState(false); // State for reset loading

  const fetchDocuments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.getDocuments();
      setDocuments(response.indexed_documents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch documents');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setUploadError('Please select a file to upload.');
      return;
    }

    setUploading(true);
    setUploadError(null);
    try {
      // Assuming 'internal' as default source_type for now
      await apiClient.uploadDocument(selectedFile, selectedSourceType);
      setSelectedFile(null); // Clear selected file
      fetchDocuments(); // Refresh document list
      setSuccessMessage('Document uploaded successfully!');
      setTimeout(() => setSuccessMessage(null), 3000); // Clear after 3 seconds
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Failed to upload document.');
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
      setError(err instanceof Error ? err.message : 'Failed to retrieve document content.');
    }
  };

  const handleDeleteDocument = async (filePath: string) => {
    if (window.confirm(`Are you sure you want to delete "${filePath}"?`)) {
      setIsDeleting(true); // Set deleting state
      try {
        await apiClient.deleteDocument(filePath);
        fetchDocuments(); // Refresh document list
        setSuccessMessage('Document deleted successfully!');
        setTimeout(() => setSuccessMessage(null), 3000); // Clear after 3 seconds
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete document.');
      } finally {
        setIsDeleting(false); // Reset deleting state
      }
    }
  };

  const handleResetKnowledgeBase = async (resetType: 'hard' | 'soft') => {
    const confirmationMessage = 
      resetType === 'hard'
        ? 'Êtes-vous sûr de vouloir réinitialiser complètement la base de connaissances ? Cela supprimera tous les fichiers et embeddings et est irréversible.'
        : 'Êtes-vous sûr de vouloir réinitialiser la base de connaissances (réinitialisation douce) ? Cela réindexera tous les fichiers existants.';

    if (window.confirm(confirmationMessage)) {
      setIsResetting(true); // Set resetting state
      try {
        const response = await apiClient.resetKnowledgeBase(resetType);
        setSuccessMessage(response.message);
        setTimeout(() => setSuccessMessage(null), 3000); // Clear after 3 seconds
        fetchDocuments(); // Refresh document list
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Échec de la réinitialisation de la base de connaissances.');
      } finally {
        setIsResetting(false); // Reset resetting state
      }
    }
  };

  return (
    <>
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2 mb-4"> {/* Title section */}
        <div className="flex items-center space-x-2">
          <Database className="h-6 w-6" />
          <h2 className="text-3xl font-bold tracking-tight">Fichiers</h2>
        </div>
      </div>
      <Tabs defaultValue="list" className="w-full">
        <div className="flex justify-end">
          <TabsList>
            <TabsTrigger value="list">Lister les Fichiers</TabsTrigger>
            <TabsTrigger value="import">Importer un Fichier</TabsTrigger>
            <TabsTrigger value="advanced">Avancé</TabsTrigger>
          </TabsList>
        </div>
        <TabsContent value="list">
          <div className="flex items-center space-x-2 mt-4">
            <Badge variant="secondary" className="flex items-center gap-1">
              <FileText className="h-3 w-3" />
              {documents.length} indexed
            </Badge>
            <Button
              onClick={fetchDocuments}
              disabled={isLoading}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
            {uploadError && (
              <div className="flex items-center gap-3 p-4 border border-destructive/50 rounded-lg bg-destructive/5 text-destructive mb-4 mt-4">
                <AlertCircle className="h-5 w-5 flex-shrink-0" />
                <div>
                  <p className="font-medium">Upload Error</p>
                  <p className="text-sm">{uploadError}</p>
                </div>
              </div>
            )}
            {successMessage && (
              <Alert variant="default" className="mb-4 mt-4">
                <CheckCircle className="h-5 w-5" />
                <AlertTitle>Success</AlertTitle>
                <AlertDescription>{successMessage}</AlertDescription>
              </Alert>
            )}
            {error && (
              <div className="flex items-center gap-3 p-4 border border-destructive/50 rounded-lg bg-destructive/5 text-destructive mt-4">
                <AlertCircle className="h-5 w-5 flex-shrink-0" />
                <div>
                  <p className="font-medium">Error loading documents</p>
                  <p className="text-sm">{error}</p>
                </div>
              </div>
            )}

            {isLoading && documents.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground mb-4" />
                <p className="text-muted-foreground">Loading documents...</p>
              </div>
            ) : documents.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center border border-dashed rounded-lg p-8 mt-4">
                <Database className="h-16 w-16 text-muted-foreground mb-4" />
                <h3 className="text-xl font-semibold mb-2">Aucun Fichier Indexé pour l'instant</h3>
                <p className="text-muted-foreground max-w-sm mb-4">
                  It looks like your knowledge base is empty. Upload new documents to get started!
                </p>
                <Button onClick={() => { fetchDocuments(); /* Optionally switch to import tab here */ }} variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh List
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
                      Indexed document • Ready for AI search
                    </p>
                  </div>
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewContent(doc)}
                    >
                      <Search className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDeleteDocument(doc)}
                      disabled={isDeleting}
                    >
                      {isDeleting ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
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
                  <span>Total des fichiers indexés : {documents.length}</span>
                </div>
                <Badge variant="secondary">
                  Knowledge Base Active
                </Badge>
              </div>
            )}
          </TabsContent>
          <TabsContent value="import">
            <Card className="mt-4">
              <CardHeader>
                <CardTitle>Télécharger un Nouveau Fichier</CardTitle>
                <CardDescription>Sélectionnez un fichier et son type de source à ajouter à votre base de connaissances.</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col space-y-4">
                <Select onValueChange={(value: 'internal' | 'external') => setSelectedSourceType(value)} defaultValue={selectedSourceType}>
                  <SelectTrigger className="w-[240px]"> 
                    <SelectValue placeholder="Select Source Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="internal">Internal Knowledge Base</SelectItem>
                    <SelectItem value="external">External Knowledge Base</SelectItem>
                  </SelectContent>
                </Select>
                <Input
                  type="file"
                  className="max-w-lg"
                  onChange={(e) => setSelectedFile(e.target.files ? e.target.files[0] : null)}
                  disabled={uploading}
                />
                <Button onClick={handleFileUpload} disabled={uploading || !selectedFile}>
                  {uploading ? 'Téléchargement en cours...' : 'Télécharger le Fichier'}
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
                    <AlertTitle>Success</AlertTitle>
                    <AlertDescription>{successMessage}</AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="advanced">
            <Card className="mt-4">
              <CardHeader>
                <CardTitle>Paramètres Avancés</CardTitle>
                <CardDescription>
                  Utilisez ces paramètres avec prudence. Ils peuvent entraîner une perte de données.
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col space-y-4">
                <div className="p-4 border border-destructive/50 rounded-lg bg-destructive/5 text-destructive">
                  <h4 className="font-semibold mb-2">Réinitialiser la Base de Connaissances</h4>
                  <p className="text-sm mb-4">
                    Cela supprimera tous les fichiers indexés et leurs embeddings. Cette action est irréversible.
                  </p>
                  <div className="flex space-x-4">
                    <Button
                      variant="destructive"
                      onClick={() => handleResetKnowledgeBase('soft')}
                      disabled={isResetting}
                    >
                      {isResetting ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : null}
                      Soft Reset (Réindexer tous les fichiers)
                    </Button>
                    <Button
                      variant="destructive"
                      onClick={() => handleResetKnowledgeBase('hard')}
                      disabled={isResetting}
                    >
                      {isResetting ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : null}
                      Réinitialisation Complète (Supprimer tous les fichiers et embeddings)
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    {showContentModal && (
      <FileContentModal
        showContentModal={showContentModal}
        setShowContentModal={setShowContentModal}
        documentContent={documentContent}
      />
    )}
    </>
  );
};