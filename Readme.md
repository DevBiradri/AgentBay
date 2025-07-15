# 🎯 AgentBay

AI powered auction marketplace to revolutionize online auctions. This platform seamlessly integrates text, images, and voice interactions to create an intuitive and intelligent auction experience.

## 🚀 Features

### 🤖 AI-Powered Intelligence
- **Smart Listing Agent**: Automatically analyzes product images and generates compelling auction descriptions and other required fields using ListingAgent
- **Intelligent Recommendations**: Personalized product suggestions based on user query and preferences
- **Natural Language Search**: Ask questions like "find me vintage sneakers under $100" and get relevant results
- **Price Optimization**: Automated price suggestions based on market trends and item characteristics

### 💰 Auction Features
- **Bidding**: create bids on products
- **Auction Categories**: Organized product categories for easy browsing

### 📱 User Experience
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Interactive Chat**: AI-powered chat interface for buyer assistance
- **Image Upload**: Multi-image support for auction listings

## 🛠️ Tech Stack

### Backend
- **Framework**: Python + FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Framework**: Google Agent Development Kit (ADK)
- **AI Models**: Google Gemini

### Frontend
- **Framework**: React
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **State Management**: React hooks + Context API
- **UI Components**: Custom component library

## 📁 Project Structure

```
AgentBay/
├── backend/
│   ├── .gitignore
│   ├── .python-version
│   ├── alembic/
│   │   ├── env.py
│   │   ├── README
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── alembic.ini
│   ├── app/
│   │   ├── agents/
│   │   │   ├── listing_agent/
│   │   │   │   └── agent.py
│   │   │   ├── recommendation_agent/
│   │   │   │   └── agent.py
│   │   │   └── voice_agent/
│   │   │       └── agent.py
│   │   ├── api/
│   │   │   └── api.py
│   │   ├── database.py
│   │   ├── enums/
│   │   │   └── enums.py
│   │   ├── main.py
│   │   ├── models/
│   │   │   ├── agent_models.py
│   │   │   ├── converters/
│   │   │   │   └── converters.py
│   │   │   ├── db_models.py
│   │   │   └── request_models.py
│   │   └── services/
│   │       ├── bid_service.py
│   │       └── product_service.py
│   ├── backend/
│   │   └── data/
│   │       └── products.json
│   ├── products.json
│   ├── pyproject.toml
│   ├── uploads/
│   │   └── images/
│   └── uv.lock
└── frontend/
    ├── .gitignore
    ├── bun.lockb
    ├── components.json
    ├── eslint.config.js
    ├── index.html
    ├── package-lock.json
    ├── package.json
    ├── postcss.config.js
    ├── public/
    │   ├── favicon.ico
    │   ├── placeholder.svg
    │   └── robots.txt
    ├── README.md
    ├── src/
    │   ├── App.css
    │   ├── App.tsx
    │   ├── assets/
    │   │   ├── architecture.svg
    │   │   ├── marketplace-hero.jpg
    │   │   ├── personalized-experience.jpg
    │   │   ├── search-feature.jpg
    │   │   ├── sparkles.png
    │   │   └── upload-feature.jpg
    │   ├── components/
    │   │   ├── landing/
    │   │   │   ├── AnimatedTooltip.tsx
    │   │   │   ├── CTASection.tsx
    │   │   │   ├── FeaturesSection.tsx
    │   │   │   ├── Footer.tsx
    │   │   │   ├── HeroSection.tsx
    │   │   │   ├── HowItWorksSection.tsx
    │   │   │   ├── Navigation.tsx
    │   │   │   └── ProductForm.tsx
    │   │   ├── RecommendationCards.tsx
    │   │   └── ui/
    │   │       ├── accordion.tsx
    │   │       ├── alert-dialog.tsx
    │   │       ├── alert.tsx
    │   │       ├── animated-tooltip.tsx
    │   │       ├── aspect-ratio.tsx
    │   │       ├── avatar.tsx
    │   │       ├── badge.tsx
    │   │       ├── breadcrumb.tsx
    │   │       ├── button.tsx
    │   │       ├── calendar.tsx
    │   │       ├── card.tsx
    │   │       ├── carousel.tsx
    │   │       ├── chart.tsx
    │   │       ├── checkbox.tsx
    │   │       ├── collapsible.tsx
    │   │       ├── command.tsx
    │   │       ├── context-menu.tsx
    │   │       ├── dialog.tsx
    │   │       ├── drawer.tsx
    │   │       ├── dropdown-menu.tsx
    │   │       ├── form.tsx
    │   │       ├── hover-card.tsx
    │   │       ├── input-otp.tsx
    │   │       ├── input.tsx
    │   │       ├── label.tsx
    │   │       ├── menubar.tsx
    │   │       ├── navigation-menu.tsx
    │   │       ├── pagination.tsx
    │   │       ├── popover.tsx
    │   │       ├── progress.tsx
    │   │       ├── radio-group.tsx
    │   │       ├── resizable.tsx
    │   │       ├── scroll-area.tsx
    │   │       ├── select.tsx
    │   │       ├── separator.tsx
    │   │       ├── sheet.tsx
    │   │       ├── sidebar.tsx
    │   │       ├── skeleton.tsx
    │   │       ├── slider.tsx
    │   │       ├── sonner.tsx
    │   │       ├── switch.tsx
    │   │       ├── table.tsx
    │   │       ├── tabs.tsx
    │   │       ├── textarea.tsx
    │   │       ├── theme-toggle.tsx
    │   │       ├── toast.tsx
    │   │       ├── toaster.tsx
    │   │       ├── toggle-group.tsx
    │   │       ├── toggle.tsx
    │   │       ├── tooltip.tsx
    │   │       └── use-toast.ts
    │   ├── contexts/
    │   │   └── ThemeContext.tsx
    │   ├── data/
    │   │   └── products.js
    │   ├── hooks/
    │   │   ├── use-mobile.tsx
    │   │   └── use-toast.ts
    │   ├── index.css
    │   ├── lib/
    │   │   └── utils.ts
    │   ├── main.tsx
    │   ├── pages/
    │   │   ├── Architecture.tsx
    │   │   ├── Chat.tsx
    │   │   ├── Index.tsx
    │   │   ├── NotFound.tsx
    │   │   ├── Products.tsx
    │   │   ├── Signin.tsx
    │   │   └── Signup.tsx
    │   └── vite-env.d.ts
    ├── tailwind.config.ts
    ├── tsconfig.app.json
    ├── tsconfig.json
    ├── tsconfig.node.json
    └── vite.config.ts

```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Gemini API Key

