// Mandi Price Intelligence Data Model (ICAR / AGMARKNET Aligned)
export const MANDI_MARKETS = [
  { id: "APMC_SIRSI", name: "Sirsi APMC", district: "Uttara Kannada", state: "Karnataka" },
  { id: "APMC_BELAGAVI", name: "Belagavi Main Market", district: "Belagavi", state: "Karnataka" },
  { id: "APMC_MANDYA", name: "Mandya Mandi", district: "Mandya", state: "Karnataka" },
  { id: "APMC_SHIMOGA", name: "Shimoga Central APMC", district: "Shimoga", state: "Karnataka" },
  { id: "APMC_DAVANAGERE", name: "Davanagere Grain Market", district: "Davanagere", state: "Karnataka" }
];

export const COMMODITY_PRICES = {
  Tomato: {
    market: "Sirsi APMC",
    unit: "₹ / Quintal",
    lastUpdated: "2026-11-04T08:00:00Z",
    source: "Agmarknet APMC Daily Bulletin",
    minPrice: 1800,
    maxPrice: 2600,
    modalPrice: 2250,
    historical: [
      { date: "29/10", min: 1700, max: 2400, modal: 2100, type: "actual" },
      { date: "30/10", min: 1750, max: 2450, modal: 2150, type: "actual" },
      { date: "31/10", min: 1800, max: 2500, modal: 2200, type: "actual" },
      { date: "01/11", min: 1750, max: 2550, modal: 2200, type: "actual" },
      { date: "02/11", min: 1850, max: 2600, modal: 2300, type: "actual" },
      { date: "03/11", min: 1800, max: 2600, modal: 2250, type: "actual" },
      { date: "04/11 (Today)", min: 1800, max: 2600, modal: 2250, type: "actual" },
      // Distinct ML 5-Day Forecast
      { date: "05/11 (Est)", min: 1850, max: 2650, modal: 2300, type: "forecast" },
      { date: "06/11 (Est)", min: 1900, max: 2700, modal: 2350, type: "forecast" },
      { date: "07/11 (Est)", min: 1950, max: 2750, modal: 2400, type: "forecast" },
      { date: "08/11 (Est)", min: 1900, max: 2700, modal: 2380, type: "forecast" },
      { date: "09/11 (Est)", min: 1880, max: 2680, modal: 2340, type: "forecast" }
    ]
  },
  Potato: {
    market: "Belagavi Main Market",
    unit: "₹ / Quintal",
    lastUpdated: "2026-11-04T08:00:00Z",
    source: "Agmarknet APMC Daily Bulletin",
    minPrice: 1400,
    maxPrice: 2100,
    modalPrice: 1750,
    historical: [
      { date: "29/10", min: 1350, max: 2000, modal: 1700, type: "actual" },
      { date: "30/10", min: 1380, max: 2050, modal: 1720, type: "actual" },
      { date: "31/10", min: 1400, max: 2080, modal: 1740, type: "actual" },
      { date: "01/11", min: 1400, max: 2100, modal: 1750, type: "actual" },
      { date: "02/11", min: 1420, max: 2120, modal: 1760, type: "actual" },
      { date: "03/11", min: 1400, max: 2100, modal: 1750, type: "actual" },
      { date: "04/11 (Today)", min: 1400, max: 2100, modal: 1750, type: "actual" },
      { date: "05/11 (Est)", min: 1410, max: 2120, modal: 1770, type: "forecast" },
      { date: "06/11 (Est)", min: 1430, max: 2150, modal: 1790, type: "forecast" },
      { date: "07/11 (Est)", min: 1450, max: 2180, modal: 1810, type: "forecast" },
      { date: "08/11 (Est)", min: 1460, max: 2200, modal: 1830, type: "forecast" },
      { date: "09/11 (Est)", min: 1440, max: 2190, modal: 1820, type: "forecast" }
    ]
  },
  Paddy: {
    market: "Shimoga Central APMC",
    unit: "₹ / Quintal",
    lastUpdated: "2026-11-04T08:00:00Z",
    source: "Agmarknet APMC Daily Bulletin",
    minPrice: 2183,
    maxPrice: 2450,
    modalPrice: 2320,
    historical: [
      { date: "29/10", min: 2183, max: 2400, modal: 2290, type: "actual" },
      { date: "30/10", min: 2183, max: 2420, modal: 2300, type: "actual" },
      { date: "31/10", min: 2183, max: 2440, modal: 2310, type: "actual" },
      { date: "01/11", min: 2183, max: 2440, modal: 2310, type: "actual" },
      { date: "02/11", min: 2183, max: 2460, modal: 2330, type: "actual" },
      { date: "03/11", min: 2183, max: 2450, modal: 2320, type: "actual" },
      { date: "04/11 (Today)", min: 2183, max: 2450, modal: 2320, type: "actual" },
      { date: "05/11 (Est)", min: 2183, max: 2460, modal: 2330, type: "forecast" },
      { date: "06/11 (Est)", min: 2183, max: 2470, modal: 2340, type: "forecast" },
      { date: "07/11 (Est)", min: 2183, max: 2480, modal: 2350, type: "forecast" },
      { date: "08/11 (Est)", min: 2183, max: 2470, modal: 2340, type: "forecast" },
      { date: "09/11 (Est)", min: 2183, max: 2460, modal: 2330, type: "forecast" }
    ]
  },
  Cotton: {
    market: "Davanagere Grain Market",
    unit: "₹ / Quintal",
    lastUpdated: "2026-11-04T08:00:00Z",
    source: "Agmarknet APMC Daily Bulletin",
    minPrice: 6800,
    maxPrice: 7650,
    modalPrice: 7250,
    historical: [
      { date: "29/10", min: 6700, max: 7500, modal: 7100, type: "actual" },
      { date: "30/10", min: 6750, max: 7550, modal: 7180, type: "actual" },
      { date: "31/10", min: 6780, max: 7580, modal: 7200, type: "actual" },
      { date: "01/11", min: 6800, max: 7600, modal: 7220, type: "actual" },
      { date: "02/11", min: 6820, max: 7640, modal: 7260, type: "actual" },
      { date: "03/11", min: 6800, max: 7650, modal: 7250, type: "actual" },
      { date: "04/11 (Today)", min: 6800, max: 7650, modal: 7250, type: "actual" },
      { date: "05/11 (Est)", min: 6830, max: 7680, modal: 7280, type: "forecast" },
      { date: "06/11 (Est)", min: 6850, max: 7700, modal: 7300, type: "forecast" },
      { date: "07/11 (Est)", min: 6870, max: 7720, modal: 7320, type: "forecast" },
      { date: "08/11 (Est)", min: 6860, max: 7700, modal: 7310, type: "forecast" },
      { date: "09/11 (Est)", min: 6840, max: 7680, modal: 7290, type: "forecast" }
    ]
  },
  Corn: {
    market: "Davanagere Grain Market",
    unit: "₹ / Quintal",
    lastUpdated: "2026-11-04T08:00:00Z",
    source: "Agmarknet APMC Daily Bulletin",
    minPrice: 1950,
    maxPrice: 2300,
    modalPrice: 2150,
    historical: [
      { date: "29/10", min: 1900, max: 2250, modal: 2100, type: "actual" },
      { date: "30/10", min: 1920, max: 2260, modal: 2110, type: "actual" },
      { date: "31/10", min: 1930, max: 2280, modal: 2130, type: "actual" },
      { date: "01/11", min: 1940, max: 2290, modal: 2140, type: "actual" },
      { date: "02/11", min: 1960, max: 2310, modal: 2160, type: "actual" },
      { date: "03/11", min: 1950, max: 2300, modal: 2150, type: "actual" },
      { date: "04/11 (Today)", min: 1950, max: 2300, modal: 2150, type: "actual" },
      { date: "05/11 (Est)", min: 1960, max: 2320, modal: 2170, type: "forecast" },
      { date: "06/11 (Est)", min: 1970, max: 2330, modal: 2180, type: "forecast" },
      { date: "07/11 (Est)", min: 1980, max: 2340, modal: 2190, type: "forecast" },
      { date: "08/11 (Est)", min: 1970, max: 2330, modal: 2180, type: "forecast" },
      { date: "09/11 (Est)", min: 1960, max: 2310, modal: 2160, type: "forecast" }
    ]
  }
};