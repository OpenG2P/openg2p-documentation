# React/Next.js Project Structure

## **Overview**

This document outlines a modern, scalable folder structure for React/Next.js applications. The structure follows **feature-first architecture** principles, promoting maintainability, scalability, and team collaboration.

## **Core Architecture Principles**

### 1. **Feature-First Design**

* Group related functionality together
* Each feature is self-contained
* Clear separation of concerns

### 2. **Separation of Concerns**

* UI components vs business logic
* Shared utilities vs feature-specific code
* Configuration vs implementation

### 3. **Scalability**

* Easy to add new features
* Consistent organization patterns
* Team-friendly structure

***

## **Root Level Structure**

```
src/
├── app/                    # Next.js App Router
├── components/             # Shared UI Components
├── features/               # Feature-Based Modules
├── shared/                 # Shared Utilities & Services
├── context/                # React Context Providers
├── i18n/                   # Internationalization
├── commons/                # Global Styles
└── middleware.ts           # Next.js Middleware
```

***

## **Detailed Folder Explanations**

### **`app/` - Next.js App Router**

**Purpose:** Next.js 13+ App Router for routing and pages

```
app/
├── [locale]/               # Internationalization routing
│   ├── feature1/           # Feature-specific routes
│   ├── feature2/           # Another feature's routes
│   └── layout.tsx          # Layout for this route group
├── layout.tsx              # Root layout
├── page.tsx                # Home page
└── not-found.tsx           # 404 error page
```

**Key Concepts:**

* Each folder represents a route
* `page.tsx` = route component
* `layout.tsx` = layout wrapper
* `[locale]` = dynamic routing for i18n

***

### **`components/` - Shared UI Components**

**Purpose:** Reusable components used across the application

```
components/
├── ui/                     # Basic UI Components
│   ├── Button.tsx          # Reusable button
│   ├── Input.tsx           # Form input
│   ├── Modal.tsx           # Modal dialog
│   └── index.ts            # Clean exports
├── layout/                 # Layout Components
│   ├── Header.tsx          # Top navigation
│   ├── Sidebar.tsx         # Side navigation
│   └── index.ts            # Clean exports
├── shared/                 # Common Components
│   ├── Loading.tsx         # Loading states
│   ├── Error.tsx           # Error display
│   └── index.ts            # Clean exports
└── index.ts                # Main export file
```

**Component Categories:**

* **UI Components:** Basic, styleable primitives
* **Layout Components:** Navigation and structure
* **Shared Components:** Common functionality

***

### **`features/` - Feature-Based Modules**

**Purpose:** Self-contained business logic modules

```
features/
├── feature-name/           # Individual feature
│   ├── components/         # Feature-specific components
│   ├── hooks/              # Custom hooks
│   ├── services/           # API calls
│   ├── types/              # TypeScript types
│   ├── utils/              # Feature utilities
│   └── index.ts            # Feature exports
└── another-feature/        # Another feature
    └── ...                 # Same structure
```

**Feature Structure:**

* **`components/`** - Feature-specific UI components
* **`hooks/`** - Custom React hooks for logic
* **`services/`** - API calls and external integrations
* **`types/`** - TypeScript interfaces and types
* **`utils/`** - Feature-specific utility functions
* **`index.ts`** - Clean exports for the feature

***

### **`shared/` - Shared Utilities**

**Purpose:** Code used across multiple features

```
shared/
├── constants/              # App Constants
│   ├── api.ts              # API endpoints
│   ├── config.ts           # Configuration
│   └── index.ts            # Clean exports
├── services/               # Shared Services
│   ├── api.ts              # API service
│   ├── storage.ts          # Local storage
│   └── index.ts            # Clean exports
├── types/                  # Shared Types
│   ├── common.ts           # Common interfaces
│   ├── api.ts              # API types
│   └── index.ts            # Clean exports
├── utils/                  # Utility Functions
│   ├── helpers.ts          # Helper functions
│   ├── validation.ts       # Validation logic
│   └── index.ts            # Clean exports
└── index.ts                # Main export file
```

**Shared Categories:**

* **Constants:** Configuration values, API endpoints
* **Services:** External API integrations, storage
* **Types:** Shared TypeScript interfaces
* **Utils:** Pure functions and helpers

***

### **`context/` - React Context**

**Purpose:** Global state management

```
context/
├── global.tsx              # Global app state
├── theme.tsx               # Theme context
└── index.ts                # Context exports
```

**Usage:**

* Global app state (user, auth, theme)
* Avoid prop drilling
* Shared state across components

***

### **`i18n/` - Internationalization**

**Purpose:** Multi-language support

```
i18n/
├── navigation.ts           # i18n routing
├── request.ts              # Request handling
├── routing.ts              # Route configuration
└── index.ts                # i18n exports
```

**Features:**

* Multi-language routing
* Translation management
* Locale-specific content

***

### **`commons/` - Global Styles**

**Purpose:** Application-wide styling

```
commons/
├── globals.css             # Global CSS
├── variables.css           # CSS variables
└── index.ts                # Style exports
```

**Contents:**

* Global CSS styles
* CSS variables
* Tailwind imports
* Base styles and resets

***

### **`middleware.ts` - Next.js Middleware**

**Purpose:** Request/response interception and API proxying

**Key Features:**

