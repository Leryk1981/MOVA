import React, { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Editor as MonacoEditor } from '@monaco-editor/react';
import { 
  FolderIcon, 
  DocumentTextIcon, 
  ArrowDownTrayIcon, 
  PlusIcon,
  TrashIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';
import { apiService } from '@/services/api';
import { FileInfo } from '@/types/api';

interface FileNode {
  name: string;
  path: string;
  isDirectory: boolean;
  children?: FileNode[];
}

const Editor: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [isFileTreeVisible, setIsFileTreeVisible] = useState(true);
  const [newFileName, setNewFileName] = useState('');
  const [showNewFileInput, setShowNewFileInput] = useState(false);
  
  const queryClient = useQueryClient();

  // Отримання списку файлів
  const { data: filesResponse, isLoading: filesLoading } = useQuery({
    queryKey: ['files-list'],
    queryFn: () => apiService.listFiles('mova'),
    refetchInterval: 30000,
  });

  // Отримання вмісту файлу
  const { data: fileContentResponse, isLoading: contentLoading } = useQuery({
    queryKey: ['file-content', selectedFile],
    queryFn: () => selectedFile ? apiService.readFile(selectedFile, 'mova') : null,
    enabled: !!selectedFile,
  });

  // Мутація для збереження файлу
  const saveFileMutation = useMutation({
    mutationFn: ({ filename, content }: { filename: string; content: string }) =>
      apiService.writeFile(filename, content, 'mova'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files-list'] });
      queryClient.invalidateQueries({ queryKey: ['file-content', selectedFile] });
    },
  });

  // Мутація для створення нового файлу
  const createFileMutation = useMutation({
    mutationFn: ({ filename, content }: { filename: string; content: string }) =>
      apiService.writeFile(filename, content, 'mova'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files-list'] });
      setNewFileName('');
      setShowNewFileInput(false);
    },
  });

  // Мутація для видалення файлу
  const deleteFileMutation = useMutation({
    mutationFn: (filename: string) => apiService.deleteFile(filename, 'mova'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files-list'] });
      if (selectedFile) {
        setSelectedFile(null);
        setFileContent('');
      }
    },
  });

  // Структура файлового дерева
  const fileTree = useMemo(() => {
    if (!filesResponse?.files) return [];
    
    const files = filesResponse.files;
    const tree: FileNode[] = [];
    
    files.forEach((file: FileInfo) => {
      const pathParts = file.path.split('/');
      let currentLevel = tree;
      
      pathParts.forEach((part, index) => {
        const existingNode = currentLevel.find(node => node.name === part);
        
        if (existingNode) {
          currentLevel = existingNode.children || [];
        } else {
          const newNode: FileNode = {
            name: part,
            path: pathParts.slice(0, index + 1).join('/'),
            isDirectory: index < pathParts.length - 1,
            children: [],
          };
          currentLevel.push(newNode);
          currentLevel = newNode.children!;
        }
      });
    });
    
    return tree;
  }, [filesResponse]);

  // Обробка вибору файлу
  const handleFileSelect = useCallback((filePath: string) => {
    setSelectedFile(filePath);
  }, []);

  // Обробка збереження файлу
  const handleSaveFile = useCallback(() => {
    if (selectedFile && fileContent) {
      saveFileMutation.mutate({ filename: selectedFile, content: fileContent });
    }
  }, [selectedFile, fileContent, saveFileMutation]);

  // Обробка створення нового файлу
  const handleCreateFile = useCallback(() => {
    if (newFileName && fileContent) {
      const filename = newFileName.endsWith('.json') ? newFileName : `${newFileName}.json`;
      createFileMutation.mutate({ filename, content: fileContent });
    }
  }, [newFileName, fileContent, createFileMutation]);

  // Обробка видалення файлу
  const handleDeleteFile = useCallback((filename: string) => {
    if (confirm(`Ви впевнені, що хочете видалити файл "${filename}"?`)) {
      deleteFileMutation.mutate(filename);
    }
  }, [deleteFileMutation]);

  // Рендер файлового дерева
  const renderFileTree = (nodes: FileNode[], level = 0) => {
    return nodes.map((node) => (
      <div key={node.path} style={{ paddingLeft: `${level * 16}px` }}>
        <div
          className={`flex items-center py-1 px-2 rounded cursor-pointer hover:bg-gray-100 ${
            selectedFile === node.path ? 'bg-blue-100 text-blue-700' : ''
          }`}
          onClick={() => !node.isDirectory && handleFileSelect(node.path)}
        >
          {node.isDirectory ? (
            <FolderIcon className="h-4 w-4 mr-2 text-yellow-500" />
          ) : (
            <DocumentTextIcon className="h-4 w-4 mr-2 text-blue-500" />
          )}
          <span className="text-sm truncate">{node.name}</span>
          {!node.isDirectory && selectedFile === node.path && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteFile(node.name);
              }}
              className="ml-auto p-1 hover:bg-red-100 rounded"
            >
              <TrashIcon className="h-3 w-3 text-red-500" />
            </button>
          )}
        </div>
        {node.children && node.children.length > 0 && (
          <div>{renderFileTree(node.children, level + 1)}</div>
        )}
      </div>
    ));
  };

  // MOVA JSON схема для підсвічування синтаксису
  const monacoOptions = {
    minimap: { enabled: false },
    fontSize: 14,
    lineNumbers: 'on' as const,
    roundedSelection: false,
    scrollBeyondLastLine: false,
    automaticLayout: true,
    theme: 'vs-dark',
    language: 'json',
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-white">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold text-gray-900">Редактор файлів</h1>
          <button
            onClick={() => setIsFileTreeVisible(!isFileTreeVisible)}
            className="p-2 hover:bg-gray-100 rounded"
          >
            {isFileTreeVisible ? (
              <EyeSlashIcon className="h-5 w-5 text-gray-600" />
            ) : (
              <EyeIcon className="h-5 w-5 text-gray-600" />
            )}
          </button>
        </div>
        
        <div className="flex items-center space-x-2">
          {selectedFile && (
            <span className="text-sm text-gray-600">
              {selectedFile}
            </span>
          )}
          <button
            onClick={() => setShowNewFileInput(true)}
            className="btn btn-primary btn-sm"
            disabled={showNewFileInput}
          >
            <PlusIcon className="h-4 w-4 mr-1" />
            Новий файл
          </button>
          {selectedFile && (
            <button
              onClick={handleSaveFile}
              className="btn btn-outline btn-sm"
              disabled={saveFileMutation.isPending}
            >
              <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
              {saveFileMutation.isPending ? 'Збереження...' : 'Зберегти'}
            </button>
          )}
        </div>
      </div>

      {/* New File Input */}
      {showNewFileInput && (
        <div className="p-4 border-b bg-gray-50">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              placeholder="Назва файлу (без розширення)"
              value={newFileName}
              onChange={(e) => setNewFileName(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleCreateFile}
              className="btn btn-primary btn-sm"
              disabled={!newFileName || createFileMutation.isPending}
            >
              {createFileMutation.isPending ? 'Створення...' : 'Створити'}
            </button>
            <button
              onClick={() => {
                setShowNewFileInput(false);
                setNewFileName('');
              }}
              className="btn btn-outline btn-sm"
            >
              Скасувати
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* File Tree Sidebar */}
        {isFileTreeVisible && (
          <div className="w-64 border-r bg-gray-50 overflow-y-auto">
            <div className="p-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Файли MOVA</h3>
              {filesLoading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                </div>
              ) : fileTree.length === 0 ? (
                <div className="text-center py-4 text-gray-500">
                  <p>Немає файлів</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {renderFileTree(fileTree)}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Editor */}
        <div className="flex-1 flex flex-col">
          {!selectedFile ? (
            <div className="flex-1 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Виберіть файл для редагування
                </h3>
                <p className="text-gray-500">
                  Виберіть файл з дерева зліва або створіть новий файл
                </p>
              </div>
            </div>
          ) : (
            <div className="flex-1">
              {contentLoading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : (
                <MonacoEditor
                  height="100%"
                  language="json"
                  theme="vs-dark"
                  value={fileContentResponse?.data?.content || fileContent}
                  onChange={(value) => setFileContent(value || '')}
                  options={monacoOptions}
                />
              )}
            </div>
          )}
        </div>
      </div>

      {/* Status Bar */}
      <div className="h-8 bg-gray-100 border-t flex items-center px-4 text-xs text-gray-600">
        <div className="flex items-center space-x-4">
          <span>
            {selectedFile ? `Файл: ${selectedFile}` : 'Файл не вибрано'}
          </span>
          {selectedFile && (
            <span>
              Розмір: {fileContentResponse?.data?.size || fileContent.length} символів
            </span>
          )}
        </div>
        <div className="ml-auto">
          <span>MOVA 2.2 Editor</span>
        </div>
      </div>
    </div>
  );
};

export default Editor; 