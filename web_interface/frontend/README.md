# MOVA Web Interface Frontend

React + TypeScript frontend for MOVA 2.2 Web Interface.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation
```bash
npm install
```

### Development
```bash
npm run dev
```

The application will be available at http://localhost:3000

### Build
```bash
npm run build
```

### Preview
```bash
npm run preview
```

## 🛠️ Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Run tests with coverage
- `npm run type-check` - Run TypeScript type checking

## 📁 Project Structure

```
src/
├── components/          # React components
│   ├── common/         # Shared components
│   ├── dashboard/      # Dashboard components
│   ├── editor/         # File editor components
│   ├── monitor/        # System monitor components
│   └── ml/            # ML components
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── services/           # API services
├── types/              # TypeScript types
├── utils/              # Utility functions
├── styles/             # CSS styles
└── test/               # Test files
```

## 🎨 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Routing
- **React Query** - Server state management
- **Zustand** - Client state management
- **Monaco Editor** - Code editor
- **Heroicons** - Icons
- **Headless UI** - Accessible components

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=MOVA Web Interface
```

### API Proxy
The development server is configured to proxy API requests to the backend at `http://localhost:8000`.

## 📱 Features

- **Dashboard** - System overview and quick actions
- **File Editor** - Monaco Editor with MOVA syntax highlighting
- **System Monitor** - Real-time metrics and monitoring
- **ML Management** - Model training and management
- **File Management** - Upload, organize, and manage files
- **Responsive Design** - Works on desktop, tablet, and mobile

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## 📦 Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 🚀 Deployment

The application can be deployed to any static hosting service:

- Vercel
- Netlify
- GitHub Pages
- AWS S3
- etc.

## 📄 License

GPL v3 - Same as the main MOVA project 