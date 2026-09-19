/**
 * Wood Fired Designs - Upwork lead scraper config.
 * Edit this file to change what gets pulled and how leads are scored.
 */

export const searches = [
  {
    id: 'brand-identity',
    q: 'brand identity',
    pages: 2,
    filters: { paymentVerified: true, fixedMin: 1000, hourlyMin: 45, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'logo-and-website',
    q: 'logo and website design',
    pages: 2,
    filters: { paymentVerified: true, fixedMin: 1500, hourlyMin: 45, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'framer-website',
    q: 'Framer website',
    pages: 2,
    filters: { paymentVerified: true, fixedMin: 1000, hourlyMin: 50, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'shopify-design',
    q: 'Shopify website design',
    pages: 2,
    filters: { paymentVerified: true, fixedMin: 1500, hourlyMin: 50, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'packaging-design',
    q: 'packaging design',
    pages: 1,
    filters: { paymentVerified: true, fixedMin: 1000, hourlyMin: 45, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'landing-page',
    q: 'high converting landing page design',
    pages: 1,
    filters: { paymentVerified: true, fixedMin: 1000, hourlyMin: 50, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'rebrand',
    q: 'rebrand brand refresh',
    pages: 1,
    filters: { paymentVerified: true, fixedMin: 2000, hourlyMin: 50, tiers: ['intermediate', 'expert'] },
  },
];

export const scoring = {
  // Hard floor. Anything under this is dropped before it ever hits the digest.
  // Calibration: a decent-but-plain $2k website job lands around 55-65.
  // A $6k brand-identity-plus-Framer job with a verified, high-spend client lands 120+.
  minScore: 55,
  // Anything at or above this gets flagged "PRIORITY" in the digest.
  priorityScore: 95,

  // Budget bands (USD). Fixed-price budget or hourly max, whichever applies.
  fixedBands: [
    { min: 10000, points: 30 },
    { min: 5000, points: 26 },
    { min: 3000, points: 22 },
    { min: 1500, points: 16 },
    { min: 800, points: 8 },
    { min: 0, points: -10 },
  ],
  hourlyBands: [
    { min: 100, points: 30 },
    { min: 75, points: 26 },
    { min: 55, points: 20 },
    { min: 40, points: 12 },
    { min: 0, points: -10 },
  ],

  // Phrases in title/description that pull the score up.
  positive: [
    { match: ['brand identity', 'visual identity', 'identity system', 'brand system'], points: 18 },
    { match: ['rebrand', 'brand refresh', 'brand overhaul'], points: 14 },
    { match: ['framer'], points: 14 },
    { match: ['shopify', 'ecommerce', 'e-commerce'], points: 10 },
    { match: ['packaging', 'label design', 'box design'], points: 10 },
    { match: ['landing page', 'conversion', 'cro'], points: 8 },
    { match: ['brand guidelines', 'style guide', 'brand book'], points: 8 },
    { match: ['website redesign', 'web design', 'website design'], points: 8 },
    { match: ['long term', 'long-term', 'ongoing', 'retainer'], points: 12 },
    { match: ['logo and website', 'branding and website', 'brand and web'], points: 14 },
    { match: ['product photography', 'ai product photos', 'mockups'], points: 6 },
    { match: ['roofing', 'contractor', 'hvac', 'trades', 'construction'], points: 6 },
  ],

  // Phrases that kill or heavily discount a job.
  negative: [
    { match: ['contest', 'design contest', 'spec work'], points: -40 },
    { match: ['wordpress', 'elementor', 'wix '], points: -14 },
    { match: ['seo', 'backlink', 'link building'], points: -25 },
    { match: ['data entry', 'virtual assistant', 'lead scraping', 'appointment setter'], points: -45 },
    { match: ['low budget', 'tight budget', 'small budget', 'cheap', 'beginner welcome', 'students welcome'], points: -30 },
    { match: ['canva'], points: -18 },
    { match: ['urgent within 24 hours', 'need it today', 'asap today'], points: -10 },
    { match: ['full time employee', 'full-time position', '40 hours per week'], points: -15 },
  ],

  // Client-quality signals.
  signals: {
    paymentVerified: 12,
    notPaymentVerified: -20,
    clientSpendBands: [
      { min: 100000, points: 16 },
      { min: 25000, points: 12 },
      { min: 5000, points: 8 },
      { min: 1000, points: 4 },
      { min: 0, points: 0 },
    ],
    // Fewer proposals = more likely to get read.
    proposalBands: [
      { max: 5, points: 14 },
      { max: 10, points: 10 },
      { max: 20, points: 4 },
      { max: 50, points: -6 },
      { max: Infinity, points: -14 },
    ],
    ratingAtLeast45: 6,
    usClient: 6,
    // Posted within N hours -> points
    freshnessBands: [
      { maxHours: 6, points: 12 },
      { maxHours: 24, points: 8 },
      { maxHours: 72, points: 3 },
      { maxHours: Infinity, points: 0 },
    ],
  },
};

export const run = {
  // Pull full job detail pages for anything scoring this high (costs extra credits).
  enrichAboveScore: 65,
  maxEnrichPerRun: 12,
  // Pause between Firecrawl calls so you don't hammer the API.
  delayMs: 1200,
};
