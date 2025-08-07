import React, { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  FolderIcon, 
  DocumentTextIcon, 
  ArrowUpTrayIcon, 
  ArrowDownTrayIcon,
  TrashIcon,
  EyeIcon,
  PencilIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { apiService } from '@/services/api';
import { FileInfo } from '@/types/api';

const Files: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [currentDirectory, setCurrentDirectory] = useState('mova');
  const [searchTerm, setSearchTerm] = useState('');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showNewFolderModal, setShowNewFolderModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const queryClient = useQueryClient();

  // Отримання списку файлів
  const { data: filesResponse, isLoading: filesLoading } = useQuery({
    queryKey: ['files-list', currentDirectory],
    queryFn: () => apiService.listFiles(currentDirectory),
    refetchInterval: 30000,
  });

  // Отримання вмісту файлу
  const { data: fileContentResponse, isLoading: contentLoading } = useQuery({
    queryKey: ['file-content', selectedFile?.name],
    queryFn: () => selectedFile ? apiService.readFile(selectedFile.name, currentDirectory) : null,
    enabled: !!selectedFile,
  });

  // Мутація для завантаження файлу
  const uploadFileMutation = useMutation({
    mutationFn: (file: File) => apiService.uploadFile(file, currentDirectory),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files-list', currentDirectory] });
      setShowUploadModal(false);
      setUploadProgress(0);
    },
  });

  // Мутація для видалення файлу
  const deleteFileMutation = useMutation({
    mutationFn: (filename: string) => apiService.deleteFile(filename, currentDirectory),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files-list', currentDirectory] });
      if (selectedFile) {
        setSelectedFile(null);
      }
      setSelectedFiles([]);
    },
  });

  // Мутація для запису файлу
  const writeFileMutation = useMutation({
    mutationFn: ({ filename, content }: { filename: string; content: string }) =>
      apiService.writeFile(filename, content, currentDirectory),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files-list', currentDirectory] });
      queryClient.invalidateQueries({ queryKey: ['file-content', selectedFile?.name] });
    },
  });

  const files = filesResponse?.files || [];

  // Фільтрація файлів за пошуковим запитом
  const filteredFiles = files.filter((file) =>
    file.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Обробка завантаження файлу
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      uploadFileMutation.mutate(file);
      
      // Симуляція прогресу завантаження
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(interval);
            return 90;
          }
          return prev + 10;
        });
      }, 100);
    }
  };

  // Обробка вибору файлу
  const handleFileSelect = (file: FileInfo) => {
    setSelectedFile(file);
  };

  // Обробка видалення файлу
  const handleDeleteFile = (filename: string) => {
    if (confirm(`Ви впевнені, що хочете видалити файл "${filename}"?`)) {
      deleteFileMutation.mutate(filename);
    }
  };

  // Обробка масового видалення
  const handleBulkDelete = () => {
    if (selectedFiles.length === 0) return;
    
    if (confirm(`Ви впевнені, що хочете видалити ${selectedFiles.length} файлів?`)) {
      selectedFiles.forEach(filename => deleteFileMutation.mutate(filename));
    }
  };

  // Обробка вибору файлів для масових операцій
  const handleFileCheckbox = (filename: string, checked: boolean) => {
    if (checked) {
      setSelectedFiles(prev => [...prev, filename]);
    } else {
      setSelectedFiles(prev => prev.filter(f => f !== filename));
    }
  };

  // Обробка вибору всіх файлів
  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedFiles(filteredFiles.map(f => f.name));
    } else {
      setSelectedFiles([]);
    }
  };

  // Форматування розміру файлу
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Форматування дати
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Управління файлами</h1>
          <p className="mt-1 text-sm text-gray-500">
            Завантаження, перегляд та управління файлами MOVA
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowNewFolderModal(true)}
            className="btn btn-outline"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Нова папка
          </button>
          <button
            onClick={() => setShowUploadModal(true)}
            className="btn btn-primary"
          >
            <ArrowUpTrayIcon className="h-4 w-4 mr-2" />
            Завантажити файл
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center space-x-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Пошук файлів..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">
            {filteredFiles.length} файлів
          </span>
          {selectedFiles.length > 0 && (
            <button
              onClick={handleBulkDelete}
              className="btn btn-outline btn-sm text-red-600 hover:bg-red-50"
            >
              <TrashIcon className="h-4 w-4 mr-1" />
              Видалити ({selectedFiles.length})
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* File List */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900">
                  Файли в {currentDirectory}
                </h2>
                <div className="flex items-center space-x-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedFiles.length === filteredFiles.length && filteredFiles.length > 0}
                      onChange={(e) => handleSelectAll(e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-600">Всі</span>
                  </label>
                </div>
              </div>
            </div>
            
            {filesLoading ? (
              <div className="p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              </div>
            ) : filteredFiles.length === 0 ? (
              <div className="p-8 text-center">
                <FolderIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">
                  {searchTerm ? 'Файли не знайдено' : 'Немає файлів у цій папці'}
                </p>
              </div>
            ) : (
              <div className="divide-y">
                {filteredFiles.map((file: FileInfo) => (
                  <div
                    key={file.name}
                    className={`p-4 hover:bg-gray-50 cursor-pointer ${
                      selectedFile?.name === file.name ? 'bg-blue-50' : ''
                    }`}
                    onClick={() => handleFileSelect(file)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={selectedFiles.includes(file.name)}
                          onChange={(e) => handleFileCheckbox(file.name, e.target.checked)}
                          onClick={(e) => e.stopPropagation()}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        {file.type === 'directory' ? (
                          <FolderIcon className="h-5 w-5 text-yellow-500" />
                        ) : (
                          <DocumentTextIcon className="h-5 w-5 text-blue-500" />
                        )}
                        <div>
                          <h3 className="text-sm font-medium text-gray-900">{file.name}</h3>
                          <p className="text-xs text-gray-500">
                            {formatFileSize(file.size)} • {formatDate(file.modified)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteFile(file.name);
                          }}
                          className="p-1 hover:bg-red-100 rounded"
                        >
                          <TrashIcon className="h-4 w-4 text-red-500" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* File Details */}
        <div className="lg:col-span-1">
          <div className="card">
            <div className="p-4 border-b">
              <h2 className="text-lg font-medium text-gray-900">Деталі файлу</h2>
            </div>
            
            {selectedFile ? (
              <div className="p-4">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">{selectedFile.name}</h3>
                    <p className="text-sm text-gray-500">
                      Розмір: {formatFileSize(selectedFile.size)}
                    </p>
                    <p className="text-sm text-gray-500">
                      Змінено: {formatDate(selectedFile.modified)}
                    </p>
                  </div>
                  
                  {selectedFile.type !== 'directory' && (
                    <div className="space-y-2">
                      <button
                        onClick={() => {
                          // Логіка для перегляду файлу
                        }}
                        className="w-full btn btn-outline btn-sm"
                      >
                        <EyeIcon className="h-4 w-4 mr-2" />
                        Переглянути
                      </button>
                      <button
                        onClick={() => {
                          // Логіка для редагування файлу
                        }}
                        className="w-full btn btn-outline btn-sm"
                      >
                        <PencilIcon className="h-4 w-4 mr-2" />
                        Редагувати
                      </button>
                      <button
                        onClick={() => {
                          // Логіка для завантаження файлу
                        }}
                        className="w-full btn btn-outline btn-sm"
                      >
                        <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                        Завантажити
                      </button>
                    </div>
                  )}
                  
                  {contentLoading ? (
                    <div className="text-center py-4">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                    </div>
                  ) : fileContentResponse?.data?.content ? (
                    <div className="mt-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Попередній перегляд:</h4>
                      <div className="bg-gray-50 p-3 rounded text-xs font-mono overflow-auto max-h-32">
                        {fileContentResponse.data.content.substring(0, 200)}
                        {fileContentResponse.data.content.length > 200 && '...'}
                      </div>
                    </div>
                  ) : null}
                </div>
              </div>
            ) : (
              <div className="p-8 text-center">
                <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Виберіть файл для перегляду деталей</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Завантажити файл</h3>
            
            <div className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileUpload}
                  className="hidden"
                  accept=".json,.yaml,.yml,.txt"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="btn btn-outline"
                >
                  <ArrowUpTrayIcon className="h-4 w-4 mr-2" />
                  Виберіть файл
                </button>
                <p className="text-sm text-gray-500 mt-2">
                  Підтримуються: JSON, YAML, TXT
                </p>
              </div>
              
              {uploadProgress > 0 && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              )}
              
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="btn btn-outline"
                >
                  Скасувати
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* New Folder Modal */}
      {showNewFolderModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Створити нову папку</h3>
            
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Назва папки"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => {
                    setShowNewFolderModal(false);
                    setNewFolderName('');
                  }}
                  className="btn btn-outline"
                >
                  Скасувати
                </button>
                <button
                  onClick={() => {
                    // Логіка створення папки
                    setShowNewFolderModal(false);
                    setNewFolderName('');
                  }}
                  className="btn btn-primary"
                  disabled={!newFolderName.trim()}
                >
                  Створити
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Files; 