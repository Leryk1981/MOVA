import { useEffect, useState, useCallback, useRef } from 'react';
import { WebSocketClient, WebSocketEvents, getWebSocketClient } from '../services/websocket';

export interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnectOnError?: boolean;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
}

export interface UseWebSocketReturn {
  client: WebSocketClient;
  isConnected: boolean;
  connectionState: string;
  connect: () => Promise<void>;
  disconnect: () => void;
  send: (event: string, data: any) => void;
  subscribe: (event: string, callback: (data: any) => void) => void;
  unsubscribe: (event: string, callback?: (data: any) => void) => void;
}

export const useWebSocket = (options: UseWebSocketOptions = {}): UseWebSocketReturn => {
  const {
    autoConnect = true,
    reconnectOnError = true,
    onConnect,
    onDisconnect,
    onError,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('CLOSED');
  const clientRef = useRef<WebSocketClient | null>(null);

  const client = clientRef.current || getWebSocketClient();
  if (!clientRef.current) {
    clientRef.current = client;
  }

  const connect = useCallback(async () => {
    try {
      await client.connect();
    } catch (error) {
      if (onError) {
        onError(error as Error);
      }
    }
  }, [client, onError]);

  const disconnect = useCallback(() => {
    client.disconnect();
  }, [client]);

  const send = useCallback((event: string, data: any) => {
    client.send(event, data);
  }, [client]);

  const subscribe = useCallback((event: string, callback: (data: any) => void) => {
    client.subscribe(event, callback);
  }, [client]);

  const unsubscribe = useCallback((event: string, callback?: (data: any) => void) => {
    client.unsubscribe(event, callback);
  }, [client]);

  useEffect(() => {
    const handleConnect = () => {
      setIsConnected(true);
      setConnectionState('OPEN');
      if (onConnect) {
        onConnect();
      }
    };

    const handleDisconnect = () => {
      setIsConnected(false);
      setConnectionState('CLOSED');
      if (onDisconnect) {
        onDisconnect();
      }
    };

    const handleError = (error: Error) => {
      if (onError) {
        onError(error);
      }
    };

    const handleStateChange = () => {
      setConnectionState(client.connectionState);
      setIsConnected(client.isConnected);
    };

    // Subscribe to client events
    client.subscribe('connected', handleConnect);
    client.subscribe('disconnected', handleDisconnect);
    client.subscribe('error', handleError);

    // Initial state
    handleStateChange();

    // Auto-connect if enabled
    if (autoConnect && !client.isConnected) {
      connect();
    }

    return () => {
      client.unsubscribe('connected', handleConnect);
      client.unsubscribe('disconnected', handleDisconnect);
      client.unsubscribe('error', handleError);
    };
  }, [client, autoConnect, connect, onConnect, onDisconnect, onError]);

  return {
    client,
    isConnected,
    connectionState,
    connect,
    disconnect,
    send,
    subscribe,
    unsubscribe,
  };
};

// Specialized hooks for specific WebSocket events
export const useSystemStatus = () => {
  const [status, setStatus] = useState<any>(null);
  const { subscribe, unsubscribe } = useWebSocket();

  useEffect(() => {
    const handleStatusUpdate = (data: any) => {
      setStatus(data);
    };

    subscribe(WebSocketEvents.SYSTEM_STATUS, handleStatusUpdate);

    return () => {
      unsubscribe(WebSocketEvents.SYSTEM_STATUS, handleStatusUpdate);
    };
  }, [subscribe, unsubscribe]);

  return status;
};

export const useSystemMetrics = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const { subscribe, unsubscribe } = useWebSocket();

  useEffect(() => {
    const handleMetricsUpdate = (data: any) => {
      setMetrics(data);
    };

    subscribe(WebSocketEvents.SYSTEM_METRICS, handleMetricsUpdate);

    return () => {
      unsubscribe(WebSocketEvents.SYSTEM_METRICS, handleMetricsUpdate);
    };
  }, [subscribe, unsubscribe]);

  return metrics;
};

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<any[]>([]);
  const { subscribe, unsubscribe } = useWebSocket();

  useEffect(() => {
    const handleNotification = (data: any) => {
      setNotifications(prev => [...prev, { ...data, id: Date.now(), timestamp: new Date() }]);
    };

    subscribe(WebSocketEvents.NOTIFICATION, handleNotification);

    return () => {
      unsubscribe(WebSocketEvents.NOTIFICATION, handleNotification);
    };
  }, [subscribe, unsubscribe]);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const removeNotification = useCallback((id: number) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  return { notifications, clearNotifications, removeNotification };
};

export const useMLUpdates = () => {
  const [mlUpdates, setMLUpdates] = useState<any[]>([]);
  const { subscribe, unsubscribe } = useWebSocket();

  useEffect(() => {
    const handleModelUpdate = (data: any) => {
      setMLUpdates(prev => [...prev, { ...data, id: Date.now(), timestamp: new Date() }]);
    };

    const handleTrainingProgress = (data: any) => {
      setMLUpdates(prev => [...prev, { ...data, id: Date.now(), timestamp: new Date() }]);
    };

    subscribe(WebSocketEvents.ML_MODEL_UPDATE, handleModelUpdate);
    subscribe(WebSocketEvents.ML_TRAINING_PROGRESS, handleTrainingProgress);

    return () => {
      unsubscribe(WebSocketEvents.ML_MODEL_UPDATE, handleModelUpdate);
      unsubscribe(WebSocketEvents.ML_TRAINING_PROGRESS, handleTrainingProgress);
    };
  }, [subscribe, unsubscribe]);

  const clearUpdates = useCallback(() => {
    setMLUpdates([]);
  }, []);

  return { mlUpdates, clearUpdates };
};

export const useFileOperations = () => {
  const [fileOperations, setFileOperations] = useState<any[]>([]);
  const { subscribe, unsubscribe } = useWebSocket();

  useEffect(() => {
    const handleFileOperation = (data: any) => {
      setFileOperations(prev => [...prev, { ...data, id: Date.now(), timestamp: new Date() }]);
    };

    const handleUploadProgress = (data: any) => {
      setFileOperations(prev => [...prev, { ...data, id: Date.now(), timestamp: new Date() }]);
    };

    subscribe(WebSocketEvents.FILE_OPERATION, handleFileOperation);
    subscribe(WebSocketEvents.FILE_UPLOAD_PROGRESS, handleUploadProgress);

    return () => {
      unsubscribe(WebSocketEvents.FILE_OPERATION, handleFileOperation);
      unsubscribe(WebSocketEvents.FILE_UPLOAD_PROGRESS, handleUploadProgress);
    };
  }, [subscribe, unsubscribe]);

  const clearOperations = useCallback(() => {
    setFileOperations([]);
  }, []);

  return { fileOperations, clearOperations };
}; 