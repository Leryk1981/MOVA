import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, Grid, List, MoreVertical, Edit, Trash2, Eye, Share, Download } from 'lucide-react';
import DashboardBuilder from '../components/dashboard/DashboardBuilder';
import DashboardViewer from '../components/dashboard/DashboardViewer';
import WidgetLibrary from '../components/dashboard/WidgetLibrary';

interface Dashboard {
  id: string;
  name: string;
  description: string;
  layout: DashboardLayout;
  widgets: Widget[];
  template?: string;
  isPublic: boolean;
  createdAt: Date;
  updatedAt: Date;
}

interface DashboardLayout {
  grid: GridConfig;
  widgets: WidgetPosition[];
  theme: DashboardTheme;
}

interface GridConfig {
  columns: number;
  rows: number;
  cellWidth: number;
  cellHeight: number;
}

interface WidgetPosition {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

interface Widget {
  id: string;
  type: WidgetType;
  title: string;
  config: WidgetConfig;
  data: WidgetData;
  position: WidgetPosition;
}

interface WidgetConfig {
  [key: string]: any;
}

interface WidgetData {
  [key: string]: any;
}

interface DashboardTheme {
  primaryColor: string;
  secondaryColor: string;
  backgroundColor: string;
  textColor: string;
}

enum WidgetType {
  METRIC = 'metric',
  CHART = 'chart',
  TABLE = 'table',
  TEXT = 'text',
  IMAGE = 'image',
  CUSTOM = 'custom'
}

// Mock data for demonstration
const mockDashboards: Dashboard[] = [
  {
    id: '1',
    name: 'System Overview',
    description: 'Overview of system performance and key metrics',
    layout: {
      grid: { columns: 12, rows: 8, cellWidth: 100, cellHeight: 100 },
      widgets: [],
      theme: {
        primaryColor: '#3B82F6',
        secondaryColor: '#6B7280',
        backgroundColor: '#FFFFFF',
        textColor: '#1F2937'
      }
    },
    widgets: [
      {
        id: 'widget-1',
        type: WidgetType.METRIC,
        title: 'Active Users',
        config: { format: 'number', showTrend: true },
        data: { value: 1234, trendValue: 12.5 },
        position: { id: 'widget-1', x: 0, y: 0, width: 3, height: 2 }
      },
      {
        id: 'widget-2',
        type: WidgetType.METRIC,
        title: 'Response Time',
        config: { format: 'number' },
        data: { value: 245 },
        position: { id: 'widget-2', x: 3, y: 0, width: 3, height: 2 }
      },
      {
        id: 'widget-3',
        type: WidgetType.CHART,
        title: 'Performance Trend',
        config: { chartType: 'line' },
        data: { chartData: [] },
        position: { id: 'widget-3', x: 0, y: 2, width: 6, height: 3 }
      }
    ],
    isPublic: true,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-15')
  },
  {
    id: '2',
    name: 'ML Analytics',
    description: 'Machine learning model performance and analytics',
    layout: {
      grid: { columns: 12, rows: 8, cellWidth: 100, cellHeight: 100 },
      widgets: [],
      theme: {
        primaryColor: '#10B981',
        secondaryColor: '#6B7280',
        backgroundColor: '#FFFFFF',
        textColor: '#1F2937'
      }
    },
    widgets: [
      {
        id: 'widget-4',
        type: WidgetType.METRIC,
        title: 'Model Accuracy',
        config: { format: 'percentage' },
        data: { value: 94.2 },
        position: { id: 'widget-4', x: 0, y: 0, width: 3, height: 2 }
      },
      {
        id: 'widget-5',
        type: WidgetType.CHART,
        title: 'Training Progress',
        config: { chartType: 'line' },
        data: { chartData: [] },
        position: { id: 'widget-5', x: 3, y: 0, width: 6, height: 4 }
      },
      {
        id: 'widget-6',
        type: WidgetType.TABLE,
        title: 'Model Comparison',
        config: { pagination: true, sorting: true },
        data: { tableData: [], columns: [] },
        position: { id: 'widget-6', x: 0, y: 4, width: 9, height: 3 }
      }
    ],
    isPublic: false,
    createdAt: new Date('2024-01-10'),
    updatedAt: new Date('2024-01-20')
  }
];

const Dashboards: React.FC = () => {
  const [dashboards, setDashboards] = useState<Dashboard[]>(mockDashboards);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'public' | 'private'>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedDashboard, setSelectedDashboard] = useState<Dashboard | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [isViewing, setIsViewing] = useState(false);
  const [showWidgetLibrary, setShowWidgetLibrary] = useState(false);

  const filteredDashboards = dashboards.filter(dashboard => {
    const matchesSearch = dashboard.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         dashboard.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || 
                         (filterStatus === 'public' && dashboard.isPublic) ||
                         (filterStatus === 'private' && !dashboard.isPublic);
    return matchesSearch && matchesFilter;
  });

  const handleCreateDashboard = () => {
    setIsCreating(true);
  };

  const handleEditDashboard = (dashboard: Dashboard) => {
    setSelectedDashboard(dashboard);
    setIsEditing(true);
  };

