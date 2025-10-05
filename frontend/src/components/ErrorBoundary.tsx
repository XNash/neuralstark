import React, { Component, ReactNode } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Dashboard Error Boundary caught an error:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
          <Card className="max-w-md mx-auto">
            <CardHeader>
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <CardTitle className="text-red-800">Erreur du Tableau de Bord</CardTitle>
              </div>
              <CardDescription>
                Une erreur s'est produite lors du chargement du tableau de bord.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {this.state.error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  <strong>Détails de l'erreur:</strong>
                  <br />
                  {this.state.error.message}
                </div>
              )}
              <button
                onClick={this.handleRetry}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Réessayer</span>
              </button>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;