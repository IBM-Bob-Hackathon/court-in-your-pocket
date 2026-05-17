# Frontend Setup Guide

## Prerequisites

- **Node.js**: Version 18.x or higher
- **npm**: Version 9.x or higher (comes with Node.js)

## Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

   This will install all dependencies listed in `package.json`:
   
   ### Main Dependencies
   - `react` (^19.2.6) - React library
   - `react-dom` (^19.2.6) - React DOM rendering
   - `react-router-dom` (^7.15.1) - Client-side routing
   
   ### Dev Dependencies
   - `vite` (^8.0.12) - Build tool and dev server
   - `@vitejs/plugin-react` (^6.0.1) - Vite plugin for React
   - `eslint` (^10.3.0) - Code linting
   - `eslint-plugin-react-hooks` (^7.1.1) - React Hooks linting rules
   - `eslint-plugin-react-refresh` (^0.5.2) - React Refresh linting
   - TypeScript type definitions for React

## Development

1. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The app will be available at `http://localhost:5173`

2. **API Proxy Configuration:**
   - The Vite dev server is configured to proxy `/api` requests to `http://localhost:8000`
   - Make sure the backend FastAPI server is running on port 8000

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

## Preview Production Build

```bash
npm run preview
```

## Code Quality

Run ESLint to check code quality:
```bash
npm run lint
```

## Project Structure

```
frontend/
├── public/          # Static assets
├── src/
│   ├── assets/      # Images, icons
│   ├── context/     # React Context (AppContext)
│   ├── screens/     # Page components (RightsScreen, etc.)
│   ├── App.jsx      # Main App component
│   ├── main.jsx     # Entry point with Router and Context providers
│   └── index.css    # Global styles
├── package.json     # Dependencies and scripts
└── vite.config.js   # Vite configuration with proxy
```

## Key Features Configured

1. **React Router** - Client-side routing with `BrowserRouter`
2. **App Context** - Global state management with `AppProvider`
3. **API Proxy** - Development proxy for backend API calls
4. **Tailwind CSS** - Utility-first CSS framework (configured in index.css)

## Troubleshooting

### Port Already in Use
If port 5173 is already in use, Vite will automatically try the next available port.

### API Calls Failing
- Ensure the backend server is running on `http://localhost:8000`
- Check the proxy configuration in `vite.config.js`

### Module Not Found Errors
Run `npm install` again to ensure all dependencies are installed.

## Environment Variables

If needed, create a `.env` file in the frontend directory:
```
VITE_API_URL=http://localhost:8000
```

Access in code with `import.meta.env.VITE_API_URL`

## Additional Resources

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [React Router Documentation](https://reactrouter.com/)