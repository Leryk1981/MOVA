import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';

interface ActivityItem {
  id: number;
  type: string;
  title: string;
  description: string;
  timestamp: Date;
  user?: string;
  status: 'success' | 'error' | 'warning' | 'info';
}

interface LiveActivityFeedProps {
  maxItems?: number;
  autoScroll?: boolean;
  showUserInfo?: boolean;
  className?: string;
}

export const LiveActivityFeed: React.FC<LiveActivityFeedProps> = ({
  maxItems = 50,
  autoScroll = true,
  showUserInfo = true,
  className = '',
}) => {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const { subscribe, unsubscribe } = useWebSocket();

  useEffect(() => {
    const handleActivity = (data: any) => {
      const newActivity: ActivityItem = {
        id: Date.now(),
        type: data.type || 'info',
        title: data.title || 'Активність',
        description: data.description || '',
        timestamp: new Date(),
        user: data.user,
        status: data.status || 'info',
      };

      setActivities(prev => {
        const updated = [newActivity, ...prev].slice(0, maxItems);
        return updated;
      });
    };

    // Subscribe to various activity events
    subscribe('user.activity', handleActivity);
    subscribe('file.operation', handleActivity);
    subscribe('ml.model.update', handleActivity);
    subscribe('system.status', handleActivity);

    return () => {
      unsubscribe('user.activity', handleActivity);
      unsubscribe('file.operation', handleActivity);
      unsubscribe('ml.model.update', handleActivity);
      unsubscribe('system.status', handleActivity);
    };
  }, [subscribe, unsubscribe, maxItems]);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'file':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
          </svg>
        );
      case 'ml':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
          </svg>
        );
      case 'user':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
          </svg>
        );
      case 'system':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-600 bg-green-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'info':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTime = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);

    if (minutes > 0) {
      return `${minutes}хв тому`;
    } else if (seconds > 0) {
      return `${seconds}с тому`;
    } else {
      return 'щойно';
    }
  };

  const clearActivities = () => {
    setActivities([]);
  };

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">Активність в реальному часі</h3>
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-xs text-gray-500">Live</span>
            </div>
            <button
              onClick={clearActivities}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Очистити
            </button>
          </div>
        </div>
      </div>

      <div className="max-h-96 overflow-y-auto">
        {activities.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p className="mt-2">Немає активності</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {activities.map((activity) => (
              <div key={activity.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start space-x-3">
                  <div className={`flex-shrink-0 p-1 rounded-full ${getStatusColor(activity.status)}`}>
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">
                        {activity.title}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatTime(activity.timestamp)}
                      </p>
                    </div>
                    {activity.description && (
                      <p className="mt-1 text-sm text-gray-600">
                        {activity.description}
                      </p>
                    )}
                    {showUserInfo && activity.user && (
                      <p className="mt-1 text-xs text-gray-500">
                        Користувач: {activity.user}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveActivityFeed; 