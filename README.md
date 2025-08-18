# Semantic Search Category Application

A modern Next.js application featuring semantic search functionality and interactive category selection for business use cases.

## Features

### 🔍 Semantic Search
- Real-time search with 300ms debouncing
- Intelligent filtering based on titles, descriptions, and tags
- Relevance scoring system prioritizing title matches
- Fuzzy matching for similar words

### 📋 Interactive Categories
- 6 predefined business categories:
  - **Happy Hour**: Promote special drink offers during happy hours
  - **Birthdays**: Create personalized birthday campaigns
  - **Weather-based Promocode**: Generate weather-dependent promotions
  - **Social Media Posts**: Automated content generation
  - **Know Your Consumer**: Customer analytics and insights
  - **Recommend Items**: AI-powered product recommendations

### 🎨 Modern UI/UX
- Clean, responsive design with Tailwind CSS
- Visual feedback for selections and loading states
- Hover effects and smooth transitions
- Error handling with user-friendly messages
- Accessibility features including screen reader support

### ⚡ State Management
- Custom React hooks for category management
- Real-time loading states and error handling
- Debounced search to optimize API calls
- Selection tracking with visual indicators

## Technology Stack

- **Frontend**: Next.js 14, React, TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **API**: Next.js API Routes
- **State Management**: React Hooks

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── categories/
│   │   │       ├── route.ts          # Semantic search API
│   │   │       └── select/
│   │   │           └── route.ts      # Category selection API
│   │   ├── globals.css               # Global styles
│   │   └── page.tsx                  # Main homepage
│   └── hooks/
│       └── useCategories.ts          # Category management hook
└── backend/
    ├── main.py                       # Python backend server
    ├── agent.py                      # AI agent logic
    └── data/
        └── dummy_data.py             # Mock data
```

## API Endpoints

### GET /api/categories
Returns filtered categories based on search query.

**Parameters:**
- `q` (optional): Search query string

**Response:**
```json
[
  {
    "id": 1,
    "title": "Happy hour",
    "description": "Promote special drink offers during happy hours",
    "tags": ["drinks", "promotion", "evening", "bar"]
  }
]
```

### POST /api/categories/select
Processes category selection and triggers backend workflows.

**Request Body:**
```json
{
  "categoryId": 1,
  "additionalData": {}
}
```

**Response:**
```json
{
  "success": true,
  "message": "Category processed successfully",
  "data": {
    "action": "promotion_created",
    "jobId": "job_12345",
    "estimatedCompletion": "2024-01-15T10:30:00Z"
  }
}
```

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Python 3.8+ (for backend)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Hackathon
   ```

2. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd ../backend
   pip install -r ../requirements.txt
   ```

### Running the Application

1. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```
   The application will be available at `http://localhost:3001`

2. **Start the backend server** (optional)
   ```bash
   cd backend
   python main.py
   ```

## Usage

1. **Search Categories**: Use the search bar to find relevant categories
2. **Select Category**: Click on any category card to select it
3. **View Details**: Selected categories show additional information and tags
4. **Process Selection**: The system automatically processes selections and provides feedback

## Development

### Key Components

- **useCategories Hook**: Manages all category-related state and API calls
- **Semantic Search**: Implements intelligent search with relevance scoring
- **Category Grid**: Responsive grid layout with interactive cards
- **Error Handling**: Comprehensive error states and user feedback

### Customization

To add new categories, update the `allCategories` array in `/api/categories/route.ts` and add corresponding processing logic in `/api/categories/select/route.ts`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.