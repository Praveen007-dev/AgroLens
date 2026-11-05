export const MANDI_MARKETS = [
  { id: "APMC_1", name: "Sirsi APMC", district: "Uttara Kannada", state: "Karnataka" },
  { id: "APMC_2", name: "Belagavi Main Market", district: "Belagavi", state: "Karnataka" },
  { id: "APMC_3", name: "Mandya Mandi", district: "Mandya", state: "Karnataka" },
  { id: "APMC_4", name: "Shimoga Central APMC", district: "Shivamogga", state: "Karnataka" },
  { id: "APMC_5", name: "Davanagere Grain Market", district: "Davanagere", state: "Karnataka" },
  { id: "APMC_6", name: "Vashi APMC Terminal", district: "Navi Mumbai", state: "Maharashtra" },
  { id: "APMC_7", name: "Lasalgaon Onion Mandi", district: "Nashik", state: "Maharashtra" },
  { id: "APMC_8", name: "Khanna Grain Market", district: "Ludhiana", state: "Punjab" },
  { id: "APMC_9", name: "Unjha Spices & Cumin Mandi", district: "Mehsana", state: "Gujarat" },
  { id: "APMC_10", name: "Guntur Mirchi Yard", district: "Guntur", state: "Andhra Pradesh" },
  { id: "APMC_11", name: "Koyambedu Wholesale Complex", district: "Chennai", state: "Tamil Nadu" },
  { id: "APMC_12", name: "Neemuch Garlic & Herbs Mandi", district: "Neemuch", state: "Madhya Pradesh" },
  { id: "APMC_13", name: "Karnal Basmati Rice Yard", district: "Karnal", state: "Haryana" },
  { id: "APMC_14", name: "Agra Potato & Grain Mandi", district: "Agra", state: "Uttar Pradesh" },
  { id: "APMC_15", name: "Azadpur APMC Central Hub", district: "North Delhi", state: "Delhi" }
];

const BASE_CROP_PRICES = {
  Tomato: { baseModal: 2250, baseMin: 1800, baseMax: 2600, unit: "₹ / Quintal" },
  Potato: { baseModal: 1750, baseMin: 1400, baseMax: 2100, unit: "₹ / Quintal" },
  Paddy:  { baseModal: 2320, baseMin: 2183, baseMax: 2450, unit: "₹ / Quintal" },
  Cotton: { baseModal: 7250, baseMin: 6800, baseMax: 7650, unit: "₹ / Quintal" },
  Corn:   { baseModal: 2150, baseMin: 1950, baseMax: 2300, unit: "₹ / Quintal" }
};

// Generates dynamic market price data when any center is clicked
export function getMarketPriceData(crop, market) {
  const cropConfig = BASE_CROP_PRICES[crop] || BASE_CROP_PRICES.Tomato;
  const marketName = market ? market.name : "Sirsi APMC";
  const marketDistrict = market ? market.district : "Uttara Kannada";
  const marketState = market ? market.state : "Karnataka";

  // Calculate distinct offset per market using string hash
  const hash = (marketName + crop).split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
  const offset = ((hash % 11) - 5) * 40; // Price difference between markets

  const modalPrice = cropConfig.baseModal + offset;
  const minPrice = cropConfig.baseMin + offset;
  const maxPrice = cropConfig.baseMax + offset;

  const dates = [
    { date: "29/10", type: "actual", delta: -120 },
    { date: "30/10", type: "actual", delta: -80 },
    { date: "31/10", type: "actual", delta: -40 },
    { date: "01/11", type: "actual", delta: -30 },
    { date: "02/11", type: "actual", delta: +30 },
    { date: "03/11", type: "actual", delta: +10 },
    { date: "04/11 (Today)", type: "actual", delta: 0 },
    { date: "05/11 (Est)", type: "forecast", delta: +40 },
    { date: "06/11 (Est)", type: "forecast", delta: +80 },
    { date: "07/11 (Est)", type: "forecast", delta: +120 },
    { date: "08/11 (Est)", type: "forecast", delta: +100 },
    { date: "09/11 (Est)", type: "forecast", delta: +70 }
  ];

  const historical = dates.map(d => ({
    date: d.date,
    type: d.type,
    modal: modalPrice + d.delta,
    min: minPrice + Math.round(d.delta * 0.8),
    max: maxPrice + Math.round(d.delta * 1.1)
  }));

  return {
    market: `${marketName} (${marketDistrict}, ${marketState})`,
    unit: cropConfig.unit,
    lastUpdated: "2026-11-04T08:00:00Z",
    source: `Agmarknet Daily Feed — ${marketName}`,
    minPrice,
    maxPrice,
    modalPrice,
    historical
  };
}