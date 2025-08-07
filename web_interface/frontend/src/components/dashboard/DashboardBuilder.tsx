import React, { useState, useCallback } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { Plus, Settings, Share, Download, Eye } from 'lucide-react';

interface DashboardBuilderProps {
  dashboard?: Dashboard;
  onSave?: (dashboard: Dashboard) => void;
  onCancel?: () => void;
  isEditing?: boolean;
}

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

const DashboardBuilder: React.FC<DashboardBuilderProps> = ({
  dashboard,
  onSave,
  onCancel,
  isEditing = false
}) => {
  const [currentDashboard, setCurrentDashboard] = useState<Dashboard>(
    dashboard || {
      id: '',
      name: 'New Dashboard',
      description: '',
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
      widgets: [],
      isPublic: false,
      createdAt: new Date(),
      updatedAt: new Date()
    }
  );

  const [selectedWidget, setSelectedWidget] = useState<string | null>(null);
  const [showWidgetLibrary, setShowWidgetLibrary] = useState(false);

  const handleDragEnd = useCallback((result: any) => {
    if (!result.destination) return;

    const { source, destination, draggableId } = result;

    if (source.droppableId === 'widget-library' && destination.droppableId === 'dashboard-grid') {
      // Add new widget from library
      const newWidget: Widget = {
        id: `widget-${Date.now()}`,
        type: draggableId as WidgetType,
        title: `New ${draggableId.charAt(0).toUpperCase() + draggableId.slice(1)}`,
        config: {},
        data: {},
        position: {
          id: `widget-${Date.now()}`,
          x: Math.floor(destination.x / currentDashboard.layout.grid.cellWidth),
          y: Math.floor(destination.y / currentDashboard.layout.grid.cellHeight),
          width: 3,
          height: 2
        }
      };

      setCurrentDashboard(prev => ({
        ...prev,
        widgets: [...prev.widgets, newWidget],
        layout: {
          ...prev.layout,
          widgets: [...prev.layout.widgets, newWidget.position]
        }
      }));
    } else if (source.droppableId === 'dashboard-grid' && destination.droppableId === 'dashboard-grid') {
      // Move existing widget
      const updatedWidgets = [...currentDashboard.widgets];
      const widgetIndex = updatedWidgets.findIndex(w => w.id === draggableId);
      
      if (widgetIndex !== -1) {
        const widget = updatedWidgets[widgetIndex];
        widget.position.x = Math.floor(destination.x / currentDashboard.layout.grid.cellWidth);
        widget.position.y = Math.floor(destination.y / currentDashboard.layout.grid.cellHeight);
        
        setCurrentDashboard(prev => ({
          ...prev,
          widgets: updatedWidgets
        }));
      }
    }
  }, [currentDashboard]);

  const handleWidgetSelect = (widgetId: string) => {
    setSelectedWidget(widgetId);
  };

  const handleWidgetConfigChange = (widgetId: string, config: WidgetConfig) => {
    setCurrentDashboard(prev => ({
      ...prev,
      widgets: prev.widgets.map(w => 
        w.id === widgetId ? { ...w, config } : w
      )
    }));
  };

  const handleWidgetDelete = (widgetId: string) => {
    setCurrentDashboard(prev => ({
      ...prev,
      widgets: prev.widgets.filter(w => w.id !== widgetId),
      layout: {
        ...prev.layout,
        widgets: prev.layout.widgets.filter(w => w.id !== widgetId)
      }
    }));
    setSelectedWidget(null);
  };

  const handleSave = () => {
    if (onSave) {
      onSave({
        ...currentDashboard,
        updatedAt: new Date()
      });
    }
  };

  const renderWidget = (widget: Widget) => {
    const { type, title, config, data } = widget;
    
    switch (type) {
      case WidgetType.METRIC:
        return (
          <div className="p-4 bg-white rounded-lg shadow border">
            <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
            <div className="text-3xl font-bold text-blue-600">
              {data.value || '0'}
            </div>
            <div className="text-sm text-gray-500">
              {data.change ? `${data.change > 0 ? '+' : ''}${data.change}%` : ''}
            </div>
          </div>
        );
      
      case WidgetType.CHART:
        return (
          <div className="p-4 bg-white rounded-lg shadow border">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
            <div className="h-32 bg-gray-100 rounded flex items-center justify-center">
              <span className="text-gray-500">Chart Placeholder</span>
            </div>
          </div>
        );
      
      case WidgetType.TABLE:
        return (
          <div className="p-4 bg-white rounded-lg shadow border">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
            <div className="bg-gray-100 rounded p-4">
              <span className="text-gray-500">Table Placeholder</span>
            </div>
          </div>
        );
      
      case WidgetType.TEXT:
        return (
          <div className="p-4 bg-white rounded-lg shadow border">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
            <p className="text-gray-600">{data.content || 'Text content'}</p>
          </div>
        );
      
      default:
        return (
          <div className="p-4 bg-white rounded-lg shadow border">
            <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
            <div className="text-gray-500">Widget Type: {type}</div>
          </div>
        );
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">
            {isEditing ? 'Edit Dashboard' : 'Create Dashboard'}
          </h2>
        </div>

        {/* Dashboard Info */}
        <div className="p-4 border-b border-gray-200">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dashboard Name
              </label>
              <input
                type="text"
                value={currentDashboard.name}
                onChange={(e) => setCurrentDashboard(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={currentDashboard.description}
                onChange={(e) => setCurrentDashboard(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Widget Library */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            <h3 className="text-lg font-medium text-gray-800 mb-4">Widget Library</h3>
            <Droppable droppableId="widget-library" isDropDisabled={true}>
              {(provided) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className="space-y-2"
                >
                  {Object.values(WidgetType).map((type, index) => (
                    <Draggable key={type} draggableId={type} index={index}>
                      {(provided) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className="p-3 bg-gray-50 border border-gray-200 rounded-md cursor-move hover:bg-gray-100"
                        >
                          <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
                              <span className="text-blue-600 text-sm font-medium">
                                {type.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <span className="text-sm font-medium text-gray-700">
                              {type.charAt(0).toUpperCase() + type.slice(1)}
                            </span>
                          </div>
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </div>
        </div>

        {/* Actions */}
        <div className="p-4 border-t border-gray-200">
          <div className="space-y-2">
            <button
              onClick={handleSave}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {isEditing ? 'Update Dashboard' : 'Create Dashboard'}
            </button>
            {onCancel && (
              <button
                onClick={onCancel}
                className="w-full bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-800">{currentDashboard.name}</h1>
              <div className="flex items-center space-x-2">
                <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded">
                  <Eye size={20} />
                </button>
                <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded">
                  <Settings size={20} />
                </button>
                <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded">
                  <Share size={20} />
                </button>
                <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded">
                  <Download size={20} />
                </button>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              {currentDashboard.widgets.length} widgets
            </div>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="flex-1 p-4 overflow-auto">
          <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="dashboard-grid">
              {(provided) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className="relative bg-white rounded-lg border border-gray-200 min-h-full"
                  style={{
                    display: 'grid',
                    gridTemplateColumns: `repeat(${currentDashboard.layout.grid.columns}, 1fr)`,
                    gridTemplateRows: `repeat(${currentDashboard.layout.grid.rows}, 1fr)`,
                    gap: '8px',
                    padding: '16px'
                  }}
                >
                  {currentDashboard.widgets.map((widget, index) => (
                    <Draggable key={widget.id} draggableId={widget.id} index={index}>
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className={`relative ${
                            snapshot.isDragging ? 'opacity-50' : ''
                          } ${
                            selectedWidget === widget.id ? 'ring-2 ring-blue-500' : ''
                          }`}
                          style={{
                            gridColumn: `span ${widget.position.width}`,
                            gridRow: `span ${widget.position.height}`,
                            ...provided.draggableProps.style
                          }}
                          onClick={() => handleWidgetSelect(widget.id)}
                        >
                          {renderWidget(widget)}
                          {selectedWidget === widget.id && (
                            <div className="absolute top-2 right-2 flex space-x-1">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleWidgetDelete(widget.id);
                                }}
                                className="p-1 bg-red-500 text-white rounded hover:bg-red-600"
                              >
                                ×
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        </div>
      </div>
    </div>
  );
};

export default DashboardBuilder; 