  const handleViewDashboard = (dashboard: Dashboard) => {
    setSelectedDashboard(dashboard);
    setIsViewing(true);
  };

  const handleDeleteDashboard = (dashboardId: string) => {
    if (confirm('Are you sure you want to delete this dashboard?')) {
      setDashboards(prev => prev.filter(d => d.id !== dashboardId));
    }
  };

  const handleSaveDashboard = (dashboard: Dashboard) => {
    if (isCreating) {
      const newDashboard = {
        ...dashboard,
        id: Date.now().toString(),
        createdAt: new Date(),
        updatedAt: new Date()
      };
      setDashboards(prev => [...prev, newDashboard]);
      setIsCreating(false);
    } else if (isEditing) {
      setDashboards(prev => prev.map(d => 
        d.id === dashboard.id ? { ...dashboard, updatedAt: new Date() } : d
      ));
      setIsEditing(false);
      setSelectedDashboard(null);
    }
  };

  const handleCancel = () => {
    setIsCreating(false);
    setIsEditing(false);
    setIsViewing(false);
    setSelectedDashboard(null);
  };

  const handleRefreshDashboard = async () => {
    // Simulate refreshing dashboard data
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('Dashboard refreshed');
  };

  if (isCreating) {
    return <DashboardBuilder onSave={handleSaveDashboard} onCancel={handleCancel} />;
  }

  if (isEditing && selectedDashboard) {
    return (
      <DashboardBuilder 
        dashboard={selectedDashboard}
        onSave={handleSaveDashboard}
        onCancel={handleCancel}
        isEditing={true}
      />
    );
  }

  if (isViewing && selectedDashboard) {
    return (
      <DashboardViewer
        dashboard={selectedDashboard}
        isEditable={true}
        onEdit={() => handleEditDashboard(selectedDashboard)}
        onRefresh={handleRefreshDashboard}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Dashboards</h1>
              <p className="text-gray-600 mt-1">Create and manage your analytics dashboards</p>
            </div>
            <button
              onClick={handleCreateDashboard}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center space-x-2"
            >
              <Plus size={20} />
              <span>Create Dashboard</span>
            </button>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search dashboards..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="flex items-center space-x-2">
              <Filter size={20} className="text-gray-400" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as 'all' | 'public' | 'private')}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Dashboards</option>
                <option value="public">Public</option>
                <option value="private">Private</option>
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <Grid size={20} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <List size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Dashboard Grid/List */}
      <div className="p-6">
        {filteredDashboards.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📊</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No dashboards found</h3>
            <p className="text-gray-500 mb-6">
              {searchTerm || filterStatus !== 'all' 
                ? 'Try adjusting your search or filters'
                : 'Get started by creating your first dashboard'
              }
            </p>
            {!searchTerm && filterStatus === 'all' && (
              <button
                onClick={handleCreateDashboard}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Create Dashboard
              </button>
            )}
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
            : 'space-y-4'
          }>
            {filteredDashboards.map(dashboard => (
              <div
                key={dashboard.id}
                className={`bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow ${
                  viewMode === 'list' ? 'flex' : ''
                }`}
              >
                {/* Dashboard Preview */}
                <div className={`${viewMode === 'list' ? 'w-48' : 'h-48'} bg-gray-50 flex items-center justify-center`}>
                  <div className="text-center">
                    <div className="text-4xl mb-2">📊</div>
                    <div className="text-sm text-gray-500">{dashboard.widgets.length} widgets</div>
                  </div>
                </div>

                {/* Dashboard Info */}
                <div className={`p-4 ${viewMode === 'list' ? 'flex-1' : ''}`}>
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-800 truncate">{dashboard.name}</h3>
                    <div className="flex items-center space-x-1">
                      {dashboard.isPublic && (
                        <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                          Public
                        </span>
                      )}
                      <button className="p-1 text-gray-400 hover:text-gray-600">
                        <MoreVertical size={16} />
                      </button>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {dashboard.description || 'No description'}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                    <span>Updated {dashboard.updatedAt.toLocaleDateString()}</span>
                    <span>{dashboard.widgets.length} widgets</span>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleViewDashboard(dashboard)}
                      className="flex-1 bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 flex items-center justify-center space-x-1"
                    >
                      <Eye size={14} />
                      <span>View</span>
                    </button>
                    
                    <button
                      onClick={() => handleEditDashboard(dashboard)}
                      className="p-2 text-gray-400 hover:text-gray-600 border border-gray-300 rounded"
                    >
                      <Edit size={14} />
                    </button>
                    
                    <button
                      onClick={() => handleDeleteDashboard(dashboard.id)}
                      className="p-2 text-gray-400 hover:text-red-600 border border-gray-300 rounded"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Widget Library Modal */}
      {showWidgetLibrary && (
        <WidgetLibrary
          onWidgetSelect={(widget) => {
            console.log('Selected widget:', widget);
            setShowWidgetLibrary(false);
          }}
          onClose={() => setShowWidgetLibrary(false)}
        />
      )}
    </div>
  );
};

export default Dashboards; 