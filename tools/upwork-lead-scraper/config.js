/**
 * Wood Fired Designs - Upwork lead scraper config.
 *
 * Target: ecommerce management and brand identity work with serious budgets and
 * the shape of a long-term retainer. Posts almost never say "retainer" out loud,
 * so retainer potential is inferred from proxy signals - duration, repeat-hire
 * history, client spend, ongoing language, and category (email design and store
 * management are structurally recurring; a one-off logo is not).
 */

/**
 * HARD GATES. Applied before scoring. A job that fails any of these is dropped
 * and never reaches the digest, no matter how well it reads. This is the
 * "serious budgets only" filter - tighten it, don't apologize for it.
 */
export const gates = {
  requirePaymentVerified: true,
  minFixedBudget: 2000,
  minHourlyRate: 45,
  // Search cards often omit the budget entirely. Keep those - enrichment usually
  // recovers it. Set false to be ruthless at the cost of missing real jobs.
  allowUnknownBudget: true,
  // Client lifetime spend floor. 0 = off. Set to 5000 once volume is healthy.
  minClientSpend: 0,
  // Drop anything already this crowded. 0 = off.
  maxProposals: 0,
};

export const searches = [
  // --- Ecommerce management: structurally ongoing work ---
  {
    id: 'shopify-store-management',
    q: 'Shopify store management ongoing',
    pages: 2,
    filters: { paymentVerified: true, fixedMin: 2000, hourlyMin: 45, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'ecommerce-manager',
    q: 'ecommerce manager brand',
    pages: 2,
    filters: { paymentVerified: true, fixedMin: 2000, hourlyMin: 45, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'klaviyo-email-design',
    q: 'Klaviyo email design ecommerce',
    pages: 1,
    filters: { paymentVerified: true, fixedMin: 2000, hourlyMin: 45, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'shopify-cro-product-pages',
    q: 'Shopify product page design conversion',
    pages: 1,
    filters: { paymentVerified: true, fixedMin: 2500, hourlyMin: 50, tiers: ['intermediate', 'expert'] },
  },

  // --- Brand identity and strategy at real budgets ---
  {
    id: 'brand-identity',
    q: 'brand identity designer',
    pages: 2,
    filters: { paymentVerified: true, fixedMin: 3000, hourlyMin: 50, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'brand-strategist',
    q: 'brand strategist positioning',
    pages: 1,
    filters: { paymentVerified: true, fixedMin: 3000, hourlyMin: 55, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'dtc-brand-designer',
    q: 'DTC brand designer ecommerce',
    pages: 2,
    filters: { paymentVerified: true, fixedMin: 2500, hourlyMin: 50, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'rebrand',
    q: 'rebrand brand refresh company',
    pages: 1,
    filters: { paymentVerified: true, fixedMin: 3000, hourlyMin: 55, tiers: ['intermediate', 'expert'] },
  },

  // --- Explicitly ongoing / partner-shaped ---
  {
    id: 'ongoing-design-partner',
    q: 'ongoing design support brand',
    pages: 2,
    filters: { paymentVerified: true, fixedMin: 2000, hourlyMin: 50, tiers: ['intermediate', 'expert'] },
  },
  {
    id: 'creative-director-part-time',
    q: 'part time creative director brand',
    pages: 1,
    filters: { paymentVerified: true, fixedMin: 2500, hourlyMin: 60, tiers: ['expert'] },
  },
];

export const scoring = {
  // Calibrated against the gates above. A gated-in job starts around 40.
  minScore: 60,
  priorityScore: 100,

  fixedBands: [
    { min: 15000, points: 34 },
    { min: 8000, points: 30 },
    { min: 5000, points: 26 },
    { min: 3000, points: 20 },
    { min: 2000, points: 12 },
    { min: 0, points: 0 },
  ],
  hourlyBands: [
    { min: 100, points: 34 },
    { min: 75, points: 30 },
    { min: 60, points: 24 },
    { min: 45, points: 14 },
    { min: 0, points: 0 },
  ],

  positive: [
    // Ecommerce management core
    { match: ['store management', 'manage our shopify', 'manage the store', 'store manager', 'ecommerce manager'], points: 20 },
    { match: ['shopify', 'ecommerce', 'e-commerce', 'dtc', 'd2c'], points: 12 },
    { match: ['klaviyo', 'email design', 'email marketing design', 'lifecycle'], points: 12 },
    { match: ['product page', 'pdp', 'collection page', 'conversion rate', 'cro'], points: 10 },
    { match: ['merchandising', 'product launch', 'seasonal campaign', 'new collection'], points: 10 },

    // Brand identity and strategy
    { match: ['brand identity', 'visual identity', 'identity system', 'brand system'], points: 20 },
    { match: ['brand strategy', 'brand strategist', 'positioning', 'brand architecture'], points: 18 },
    { match: ['rebrand', 'brand refresh', 'brand overhaul', 'brand evolution'], points: 14 },
    { match: ['brand guidelines', 'style guide', 'brand book', 'design system'], points: 10 },
    { match: ['packaging', 'label design', 'unboxing'], points: 8 },

    // Build capability that pairs with the brand work
    { match: ['framer'], points: 12 },
    { match: ['website redesign', 'web design', 'landing page'], points: 8 },

    // Seriousness tells
    { match: ['creative director', 'art direction', 'design lead'], points: 14 },
    { match: ['funded', 'series a', 'venture backed', 'scaling', '7 figure', 'eight figure', '8 figure'], points: 14 },
    { match: ['agency', 'in-house team', 'marketing team', 'our team'], points: 6 },
  ],

  negative: [
    { match: ['contest', 'design contest', 'spec work'], points: -50 },
    { match: ['data entry', 'virtual assistant', 'lead scraping', 'appointment setter', 'cold caller'], points: -50 },
    { match: ['low budget', 'tight budget', 'small budget', 'cheap', 'beginner welcome', 'students welcome', 'starter budget'], points: -40 },
    { match: ['seo', 'backlink', 'link building', 'guest post'], points: -30 },
    { match: ['just a logo', 'only a logo', 'simple logo', 'quick logo'], points: -30 },
    { match: ['canva'], points: -22 },
    { match: ['wordpress', 'elementor', 'wix ', 'godaddy'], points: -16 },
    { match: ['dropship', 'drop ship', 'print on demand', 'pod store'], points: -20 },
    { match: ['equity only', 'revenue share only', 'unpaid', 'portfolio piece'], points: -50 },
    { match: ['full time employee', 'full-time position', 'w2', '40 hours per week'], points: -12 },
  ],

  signals: {
    paymentVerified: 10,
    notPaymentVerified: -25,
    clientSpendBands: [
      { min: 250000, points: 24 },
      { min: 100000, points: 20 },
      { min: 25000, points: 14 },
      { min: 10000, points: 10 },
      { min: 1000, points: 4 },
      { min: 0, points: -6 }, // never hired anyone: unproven
    ],
    proposalBands: [
      { max: 5, points: 14 },
      { max: 10, points: 10 },
      { max: 20, points: 4 },
      { max: 50, points: -8 },
      { max: Infinity, points: -16 },
    ],
    ratingAtLeast45: 6,
    usClient: 8,
    freshnessBands: [
      { maxHours: 6, points: 12 },
      { maxHours: 24, points: 8 },
      { maxHours: 72, points: 3 },
      { maxHours: Infinity, points: 0 },
    ],
  },
};

/**
 * RETAINER POTENTIAL. Scored separately from fit so you can sort by it.
 * These are the proxies for "this turns into monthly work" when the post
 * never says the word retainer.
 */
export const retainer = {
  // Explicit or near-explicit ongoing language.
  phrases: [
    { match: ['retainer', 'monthly retainer', 'ongoing basis', 'monthly basis'], points: 40 },
    { match: ['long term', 'long-term', 'longterm', 'ongoing', 'continuous'], points: 26 },
    { match: ['first of many', 'more projects', 'additional projects', 'future projects', 'other brands'], points: 22 },
    { match: ['phase 1', 'phase one', 'start with', 'begin with', 'pilot project', 'trial project'], points: 20 },
    { match: ['grow with us', 'join our team', 'part of the team', 'embedded', 'dedicated designer'], points: 22 },
    { match: ['weekly', 'monthly', 'every month', 'per month', 'hours per week'], points: 14 },
    { match: ['maintain', 'maintenance', 'upkeep', 'manage our', 'day to day', 'day-to-day'], points: 20 },
  ],

  // Categories that are recurring by nature even when the post sounds one-off.
  categoryBoosts: [
    { match: ['store management', 'ecommerce manager', 'klaviyo', 'email design', 'lifecycle', 'campaign'], points: 24 },
    { match: ['product page', 'new collection', 'product launch', 'seasonal'], points: 16 },
    { match: ['social media design', 'ad creative', 'creative testing'], points: 14 },
    { match: ['brand guidelines', 'design system', 'brand system'], points: 10 },
  ],

  // Estimated contract duration -> months.
  durationBands: [
    { minMonths: 6, points: 30 },
    { minMonths: 3, points: 20 },
    { minMonths: 1, points: 8 },
    { minMonths: 0, points: -8 },
  ],

  // A client who hires repeatedly hires you repeatedly.
  clientHiresBands: [
    { min: 25, points: 24 },
    { min: 10, points: 18 },
    { min: 4, points: 12 },
    { min: 1, points: 4 },
    { min: 0, points: 0 },
  ],

  // Hourly contracts renew. Fixed-price contracts end.
  hourlyContract: 14,

  // Thresholds for the HIGH / MEDIUM / LOW label in the digest.
  highAt: 55,
  mediumAt: 28,
};

export const run = {
  // Full job pages carry duration, client hire count, and the complete
  // description - which is where nearly all retainer signal lives. Enrich
  // aggressively; the extra credits buy the thing you actually care about.
  enrichAboveScore: 60,
  maxEnrichPerRun: 20,
  delayMs: 1200,
};
