require('dotenv').config();
const express = require('express');
const axios = require('axios');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { v4: uuidv4 } = require('uuid');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const DB_PATH = path.join(__dirname, 'db.json');

const usage = {};
const RATE_LIMITS = { free: 100, paid: 1000 };

function readDB() {
  try {
    const raw = fs.readFileSync(DB_PATH, 'utf-8');
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

function writeDB(data) {
  fs.writeFileSync(DB_PATH, JSON.stringify(data, null, 2));
}

function getKeys() {
  const db = readDB();
  return db.keys || {};
}

function setKeys(keys) {
  const db = readDB();
  db.keys = keys;
  writeDB(db);
}

function getUsage(apiKey) {
  const today = new Date().toISOString().slice(0, 10);
  if (!usage[apiKey]) usage[apiKey] = { date: today, count: 0 };
  if (usage[apiKey].date !== today) {
    usage[apiKey] = { date: today, count: 0 };
  }
  return usage[apiKey];
}

function incrementUsage(apiKey) {
  const u = getUsage(apiKey);
  u.count += 1;
}

function authMiddleware(req, res, next) {
  const apiKey = req.headers['x-api-key'];
  if (!apiKey) return res.status(401).json({ error: 'Missing x-api-key header' });
  const keys = getKeys();
  if (!keys[apiKey]) return res.status(403).json({ error: 'Invalid API key' });
  req.apiKey = apiKey;
  req.keyData = keys[apiKey];
  next();
}

function rateLimitMiddleware(req, res, next) {
  const u = getUsage(req.apiKey);
  const limit = RATE_LIMITS[req.keyData.tier] || RATE_LIMITS.free;
  if (u.count >= limit) {
    return res.status(429).json({ error: 'Rate limit exceeded', limit, tier: req.keyData.tier });
  }
  next();
}

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get('/', (req, res) => {
  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Weather API - Simple, Reliable, Affordable</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Inter', -apple-system, sans-serif; background: #0b1120; color: #e2e8f0; line-height: 1.6; }
    .container { max-width: 1100px; margin: 0 auto; padding: 0 24px; }
    nav { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; }
    nav .logo { font-size: 1.4rem; font-weight: 800; color: #fff; letter-spacing: -0.5px; }
    nav .logo span { color: #60a5fa; }
    nav .btn-outline { background: transparent; border: 1px solid #334155; color: #e2e8f0; padding: 8px 20px; border-radius: 8px; font-weight: 500; cursor: pointer; text-decoration: none; font-size: 0.9rem; transition: all .2s; }
    nav .btn-outline:hover { border-color: #60a5fa; color: #60a5fa; }
    .hero { text-align: center; padding: 80px 0 60px; }
    .hero h1 { font-size: 3.2rem; font-weight: 800; color: #fff; letter-spacing: -1px; line-height: 1.15; }
    .hero h1 span { background: linear-gradient(135deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero p { font-size: 1.2rem; color: #94a3b8; margin-top: 16px; max-width: 600px; margin-left: auto; margin-right: auto; }
    .hero .btn-primary { display: inline-block; margin-top: 32px; background: linear-gradient(135deg, #60a5fa, #7c3aed); color: #fff; padding: 14px 36px; border-radius: 10px; font-weight: 600; font-size: 1rem; text-decoration: none; transition: transform .2s, box-shadow .2s; box-shadow: 0 4px 20px rgba(96,165,250,.3); }
    .hero .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(96,165,250,.4); }
    .features { padding: 80px 0; }
    .features h2, .pricing h2, .quickstart h2 { text-align: center; font-size: 2rem; font-weight: 700; color: #fff; margin-bottom: 48px; }
    .features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }
    .feature-card { background: #131c31; border: 1px solid #1e293b; border-radius: 14px; padding: 32px; transition: border-color .2s; }
    .feature-card:hover { border-color: #334155; }
    .feature-card .icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 16px; }
    .feature-card h3 { font-size: 1.15rem; font-weight: 600; color: #fff; margin-bottom: 8px; }
    .feature-card p { color: #94a3b8; font-size: 0.9rem; }
    .pricing { padding: 80px 0; }
    .pricing-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 28px; max-width: 750px; margin: 0 auto; }
    .pricing-card { background: #131c31; border: 1px solid #1e293b; border-radius: 14px; padding: 36px; text-align: center; position: relative; }
    .pricing-card.featured { border-color: #60a5fa; background: linear-gradient(180deg, #131c31 0%, #1a2440 100%); }
    .pricing-card .badge { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #60a5fa, #7c3aed); color: #fff; font-size: 0.75rem; font-weight: 600; padding: 4px 16px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px; }
    .pricing-card h3 { font-size: 1.3rem; font-weight: 600; color: #fff; }
    .pricing-card .price { font-size: 2.8rem; font-weight: 800; color: #fff; margin: 16px 0 8px; }
    .pricing-card .price span { font-size: 1rem; font-weight: 400; color: #94a3b8; }
    .pricing-card .desc { color: #94a3b8; font-size: 0.9rem; margin-bottom: 20px; }
    .pricing-card ul { list-style: none; text-align: left; margin-bottom: 28px; }
    .pricing-card ul li { padding: 8px 0; color: #cbd5e1; font-size: 0.9rem; }
    .pricing-card ul li::before { content: "✓"; color: #60a5fa; font-weight: 700; margin-right: 10px; }
    .pricing-card .btn { display: block; padding: 12px; border-radius: 10px; font-weight: 600; text-decoration: none; transition: all .2s; }
    .pricing-card .btn-primary { background: linear-gradient(135deg, #60a5fa, #7c3aed); color: #fff; }
    .pricing-card .btn-primary:hover { opacity: 0.9; }
    .pricing-card .btn-secondary { background: #1e293b; color: #e2e8f0; }
    .pricing-card .btn-secondary:hover { background: #334155; }
    .quickstart { padding: 80px 0; }
    .quickstart code { display: block; background: #0d1728; border: 1px solid #1e293b; border-radius: 12px; padding: 24px; color: #a5f3fc; font-family: 'Fira Code', monospace; font-size: 0.85rem; overflow-x: auto; max-width: 650px; margin: 0 auto; white-space: pre; }
    .quickstart code .cm { color: #64748b; }
    .quickstart code .kw { color: #c084fc; }
    .quickstart code .str { color: #a5f3fc; }
    footer { border-top: 1px solid #1e293b; padding: 32px 0; text-align: center; color: #64748b; font-size: 0.85rem; }
    @media (max-width: 768px) {
      .features-grid { grid-template-columns: 1fr; }
      .pricing-grid { grid-template-columns: 1fr; }
      .hero h1 { font-size: 2.2rem; }
    }
  </style>
</head>
<body>
  <div class="container">
    <nav>
      <div class="logo"><span>☁️</span> WeatherAPI</div>
      <a href="https://github.com" class="btn-outline">Docs</a>
    </nav>

    <section class="hero">
      <h1>Weather API — <span>Simple, Reliable, Affordable</span></h1>
      <p>Real-time weather data for any city in the world. One API key, zero hassle. Built for developers.</p>
      <a href="#pricing" class="btn-primary">Get Started Free</a>
    </section>

    <section class="features">
      <h2>Why WeatherAPI?</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="icon" style="background:#1e3a5f;">⚡</div>
          <h3>Simple Integration</h3>
          <p>One endpoint, one header, one promise. Get weather data with a single GET request.</p>
        </div>
        <div class="feature-card">
          <div class="icon" style="background:#1e3a5f;">🔒</div>
          <h3>99.9% Uptime</h3>
          <p>Built on battle-tested infrastructure with automatic failover and caching.</p>
        </div>
        <div class="feature-card">
          <div class="icon" style="background:#1e3a5f;">📊</div>
          <h3>Usage Analytics</h3>
          <p>Track your API consumption in real-time. Transparent billing with no surprises.</p>
        </div>
      </div>
    </section>

    <section class="pricing" id="pricing">
      <h2>Pricing</h2>
      <div class="pricing-grid">
        <div class="pricing-card">
          <h3>Free</h3>
          <div class="price">$0<span>/mo</span></div>
          <div class="desc">Perfect for prototyping and small projects.</div>
          <ul>
            <li>100 requests per day</li>
            <li>Real-time weather data</li>
            <li>City-based lookup</li>
            <li>API key authentication</li>
          </ul>
          <a href="#" class="btn btn-secondary" onclick="event.preventDefault(); fetch('/api/register',{method:'POST'}).then(r=>r.json()).then(d=>alert('Your API key: '+d.api_key))">Get Free Key</a>
        </div>
        <div class="pricing-card featured">
          <div class="badge">Popular</div>
          <h3>Pro</h3>
          <div class="price">$9<span>/mo</span></div>
          <div class="desc">For production apps and higher traffic.</div>
          <ul>
            <li>1,000 requests per day</li>
            <li>Real-time weather data</li>
            <li>City-based lookup</li>
            <li>Priority support</li>
          </ul>
          <a href="#" class="btn btn-primary" onclick="event.preventDefault(); const key=prompt('Enter your API key:'); if(key){fetch('/api/upgrade',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({apiKey:key})}).then(r=>r.json()).then(d=>{if(d.url)window.location.href=d.url;else alert(d.error||'Error')})}">Upgrade to Pro</a>
        </div>
      </div>
    </section>

    <section class="quickstart">
      <h2>Quick Start</h2>
      <code><span class="cm"># Get your free API key first</span>
curl -X POST https://weather-api.example.com/api/register

<span class="cm"># Fetch weather for any city</span>
curl -H "x-api-key: your_api_key_here" \\
  "https://weather-api.example.com/api/weather?city=London"</code>
    </section>
  </div>

  <footer>
    <div class="container">
      &copy; 2026 WeatherAPI. Built with ☕ and ❤️ for developers everywhere.
    </div>
  </footer>
</body>
</html>`);
});

app.post('/api/register', (req, res) => {
  const apiKey = uuidv4();
  const keys = getKeys();
  keys[apiKey] = { tier: 'free', created: new Date().toISOString() };
  setKeys(keys);
  res.json({ api_key: apiKey, tier: 'free', message: 'You get 100 requests/day. Upgrade for more!' });
});

app.post('/api/upgrade', (req, res) => {
  const { apiKey } = req.body;
  if (!apiKey) return res.status(400).json({ error: 'apiKey is required' });
  const keys = getKeys();
  if (!keys[apiKey]) return res.status(404).json({ error: 'API key not found' });

  const session = stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    mode: 'subscription',
    line_items: [{
      price_data: {
        currency: 'usd',
        product_data: { name: 'Weather API - Pro Tier' },
        unit_amount: 900,
        recurring: { interval: 'month' },
      },
      quantity: 1,
    }],
    metadata: { apiKey },
    success_url: req.headers.origin + '/?upgrade=success',
    cancel_url: req.headers.origin + '/?upgrade=cancel',
  }).then(session => {
    res.json({ url: session.url });
  }).catch(err => {
    res.status(500).json({ error: err.message });
  });
});

app.post('/api/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    return res.status(400).json({ error: err.message });
  }

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const apiKey = session.metadata.apiKey;
    const keys = getKeys();
    if (keys[apiKey]) {
      keys[apiKey].tier = 'paid';
      keys[apiKey].stripeCustomerId = session.customer;
      setKeys(keys);
    }
  }

  res.json({ received: true });
});

app.get('/api/weather', authMiddleware, rateLimitMiddleware, async (req, res) => {
  const { city } = req.query;
  if (!city) return res.status(400).json({ error: 'Missing city query parameter' });

  try {
    const owmKey = process.env.OPENWEATHER_API_KEY;
    if (!owmKey || owmKey === 'your_openweathermap_api_key_here') {
      return res.status(500).json({ error: 'OPENWEATHER_API_KEY not configured on server' });
    }

    const response = await axios.get('https://api.openweathermap.org/data/2.5/weather', {
      params: { q: city, appid: owmKey, units: 'metric' },
    });

    incrementUsage(req.apiKey);

    const d = response.data;
    res.json({
      city: d.name,
      country: d.sys?.country,
      temperature: { current: d.main.temp, feels_like: d.main.feels_like, min: d.main.temp_min, max: d.main.temp_max },
      humidity: d.main.humidity,
      pressure: d.main.pressure,
      description: d.weather?.[0]?.description,
      icon: d.weather?.[0]?.icon,
      wind: { speed: d.wind.speed, deg: d.wind.deg },
      clouds: d.clouds?.all,
      visibility: d.visibility,
      sunrise: d.sys?.sunrise,
      sunset: d.sys?.sunset,
      requested_at: new Date().toISOString(),
    });
  } catch (err) {
    if (err.response?.status === 404) {
      return res.status(404).json({ error: 'City not found' });
    }
    if (err.response?.status === 401) {
      return res.status(500).json({ error: 'Invalid OpenWeatherMap API key on server' });
    }
    res.status(502).json({ error: 'Failed to fetch weather data', detail: err.message });
  }
});

app.get('/api/usage', authMiddleware, (req, res) => {
  const u = getUsage(req.apiKey);
  const limit = RATE_LIMITS[req.keyData.tier];
  res.json({
    api_key: req.apiKey,
    tier: req.keyData.tier,
    requests_today: u.count,
    daily_limit: limit,
    remaining: limit - u.count,
  });
});

app.listen(PORT, () => {
  console.log(`Weather API server running on http://localhost:${PORT}`);
});