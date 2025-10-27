/**
 * Главный компонент приложения
 */
import { useState, useEffect } from 'react';
import { FileUpload } from './components/FileUpload';
import { ChatInterface } from './components/ChatInterface';
import { apiClient, FileMetadata, AgentResponse } from './api/client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  data?: AgentResponse;
  timestamp: Date;
}

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [fileMetadata, setFileMetadata] = useState<FileMetadata | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isHealthy, setIsHealthy] = useState(true);

  // Инициализация сессии
  useEffect(() => {
    const initSession = async () => {
      try {
        const session = await apiClient.createSession();
        setSessionId(session.session_id);
      } catch (error) {
        console.error('Failed to create session:', error);
      }
    };

    initSession();
  }, []);

  // Health check
  useEffect(() => {
    const checkHealth = async () => {
      const healthy = await apiClient.healthCheck();
      setIsHealthy(healthy);
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Проверяем каждые 30 секунд

    return () => clearInterval(interval);
  }, []);

  const handleFileSelect = async (file: File) => {
    if (!sessionId) return;

    setIsUploading(true);

    try {
      const result = await apiClient.uploadFile(sessionId, file);
      setFileMetadata(result.metadata);

      // Добавляем сообщение о загрузке
      addMessage('assistant', `✅ Файл "${file.name}" загружен успешно!\n\n` +
        `📊 Строк: ${result.metadata.rows}\n` +
        `📋 Столбцов: ${result.metadata.columns}\n` +
        `💾 Размер: ${(result.metadata.file_size / 1024).toFixed(2)} KB`
      );
    } catch (error) {
      console.error('Upload error:', error);
      addMessage('assistant', `❌ Ошибка при загрузке файла: ${(error as Error).message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async (messageText: string) => {
    if (!sessionId) return;

    // Добавляем сообщение пользователя
    addMessage('user', messageText);

    setIsLoading(true);

    try {
      const response = await apiClient.sendMessage(sessionId, messageText);

      // Добавляем ответ ассистента
      addMessage('assistant', response.message, response);
    } catch (error) {
      console.error('Message error:', error);
      addMessage('assistant', `❌ Ошибка: ${(error as Error).message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const addMessage = (role: 'user' | 'assistant', content: string, data?: AgentResponse) => {
    const message: Message = {
      id: Date.now().toString() + Math.random(),
      role,
      content,
      data,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, message]);
  };

  const handleReset = async () => {
    if (sessionId) {
      try {
        await apiClient.deleteSession(sessionId);
      } catch (error) {
        console.error('Failed to delete session:', error);
      }
    }

    // Создаём новую сессию
    const session = await apiClient.createSession();
    setSessionId(session.session_id);
    setFileMetadata(null);
    setMessages([]);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-3xl">📊</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Excel AI Processor
                </h1>
                <p className="text-sm text-gray-500">
                  Powered by PydanticAI
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Health indicator */}
              <div className="flex items-center space-x-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    isHealthy ? 'bg-green-500' : 'bg-red-500'
                  }`}
                />
                <span className="text-sm text-gray-600">
                  {isHealthy ? 'Online' : 'Offline'}
                </span>
              </div>

              {/* Reset button */}
              <button
                onClick={handleReset}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                🔄 Новая сессия
              </button>
            </div>
          </div>

          {/* File info */}
          {fileMetadata && (
            <div className="mt-4 flex items-center space-x-2 text-sm text-gray-600 bg-blue-50 px-4 py-2 rounded-lg">
              <span className="font-medium">📄 {fileMetadata.original_filename}</span>
              <span>•</span>
              <span>{fileMetadata.rows} строк</span>
              <span>•</span>
              <span>{fileMetadata.columns} столбцов</span>
            </div>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 overflow-hidden">
        <div className="max-w-7xl mx-auto h-full px-4 py-6">
          {!fileMetadata ? (
            /* Upload view */
            <div className="h-full flex items-center justify-center">
              <div className="w-full max-w-2xl">
                <FileUpload
                  onFileSelect={handleFileSelect}
                  isUploading={isUploading}
                />
              </div>
            </div>
          ) : (
            /* Chat view */
            <div className="h-full bg-white rounded-lg shadow-sm border">
              <ChatInterface
                messages={messages}
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
              />
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t py-3">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-500">
          <p>
            🤖 AI-powered data processing with local LLM • Built with FastAPI + PydanticAI + React
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