## 📡 API Endpoints

### Static Files
- `GET /uploads/images/{filename}` - Serve uploaded product images

### AI Agent Features
- `POST /api/agent/create-listing` - Create listing using AI agent (with image upload)
  - **Parameters**: `image` (file), `user_preferences` (JSON string)
  - **Response**: AI-generated product listing with description and pricing
- `POST /api/agent/recommendations` - Get AI-powered product recommendations
  - **Body**: `RecommendationRequest` with query string
  - **Response**: Personalized product suggestions

### Products
- `GET /api/products` - List all products
- `POST /api/products` - Create new product
  - **Body**: `ProductCreateRequest`
  - **Response**: Created product with ID
- `GET /api/products/{product_id}` - Get specific product details
  - **Response**: Product data with database timestamps

### Bidding
- `GET /api/products/{product_id}/bids` - Get all bids for a product
  - **Query Parameters**: `limit` (max 500, default 100)
  - **Response**: List of bids with bid count
- `POST /api/products/{product_id}/bids` - Place a bid on a product
  - **Body**: `BidCreateRequest` with user_id, amount, auto_bid options
  - **Response**: Created bid with status updates
- `GET /api/products/{product_id}/highest-bid` - Get highest bid for a product
  - **Response**: Current highest bid information
- `GET /api/users/{user_id}/bids` - Get all bids by a user
  - **Query Parameters**: `active_only` (boolean), `limit` (max 500)
  - **Response**: User's bid history

### Request/Response Models
- `ProductCreateRequest` - Product creation data
- `BidCreateRequest` - Bid placement data (user_id, amount, is_auto_bid, max_auto_bid)
- `RecommendationRequest` - AI recommendation query
- `Product` - Product model with AI-generated fields
- `Bid` - Bid model with status and auto-bidding features

## 🤖 Google ADK Integration

### Agent Architecture
The application uses Google ADK's multi-agent system:

1. **ListingAgent**: Analyzes product images and generates descriptions
2. **RecommendationAgent**: Provides personalized product suggestions

### API Testing
Import the Postman collection for comprehensive API testing:
- **Postman Collection**: [AgentBay API Collection](https://bold-trinity-835723.postman.co/workspace/My-Workspace~591e4136-2243-410d-8184-845605421989/collection/13972366-cca74bdd-662f-4324-8744-cdac8cac9d21?action=share&creator=13972366)
- Collection includes all endpoints with example requests
- Environment variables for different deployment stages
- Automated tests for critical user flows

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in `/docs`
- Contact the development team

---

Built with ❤️ by Team NS