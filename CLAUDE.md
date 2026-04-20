# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Build and Development
- `npm run build` - Compile TypeScript to dist/
- `npm run dev` - Run in development mode with hot reload using tsx
- `npm start` - Run compiled version from dist/
- `npm run lint` - Run ESLint on source files
- `npm run lint:fix` - Auto-fix ESLint issues
- `npm run quality` - Run type-check, lint, and format checks
- `npm test` - Run Jest tests

### Testing
- Use `node test-mcp-server.sh` script to test the MCP server functionality
- Jest is configured for unit testing

### Environment Setup
- Copy `.env.example` to `.env` and add `GOOGLE_MAPS_API_KEY`
- Google Maps API key must have Places API, Geocoding API, and related services enabled
- Default search location is Taiwan (24.1501164, 120.6692299)

## Architecture Overview

This is an **MCP (Model Context Protocol) server** for AI-powered restaurant booking and recommendations.

### Core Components

**Main Server (`src/index.ts`)**
- RestaurantBookingServer class implements MCP server
- Express.js HTTP server with session management
- Five main MCP tools: search_restaurants, get_restaurant_details, get_booking_instructions, check_availability, make_reservation
- Uses StreamableHTTPServerTransport for MCP communication

**Service Layer (`src/services/`)**
- `GoogleMapsService` - Integrates with Google Places API for restaurant data, geocoding, and photo references
- `RestaurantRecommendationService` - AI scoring engine that evaluates restaurants based on rating (40%), review count (20%), cuisine match (20%), event suitability (10%), and mood match (10%)
- `BookingService` - Mock reservation system with real booking platform detection

**Type Definitions (`src/types/index.ts`)**
- Complete TypeScript interfaces for Restaurant, Location, BookingRequest, etc.
- Google Places API response types
- Search parameters with support for coordinates, place names, or keyword searches

### Key Features

**Smart Restaurant Search**
- 20km default radius (configurable via DEFAULT_SEARCH_RADIUS env var)
- Supports coordinates, place names, or keyword-based searching
- Multi-language support via locale parameter
- Cuisine type mapping and filtering

**AI Recommendation Engine**
- Weighted scoring system based on multiple factors
- Event-specific suitability (dating, business, family, celebration)
- Mood matching (romantic, casual, upscale, fun, quiet)
- Returns top 3 recommendations with detailed reasoning

**Booking Integration**
- Mock booking system with real platform detection (OpenTable, Resy, etc.)
- Phone-only and walk-in restaurant handling
- Booking instruction generation

### Configuration

**Environment Variables**
- `GOOGLE_MAPS_API_KEY` (required)
- `DEFAULT_LATITUDE` (default: 24.1501164)
- `DEFAULT_LONGITUDE` (default: 120.6692299)
- `DEFAULT_SEARCH_RADIUS` (default: 3000 meters)
- `PORT` (default: 3000)

**TypeScript Config**
- Target ES2020, ESNext modules
- Path alias `@/*` points to `src/*`
- Strict mode enabled
- Outputs to `dist/` directory

### Cursor Rules Integration

The `.cursor/rules/booking-rule.mdc` file contains specific instructions for AI assistants working with this codebase:
- Conversational, short responses required
- Must use coordinates from user context when provided
- Autonomous restaurant selection without asking questions
- Screenshot-based reservation URL extraction workflow
- Plain text formatting only (no markdown)
- Integration with browser MCP for reservation handling

### Key Customization Points

**Adding Cuisine Types**
Edit `cuisineMap` in `src/services/googleMapsService.ts`

**Modifying Recommendation Logic**
Update scoring methods in `src/services/restaurantRecommendationService.ts`:
- `calculateRestaurantScore()` - Overall scoring
- `calculateEventSuitability()` - Event-specific criteria  
- `calculateMoodMatch()` - Mood matching algorithms

**Adding Event Types**
1. Update event enum in `src/types/index.ts`
2. Add criteria in `calculateEventSuitability()` method

### Docker Support

Dockerfile available for containerized deployment. Build with `docker build -t mcp/booking .`

### Limitations

- Booking system is currently mock implementation
- Real booking requires integration with restaurant-specific systems
- Google Places API has usage limits and costs
- Geographic coverage limited to Google Places API coverage