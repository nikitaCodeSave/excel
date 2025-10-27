/**
 * Компонент чат-интерфейса
 */
import { useState, useRef, useEffect } from 'react';
import { AgentResponse } from '../api/client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  data?: AgentResponse;
  timestamp: Date;
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export function ChatInterface({ messages, onSendMessage, isLoading }: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg font-medium">Добро пожаловать! 👋</p>
            <p className="mt-2">Загрузите файл и задайте вопрос</p>
            <div className="mt-6 text-left max-w-md mx-auto space-y-2">
              <p className="text-sm font-semibold">Примеры запросов:</p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• "Сколько строк в файле?"</li>
                <li>• "Добавь столбец Общая_Сумма = количество * цена"</li>
                <li>• "Построй график продаж по месяцам"</li>
                <li>• "Экспортируй в Excel"</li>
              </ul>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}

        {isLoading && (
          <div className="flex items-center space-x-2 text-gray-500">
            <div className="animate-bounce">●</div>
            <div className="animate-bounce animation-delay-200">●</div>
            <div className="animate-bounce animation-delay-400">●</div>
            <span className="ml-2">Обрабатываю...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input form */}
      <div className="border-t bg-white p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Введите сообщение..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={1}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className={`
              px-6 py-2 rounded-lg font-medium transition-colors
              ${
                isLoading || !input.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }
            `}
          >
            Отправить
          </button>
        </form>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`
          max-w-[70%] rounded-lg px-4 py-2
          ${
            isUser
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-800'
          }
        `}
      >
        <div className="whitespace-pre-wrap break-words">{message.content}</div>

        {/* Render data if present */}
        {message.data && !isUser && (
          <div className="mt-2">
            {message.data.preview && message.data.preview.length > 0 && (
              <DataPreview data={message.data.preview} />
            )}

            {message.data.visualization_ids && message.data.visualization_ids.length > 0 && (
              <div className="mt-2">
                {message.data.visualization_ids.map((vizId) => (
                  <img
                    key={vizId}
                    src={`http://localhost:8000/api/visualizations/${message.data?.data?.session_id || 'unknown'}/${vizId}`}
                    alt="Visualization"
                    className="rounded-lg mt-2"
                  />
                ))}
              </div>
            )}

            {message.data.file_id && message.data.data?.export && (
              <a
                href={`http://localhost:8000${message.data.data.export.download_url}`}
                download
                className="inline-block mt-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
              >
                📥 Скачать файл
              </a>
            )}
          </div>
        )}

        <div className={`text-xs mt-1 ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
          {message.timestamp.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
}

function DataPreview({ data }: { data: Array<Record<string, any>> }) {
  if (data.length === 0) return null;

  const columns = Object.keys(data[0]);

  return (
    <div className="mt-2 overflow-x-auto">
      <table className="min-w-full text-xs border border-gray-300">
        <thead>
          <tr className="bg-gray-50">
            {columns.map((col) => (
              <th key={col} className="px-2 py-1 border-b text-left font-semibold">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              {columns.map((col) => (
                <td key={col} className="px-2 py-1 border-b">
                  {row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
