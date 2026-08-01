# Weather API — Micro-SaaS API Wrapper

A paid API wrapper around OpenWeatherMap with Stripe billing, rate limiting, and usage tracking.

## Features

- **API Key Authentication** — every request requires an `x-api-key` header
- **Rate Limiting** — 100 req/day free, 1,000 req/day paid
- **Usage Tracking** — in-memory counters with automatic daily reset
- **Stripe Integration** — monthly subscription via Stripe Checkout (test mode)
- **Landing Page** — built-in pricing page served at `/`

## Quick Start

```bash
# Install dependencies
npm install

# Copy and fill in your environment variables
cp .env.example .env
# Edit .env with your keys

# Start the server
npm start
```

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | Landing & pricing page |
| POST | `/api/register` | No | Get a free API key |
| POST | `/api/upgrade` | Yes | Create Stripe checkout session |
| GET | `/api/weather?city=London` | Yes | Fetch weather data |
| GET | `/api/usage` | Yes | View your usage stats |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENWEATHER_API_KEY` | Your key from [openweathermap.org](https://openweathermap.org/api) |
| `STRIPE_SECRET_KEY` | Stripe secret key (starts with `sk_test_`) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret (starts with `whsec_`) |
| `PORT` | Server port (default: 3000) |

## Deploy

Push to any Node.js host (Render, Railway, Fly.io, DigitalOcean App Platform). Set the environment variables in your hosting dashboard.

For Stripe webhooks in production, point your Stripe webhook endpoint to `https://your-domain.com/api/webhook`.

## License

MIT