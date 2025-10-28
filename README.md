# Nestle UAE Price Optimization Platform

A modern fullstack application for dynamic price optimization built with FastAPI and Nuxt.js.

## Features

- 🎯 AI-powered price optimization recommendations
- 📊 Real-time demand and elasticity analysis
- 📈 Interactive charts and visualizations
- 💎 Modern glassmorphism UI with purple gradient theme
- 🚀 RESTful API architecture
- 📱 Responsive design

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **Nuxt 3** - Vue.js framework
- **Tailwind CSS** - Utility-first CSS
- **Chart.js** - Data visualization
- **Vue 3** - Progressive JavaScript framework

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── routes/
│   │   └── price_routes.py     # API endpoints
│   ├── services/
│   │   └── ai_service.py       # Mock AI/ML service
│   └── requirements.txt        # Python dependencies
│
└── frontend/
    ├── app.vue                 # Root component
    ├── nuxt.config.ts          # Nuxt configuration
    ├── tailwind.config.js      # Tailwind configuration
    ├── package.json            # Node dependencies
    ├── assets/
    │   └── css/
    │       └── main.css        # Global styles
    ├── components/
    │   ├── DemandChart.vue     # Demand curve visualization
    │   └── ProfitChart.vue     # Profit analysis chart
    ├── composables/
    │   └── useApi.ts           # API integration layer
    ├── layouts/
    │   └── default.vue         # Default layout
    └── pages/
        ├── index.vue           # Dashboard page
        └── products.vue        # Products listing page
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the FastAPI server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## API Endpoints

### Products
- `GET /api/products` - Get all products
- `GET /api/products/{product_id}` - Get specific product

### Price Optimization
- `POST /api/optimize-price` - Get price optimization recommendations
- `GET /api/simulate-price-impact` - Simulate price change impact

### Analytics
- `GET /api/analytics/summary` - Get analytics summary

## Features Overview

### Price Optimization Engine
The mock AI service simulates price optimization using economic principles:
- **Demand Calculation**: Uses price elasticity formula
- **Elasticity Analysis**: Categorizes products as elastic, inelastic, or unitary
- **Profit Maximization**: Finds optimal price points
- **Confidence Scoring**: Provides reliability metrics

### Visualizations
- **Demand Curve**: Shows how demand changes with price
- **Profit Analysis**: Highlights optimal pricing points
- **Revenue Projections**: Forecasts financial impact

### UI/UX
- Glassmorphism design with frosted glass effects
- Purple gradient theme
- Smooth animations and transitions
- Responsive layout for all devices

## Mock Data

The application includes 5 sample Nestle products:
1. Nescafé Classic 200g (Premium)
2. KitKat Chocolate Bar 45g (Standard)
3. Nestlé Pure Life Water 1.5L (Basic)
4. Maggi Noodles 5-Pack (Standard)
5. Nido Milk Powder 900g (Premium)

## Future Enhancements

- [ ] Real ML model integration
- [ ] Historical data tracking
- [ ] Competitor price monitoring
- [ ] Multi-currency support
- [ ] User authentication
- [ ] Export reports to PDF
- [ ] A/B testing capabilities
- [ ] Real-time market data integration

## Development Notes

### Mock AI Service
The current implementation uses mathematical models to simulate AI predictions. To integrate a real ML model:
1. Replace `MockAIService` in `backend/services/ai_service.py`
2. Add your trained model files
3. Update the optimization logic

### Styling
The glassmorphism effect is achieved using:
- `backdrop-blur` for frosted glass
- Semi-transparent backgrounds with `bg-white/10`
- Border with `border-white/20`
- Purple gradient overlays

## License

MIT

## Contact

For questions or support, please contact the development team.
