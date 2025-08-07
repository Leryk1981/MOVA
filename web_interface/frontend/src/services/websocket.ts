import { EventEmitter } from 'events';

export interface WebSocketEvent {
  type: string;
  data: any;
  timestamp: number;
}

export interface WebSocketConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

export class WebSocketClient extends EventEmitter {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private isConnecting = false;
  private isManualClose = false;

  constructor(config: WebSocketConfig) {
    super();
    this.config = {
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      ...config,
    };
  }

  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;
    this.isManualClose = false;

    try {
      this.ws = new WebSocket(this.config.url);
      this.setupEventHandlers();
    } catch (error) {
      this.isConnecting = false;
      this.emit('error', error);
      this.scheduleReconnect();
    }
  }

  disconnect(): void {
    this.isManualClose = true;
    this.clearTimers();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.emit('disconnected');
  }

  send(event: string, data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const message: WebSocketEvent = {
        type: event,
        data,
        timestamp: Date.now(),
      };
      this.ws.send(JSON.stringify(message));
    } else {
      this.emit('error', new Error('WebSocket is not connected'));
    }
  }

  subscribe(event: string, callback: (data: any) => void): void {
    this.on(event, callback);
  }

  unsubscribe(event: string, callback?: (data: any) => void): void {
    if (callback) {
      this.off(event, callback);
    } else {
      this.removeAllListeners(event);
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.emit('connected');
      this.startHeartbeat();
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketEvent = JSON.parse(event.data);
        this.emit(message.type, message.data);
        this.emit('message', message);
      } catch (error) {
        this.emit('error', new Error('Failed to parse WebSocket message'));
      }
    };

    this.ws.onclose = (event) => {
      this.isConnecting = false;
      this.clearTimers();
      this.emit('disconnected', event);

      if (!this.isManualClose && this.reconnectAttempts < (this.config.maxReconnectAttempts || 10)) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      this.emit('error', error);
    };
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    this.reconnectAttempts++;
    const delay = (this.config.reconnectInterval || 5000) * Math.pow(2, this.reconnectAttempts - 1);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private startHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }

    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send('heartbeat', { timestamp: Date.now() });
      }
    }, this.config.heartbeatInterval || 30000);
  }

  private clearTimers(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  get connectionState(): string {
    if (!this.ws) return 'CLOSED';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'OPEN';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'CLOSED';
      default:
        return 'UNKNOWN';
    }
  }
}

// WebSocket event types
export const WebSocketEvents = {
  // System events
  SYSTEM_STATUS: 'system.status',
  SYSTEM_METRICS: 'system.metrics',
  SYSTEM_HEALTH: 'system.health',
  
  // ML events
  ML_MODEL_UPDATE: 'ml.model.update',
  ML_TRAINING_PROGRESS: 'ml.training.progress',
  ML_PREDICTION_RESULT: 'ml.prediction.result',
  
  // File events
  FILE_OPERATION: 'file.operation',
  FILE_UPLOAD_PROGRESS: 'file.upload.progress',
  FILE_DOWNLOAD_PROGRESS: 'file.download.progress',
  
  // User events
  USER_ACTIVITY: 'user.activity',
  USER_PRESENCE: 'user.presence',
  
  // Notification events
  NOTIFICATION: 'notification',
  ALERT: 'alert',
  
  // Plugin events
  PLUGIN_UPDATE: 'plugin.update',
  PLUGIN_STATUS: 'plugin.status',
  
  // Analytics events
  ANALYTICS_UPDATE: 'analytics.update',
  METRICS_UPDATE: 'metrics.update',
  
  // Heartbeat
  HEARTBEAT: 'heartbeat',
} as const;

// WebSocket singleton instance
let wsClient: WebSocketClient | null = null;

export const getWebSocketClient = (): WebSocketClient => {
  if (!wsClient) {
    const wsUrl = import.meta.env.VITE_WS_URL || `ws://${window.location.host}/ws`;
    wsClient = new WebSocketClient({ url: wsUrl });
  }
  return wsClient;
};

export const connectWebSocket = async (): Promise<void> => {
  const client = getWebSocketClient();
  await client.connect();
};

export const disconnectWebSocket = (): void => {
  if (wsClient) {
    wsClient.disconnect();
  }
}; 