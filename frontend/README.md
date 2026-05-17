# Court in Your Pocket - Frontend

A messenger-style chat interface for legal assistance powered by AI.

## Features

- 💬 **Chat Interface**: WhatsApp-like messaging experience
- 🤖 **AI Assistant (Bob)**: Guides users through legal processes
- 📋 **Action Plans**: Step-by-step guidance for legal issues
- 📄 **Document Generation**: Auto-generated legal documents
- 📱 **Mobile Responsive**: Works seamlessly on all devices
- 🔗 **Share Options**: Download PDF or share via WhatsApp

## Tech Stack

- **React 19** - UI framework
- **Vite** - Build tool
- **CSS3** - Styling with animations
- **Fetch API** - Backend communication

## Getting Started

### Prerequisites

- Node.js 20+ or 22+
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
```bash
cd frontend
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Update `.env` with your backend URL:
```
VITE_API_BASE_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

Create a production build:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatMessage.jsx      # Message component
│   │   └── ChatMessage.css      # Message styles
│   ├── services/
│   │   └── api.js               # API integration
│   ├── App.jsx                  # Main app component
│   ├── App.css                  # App styles
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── public/                      # Static assets
├── .env.example                 # Environment template
├── package.json                 # Dependencies
└── vite.config.js              # Vite configuration
```

## User Flow

1. **Initial Greeting**: Bob welcomes the user
2. **Issue Description**: User describes their legal problem
3. **Fact Collection**: Bob asks clarifying questions
4. **Law Information**: Display relevant laws and rights
5. **Action Options**: User chooses A/B/C
6. **Action Plan**: Generate step-by-step plan
7. **Document Generation**: Create legal documents (if applicable)
8. **Download/Share**: User can download or share documents

## API Integration

The frontend communicates with the backend through these endpoints:

- `POST /api/action-plan/generate` - Generate action plan
- `POST /api/document/generate` - Generate legal document
- `GET /api/action-plan/health` - Health check

## Customization

### Styling

Modify the CSS files to customize:
- Colors and themes
- Message bubble styles
- Button appearances
- Animations

### Chat Flow

Update `App.jsx` to modify:
- Conversation logic
- State management
- API calls
- Message handling

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.