* **API Proxy to FastAPI Backend**: Automatically routes `/api/*` requests to Python FastAPI
* **Internationalization**: Handles locale routing (`/en/`, `/fr/`, `/tl/`)
* **Header Management**: Forwards authentication headers (JWT tokens)
* **CORS Handling**: Development-friendly CORS configuration
* **Error Handling**: Graceful fallbacks for backend connection issues

**Configuration:**

```typescript
// Environment variables needed:
NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000
NEXT_PUBLIC_FASTAPI_API_PREFIX=/api/v1
NODE_ENV=development
```

**How It Works:**

```typescript
// Frontend API call:
fetch('/api/beneficiaries')

// Middleware transforms to:
// http://localhost:8000/api/v1/beneficiaries

// All HTTP methods supported:
// GET, POST, PUT, DELETE, OPTIONS
```

**Common Uses:**

* API request proxying to FastAPI backend
* Authentication header forwarding
* i18n routing and locale handling
* CORS management for development
* Static file optimization

***

## **API Integration Patterns**

### **Frontend to FastAPI Communication**

```typescript
// All API calls automatically proxied through middleware
const response = await fetch('/api/beneficiaries', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer your-jwt-token',
    'Content-Type': 'application/json'
  }
});

// Automatically becomes:
// GET http://localhost:8000/api/v1/beneficiaries
```

### **Service Layer Example**

```typescript
// src/shared/services/api.ts
const API_BASE = '/api'; // Proxied to FastAPI

export const apiService = {
  async getBeneficiaries() {
    const response = await fetch(`${API_BASE}/beneficiaries`);
    return response.json();
  },
  
  async login(credentials: LoginCredentials) {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    return response.json();
  }
};
```

### **React Hook Integration**

```typescript
// src/features/beneficiaries/hooks/useBeneficiaries.ts
import { useState, useEffect } from 'react';
import { apiService } from '@/shared/services/api';

export const useBeneficiaries = () => {
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBeneficiaries = async () => {
      try {
        const data = await apiService.getBeneficiaries();
        setBeneficiaries(data);
      } catch (error) {
        console.error('Failed to fetch beneficiaries:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBeneficiaries();
  }, []);

  return { beneficiaries, loading };
};
```

***

## **Import Patterns**

### **Recommended Import Structure**

```typescript
// Feature components - Direct imports
import { ComponentName } from '@/features/feature-name';

// Shared components - From components
import { Button, Loading } from '@/components';

// Shared utilities - From shared
import { apiService, constants } from '@/shared';

// Context - Direct import
import { useGlobalContext } from '@/context/global';
```

### **Avoid These Patterns**

```typescript
// Don't re-export everything through a central barrel
import { FeatureComponent } from '@/components'; // ❌

// Don't mix feature and shared components
import { Button, FeatureComponent } from '@/components'; // ❌
```

***

## **Benefits of This Structure**

### **Maintainability**

* Easy to find related code
* Clear separation of concerns
* Consistent organization

### **Scalability**

* Easy to add new features
* No circular dependencies
* Modular architecture

### **Team Collaboration**

* Different developers can work on different features
* Clear ownership boundaries
* Reduced merge conflicts

### **Performance**

* Better tree shaking
* Lazy loading opportunities
* Optimized bundle splitting

***

## **Best Practices**

### 1. **Feature Isolation**

* Keep feature code self-contained
* Minimize cross-feature dependencies
* Use shared utilities for common functionality

### 2. **Clean Exports**

* Use `index.ts` files for clean exports
* Avoid deep import paths
* Group related exports

### 3. **Consistent Naming**

* Use singular names for features
* Follow consistent file naming
* Use descriptive component names

### 4. **Type Safety**

* Define types in feature-specific folders
* Use shared types for common interfaces
* Export types from index files

***

## **Configuration Files**

### **Environment Variables (`.env.local`)**

```bash
# FastAPI Backend Configuration
NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000
NEXT_PUBLIC_FASTAPI_API_PREFIX=/api/v1

# Strapi CMS Configuration (if using)
NEXT_PUBLIC_STRAPI_URL=http://localhost:1337
STRAPI_API_TOKEN=your_strapi_token_here

# Next.js Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_nextauth_secret_here

# Development/Production Environment
NODE_ENV=development
```

### **`tailwind.config.ts`**

```typescript
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/features/**/*.{js,ts,jsx,tsx,mdx}',
    './src/shared/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/commons/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Design System Colors
        primary: { /* ... */ },
        secondary: { /* ... */ },
        success: { /* ... */ },
        warning: { /* ... */ },
        error: { /* ... */ },
        neutral: { /* ... */ },
      },
      // ... other theme extensions
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### **`tsconfig.json`**

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/features/*": ["./src/features/*"],
      "@/shared/*": ["./src/shared/*"],
      "@/context/*": ["./src/context/*"],
      "@/i18n/*": ["./src/i18n/*"],
      "@/commons/*": ["./src/commons/*"]
    }
  }
}
```

***

## **Additional Resources**

* [Next.js App Router Documentation](https://nextjs.org/docs/app)
* [React Context API](https://react.dev/reference/react/useContext)
* [TypeScript Path Mapping](https://www.typescriptlang.org/docs/handbook/module-resolution.html#path-mapping)
* [Tailwind CSS Configuration](https://tailwindcss.com/docs/configuration)
