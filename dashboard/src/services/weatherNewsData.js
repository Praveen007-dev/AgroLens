export const REGIONAL_WEATHER_DATA = {
  "Uttara Kannada": {
    temp: 28,
    humidity: 78,
    rainfallForecast: "Moderate showers expected in 48h",
    windSpeed: "12 km/h",
    soilMoistureStatus: "Adequate (Field Capacity 82%)",
    riskSummary: {
      crop: "Paddy & Areca",
      level: "Medium",
      reason: "High humidity (>75%) coupled with moderate overcast elevates fungal Blast risk in lowland paddies."
    },
    advisoriesCount: 3
  },
  "Belagavi": {
    temp: 26,
    humidity: 62,
    rainfallForecast: "Dry clear weather",
    windSpeed: "9 km/h",
    soilMoistureStatus: "Optimum (68%)",
    riskSummary: {
      crop: "Potato & Sugarcane",
      level: "Low",
      reason: "Cool nights favorable for tuber bulking; monitor for early aphid vectors."
    },
    advisoriesCount: 2
  },
  "Mandya": {
    temp: 29,
    humidity: 65,
    rainfallForecast: "Scattered light drizzles",
    windSpeed: "10 km/h",
    soilMoistureStatus: "Normal (71%)",
    riskSummary: {
      crop: "Paddy & Tomato",
      level: "Low",
      reason: "Stable microclimate; standard preventive spraying schedule applies."
    },
    advisoriesCount: 1
  },
  "Shimoga": {
    temp: 27,
    humidity: 80,
    rainfallForecast: "Overcast with intermittent showers",
    windSpeed: "14 km/h",
    soilMoistureStatus: "High (89%)",
    riskSummary: {
      crop: "Paddy",
      level: "High",
      reason: "Extended leaf wetness index > 14 hrs increases Neck Blast and sheath blight potential."
    },
    advisoriesCount: 4
  },
  "Davanagere": {
    temp: 31,
    humidity: 55,
    rainfallForecast: "Dry and sunny",
    windSpeed: "8 km/h",
    soilMoistureStatus: "Dry (52% - irrigation recommended)",
    riskSummary: {
      crop: "Corn & Cotton",
      level: "Low",
      reason: "Low relative humidity suppresses foliar pathogens; monitor soil moisture levels."
    },
    advisoriesCount: 2
  }
};

export const AGRI_NEWS_SCHEMES = [
  {
    id: "news_1",
    type: "Scheme",
    title: "PM-KISAN Samman Nidhi — 19th Installment Crediting Verification",
    source: "Ministry of Agriculture & Farmers Welfare",
    date: "2026-11-02",
    summary: "e-KYC and land-record seeding mandatory for direct bank transfer of ₹2,000 seasonal benefit.",
    url: "https://pmkisan.gov.in"
  },
  {
    id: "news_2",
    type: "News",
    title: "Karnataka APMC Direct Procurement Modernization Initiative",
    source: "Karnataka State Agricultural Marketing Board",
    date: "2026-11-03",
    summary: "Unified electronic bidding expanded across regional mandis to reduce commission fees and speed up settlement.",
    url: "https://krishimaratavahini.kar.nic.in"
  },
  {
    id: "news_3",
    type: "Advisory",
    title: "ICAR-IIHR Rabi Vegetable Nursery Health & Bio-Shield Advisory",
    source: "ICAR-IIHR Bengaluru",
    date: "2026-11-04",
    summary: "Guidelines on microbial consortium seed coating to mitigate damping-off and root rot in solanaceous nurseries.",
    url: "https://iihr.icar.gov.in"
  }
];