# AI Mining Operations Co-Pilot

## Overview

This is a full-stack AI-powered mining operations co-pilot application that provides natural language querying, predictive maintenance alerts, fuel consumption analysis, and production efficiency tracking for mining equipment. The system consists of a Flask backend with simulated time-series data and an Angular web frontend with real-time visualizations.

The application uses AI (Groq Cloud API with Llama 3.3 70B Versatile model) to process natural language queries about mining operations and provides insights through text responses and interactive charts.

**Status:** Production-ready MVP for web application. Mobile Flutter app planned for Phase 2.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture (Flask + Python)

**Technology Stack:**
- Flask web framework for REST API endpoints
- Flask-CORS for cross-origin resource sharing
- Pandas and NumPy for data processing
- Groq Cloud API for AI-powered natural language processing

**Design Decisions:**
- **Simulated Data Storage**: Equipment and sensor data are stored in-memory as Python dictionaries and lists rather than using a real database. This allows for rapid prototyping and demonstration without database setup complexity.
  - **Alternative Considered**: MySQL for persistent storage
  - **Pros**: Fast development, no database configuration needed, easy to modify test data
  - **Cons**: Data doesn't persist between restarts, not suitable for production

- **Time-Series Simulation**: Instead of using AWS Timestream, sensor data is generated algorithmically using random functions. This eliminates cloud dependencies and costs during development.
  - **Rationale**: Allows offline development and testing without AWS credentials

- **AI Integration**: Uses Groq Cloud API as the LLM provider for natural language query processing
  - **Environment Variable**: Requires `GROQ_API_KEY` to be set (configured via Replit Secrets)
  - **Model**: Llama 3.3 70B Versatile for high-quality, context-aware responses
  - **Implementation**: Direct API integration with contextual mining data prompting
  - **Error Handling**: Robust timeout and error handling with graceful fallbacks

**API Endpoints:**
- `/api/query` - Receives natural language queries and returns AI-generated responses
- `/api/data` - Returns equipment and sensor data
- `/api/alerts` - Returns maintenance alerts based on equipment runtime and due dates

### Frontend Architecture (Angular 17)

**Technology Stack:**
- Angular 17 with standalone components (no NgModules)
- Chart.js for data visualization
- RxJS for reactive programming
- Standalone component architecture

**Design Decisions:**
- **Standalone Components**: Uses Angular's modern standalone component approach, eliminating the need for NgModules
  - **Pros**: Simpler project structure, better tree-shaking, easier to understand
  - **Cons**: Relatively new pattern, less community examples

- **HTTP Communication**: Uses Angular's HttpClient with provideHttpClient() for API calls
  - **Backend URL**: Configured to `http://localhost:8000` for local development
  - **Port Configuration**: Backend runs on port 8000, frontend on port 5000

- **Real-time Charts**: Chart.js integration for visualizing fuel consumption and production metrics
  - **Configuration**: Charts are created dynamically in component lifecycle
  - **Data Binding**: Uses two-way binding with FormsModule for user input

- **State Management**: Simple component-based state without external libraries
  - **Rationale**: Application complexity doesn't warrant Redux/NgRx
  - **Message History**: Stored in component array with timestamp tracking

### Mobile Architecture (Flutter)

**Design Approach:**
- Cross-platform mobile app using Flutter framework
- Chat interface with bubble design for user/AI conversations
- API integration with the Flask backend
- Voice input ready (prepared for future implementation)

**Technology Choices:**
- Flutter for true native performance on iOS and Android
- HTTP client for REST API communication
- Material Design components for consistent UI

### Data Flow

1. **User Query Flow**:
   - User enters natural language query in frontend/mobile
   - Request sent to `/api/query` endpoint
   - Backend processes query with context about equipment data
   - Groq API generates natural language response
   - Response displayed in chat interface

2. **Equipment Data Flow**:
   - Frontend polls `/api/data` endpoint
   - Backend returns current equipment status and sensor readings
   - Charts updated with new data
   - Real-time visualization rendered

3. **Alert System**:
   - Backend calculates maintenance alerts based on due dates
   - `/api/alerts` endpoint returns upcoming maintenance items
   - Frontend displays alerts with severity indicators

## External Dependencies

### Third-Party APIs
- **Groq Cloud API**: LLM service for natural language processing
  - Requires API key via environment variable `GROQ_API_KEY`
  - Used model: Llama 3.3 70B
  - Endpoint: `https://api.groq.com/openai/v1/chat/completions`

### NPM Packages (Frontend)
- **@angular/core**: Framework core (v17.3.0)
- **chart.js**: Data visualization library (v4.4.0)
- **rxjs**: Reactive programming library (v7.8.0)
- **@angular/router**: Client-side routing
- **zone.js**: Change detection mechanism

### Python Packages (Backend)
- **Flask**: Web framework (v3.0.0)
- **Flask-CORS**: Cross-origin resource sharing (v4.0.0)
- **pandas**: Data manipulation (v2.1.4)
- **numpy**: Numerical computing (v1.26.2)
- **requests**: HTTP library for API calls (v2.31.0)

### Development Dependencies
- **@angular/cli**: Angular command-line interface (v17.3.0)
- **TypeScript**: Typed JavaScript superset (v5.4.2)
- **@angular-devkit/build-angular**: Build system (v17.3.0)

### Future Integrations (Noted in Specification)
- **MySQL**: For persistent equipment and production data storage
- **AWS Timestream**: For real-time sensor data storage and querying
- **Vector Database**: For semantic search capabilities (not yet implemented)
- **Voice Input Libraries**: Speech-to-text for mobile and web interfaces