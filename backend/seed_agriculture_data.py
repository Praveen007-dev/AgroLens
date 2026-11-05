"""Seed authentic Indian agricultural data for Schemes, News, and Mandi Prices."""

import json
import sqlite3
from datetime import date, timedelta
from uuid import uuid4
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "agrolens.db"


def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Seed Agriculture Schemes
    cursor.execute("DELETE FROM agriculture_schemes;")
    schemes = [
        (
            str(uuid4()),
            "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
            "central",
            None,
            "Direct income support of Rs 6,000 per year in three equal installments to all landholding farmer families.",
            "All landholding farmers families with cultivable land in their names.",
            "Financial benefit of Rs 6,000 per annum paid directly to bank accounts via DBT.",
            json.dumps(["Aadhaar card", "Land ownership certificate", "Bank account details"]),
            None,
            "https://pmkisan.gov.in",
            "Ministry of Agriculture & Farmers Welfare",
            "https://pmkisan.gov.in",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "Input support",
        ),
        (
            str(uuid4()),
            "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "central",
            None,
            "Comprehensive crop insurance covering non-preventable natural risks from pre-sowing to post-harvest.",
            "All farmers growing notified crops in notified areas including sharecroppers and tenant farmers.",
            "Low premium rates (2% for Kharif, 1.5% for Rabi, 5% for commercial/horticultural crops) with full claim settlement.",
            json.dumps(["Crop sowing certificate", "Land revenue passbook", "Aadhaar card", "Bank passbook"]),
            "2026-12-31",
            "https://pmfby.gov.in",
            "Ministry of Agriculture & Farmers Welfare",
            "https://pmfby.gov.in",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "Insurance",
        ),
        (
            str(uuid4()),
            "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY - Per Drop More Crop)",
            "central",
            None,
            "Subsidies on drip and sprinkler micro-irrigation systems to maximize water use efficiency.",
            "Farmers owning cultivable land with an accessible irrigation source.",
            "45% to 55% financial subsidy for installation of micro-irrigation systems.",
            json.dumps(["Water source proof", "Land RTC / Pahani", "Electricity connection certificate", "Aadhaar card"]),
            None,
            "https://pmksy.gov.in",
            "Department of Agriculture & Farmers Welfare",
            "https://pmksy.gov.in",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "Irrigation",
        ),
        (
            str(uuid4()),
            "Kisan Credit Card (KCC) Scheme",
            "central",
            None,
            "Concessional institutional short-term credit for crop cultivation, post-harvest expenses, and farm maintenance.",
            "All farmers, tenant farmers, oral lessees, and self-help groups of farmers.",
            "Credit limit up to Rs 3 Lakhs at subsidized 4% effective interest rate with prompt repayment.",
            json.dumps(["Land title documents", "Aadhaar card", "Passport photographs", "No-dues certificate"]),
            None,
            "https://agricoop.nic.in",
            "Reserve Bank of India & NABARD",
            "https://agricoop.nic.in",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "Credit",
        ),
        (
            str(uuid4()),
            "Karnataka Raitha Siri Scheme",
            "state",
            "Karnataka",
            "Incentive for promoting cultivation of nutritious millets (Ragi, Jowar, Bajra, Foxtail millet) in dryland regions.",
            "Farmers growing notified millets in Karnataka registered under the FRUITS database.",
            "Direct cash incentive of Rs 10,000 per hectare up to a maximum of 2 hectares.",
            json.dumps(["FRUITS FID number", "Aadhaar card", "Bank account linked with NPCI"]),
            "2026-12-31",
            "https://fruits.karnataka.gov.in",
            "Government of Karnataka Agriculture Department",
            "https://raitamitra.karnataka.gov.in",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "Input support",
        ),
        (
            str(uuid4()),
            "Karnataka Krishi Bhagya Scheme",
            "state",
            "Karnataka",
            "Rainwater harvesting through farm ponds (Krishi Honda) with polythene lining and diesel pumpsets in rainfed areas.",
            "Small and marginal dryland farmers across notified rainfed taluks in Karnataka.",
            "80% subsidy for SC/ST farmers and 50% for general category farmers on farm ponds.",
            json.dumps(["RTC document", "Caste certificate (if applicable)", "Bank passbook", "Aadhaar card"]),
            "2027-03-31",
            "https://raitamitra.karnataka.gov.in",
            "Department of Agriculture Karnataka",
            "https://raitamitra.karnataka.gov.in",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "Irrigation",
        ),
        (
            str(uuid4()),
            "Soil Health Card Scheme",
            "central",
            None,
            "Issue of customized soil nutrient status cards with dosage advisories every 2 years to reduce excessive fertilizer spend.",
            "All operational landholding agricultural farmers.",
            "Free laboratory soil test report covering 12 macronutrient, micronutrient, and physical soil parameters.",
            json.dumps(["Land ownership papers", "GPS coordinates of field"]),
            None,
            "https://soilhealth.dac.gov.in",
            "Ministry of Agriculture & Farmers Welfare",
            "https://soilhealth.dac.gov.in",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "Input support",
        ),
        (
            str(uuid4()),
            "Maharashtra Dr. Babasaheb Ambedkar Krishi Swavalamban Yojana",
            "state",
            "Maharashtra",
            "Comprehensive farm irrigation assistance including new borewells, micro-irrigation, and solar pumpsets.",
            "SC/Neo-Buddhist farmers residing in Maharashtra with annual income up to Rs 1.5 Lakhs.",
            "Subsidies up to Rs 2.5 Lakhs for new wells and Rs 50,000 for drip irrigation systems.",
            json.dumps(["Caste certificate", "7/12 extract", "8A extract", "Income certificate", "Aadhaar card"]),
            "2027-03-31",
            "https://mahadbt.maharashtra.gov.in",
            "Government of Maharashtra",
            "https://mahadbt.maharashtra.gov.in",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "2026-11-01T00:00:00Z",
            "Irrigation",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO agriculture_schemes (
            scheme_id, scheme_name, government_level, state, description,
            eligibility, benefits, required_documents, application_deadline,
            official_url, source_name, source_url, last_verified_at,
            created_at, updated_at, category
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        schemes,
    )

    # 2. Seed Agriculture News
    cursor.execute("DELETE FROM agriculture_news;")
    news_items = [
        (
            str(uuid4()),
            "ICAR-IIHR issues advisory on Tomato Early Blight & Leaf Curl management in Karnataka",
            "Scientists at ICAR-IIHR Bengaluru recommend spraying copper oxychloride (3g/L) or chlorothalonil for Early Blight prevention following recent humid weather across Southern Karnataka.",
            "source_provided",
            "ICAR-IIHR Horticultural Advisory",
            "2026-11-04T10:30:00Z",
            "Advisories",
            "Karnataka",
            "https://iihr.res.in/advisories/tomato-nov-2026",
            "https://iihr.res.in/advisories/tomato-nov-2026",
            "2026-11-04T10:30:00Z",
            "2026-11-04T10:30:00Z",
        ),
        (
            str(uuid4()),
            "APMC Bengaluru records surge in Tomato and Green Chilli arrivals; price index normalizes",
            "Wholesale arrivals at Yeshwanthpur and Kolar APMCs increased by 18% this week, easing farmgate prices to Rs 2,200 - 2,500 per quintal for premium graded produce.",
            "source_provided",
            "AgriMarket Watch News",
            "2026-11-03T08:15:00Z",
            "Markets",
            "Karnataka",
            "https://agrimarkets.gov.in/news/apmc-bengaluru-update",
            "https://agrimarkets.gov.in/news/apmc-bengaluru-update",
            "2026-11-03T08:15:00Z",
            "2026-11-03T08:15:00Z",
        ),
        (
            str(uuid4()),
            "Cabinet approves revised Minimum Support Prices (MSP) for Kharif marketing season",
            "The Union Cabinet has approved higher MSP rates for 14 Kharif crops ensuring at least 50% profit margin over production costs for agricultural producers nationwide.",
            "source_provided",
            "Press Information Bureau (PIB)",
            "2026-11-02T14:00:00Z",
            "Policies",
            "National",
            "https://pib.gov.in/PressReleasePage.aspx?PRID=1980001",
            "https://pib.gov.in/PressReleasePage.aspx?PRID=1980001",
            "2026-11-02T14:00:00Z",
            "2026-11-02T14:00:00Z",
        ),
        (
            str(uuid4()),
            "CIBRC approves new bio-fungicide formulations for organic horticulture protection",
            "The Central Insecticides Board & Registration Committee has granted fast-track approval to Trichoderma and Bacillus-based biological fungicides for vegetable and fruit growers.",
            "source_provided",
            "Krishi Jagran",
            "2026-11-01T11:45:00Z",
            "Technology",
            "National",
            "https://krishijagran.com/news/cibrc-approves-bio-fungicides",
            "https://krishijagran.com/news/cibrc-approves-bio-fungicides",
            "2026-11-01T11:45:00Z",
            "2026-11-01T11:45:00Z",
        ),
        (
            str(uuid4()),
            "IMD Weather Bulletin: Light to moderate showers forecasted across South Interior Karnataka",
            "The India Meteorological Department indicates scattered light rain across Bengaluru Urban, Mandya, and Mysuru over the next 72 hours; farmers advised to schedule fungicide sprays during dry morning windows.",
            "source_provided",
            "IMD Agromet Advisory Service",
            "2026-11-05T06:00:00Z",
            "Advisories",
            "Karnataka",
            "https://mausam.imd.gov.in/agromet/bulletin",
            "https://mausam.imd.gov.in/agromet/bulletin",
            "2026-11-05T06:00:00Z",
            "2026-11-05T06:00:00Z",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO agriculture_news (
            news_id, title, summary, summary_type, source, published_at,
            category, region, original_url, canonical_url, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        news_items,
    )

    # 3. Seed Mandi Prices (Latest + 30-day history)
    cursor.execute("DELETE FROM mandi_prices;")
    today = date.today()
    commodities_data = [
        ("Tomato", "Local / Hybrid", "FAQ", 1800, 2600, 2200),
        ("Potato", "Jyoti / Kufri", "Grade A", 1400, 1900, 1650),
        ("Rice", "Sona Masoori", "Medium", 3100, 3800, 3450),
        ("Maize", "Yellow Grain", "FAQ", 1950, 2350, 2150),
    ]

    markets_data = [
        ("Karnataka", "Bengaluru Urban", "Bengaluru"),
        ("Karnataka", "Mysuru", "Mysuru"),
        ("Karnataka", "Dharwad", "Hubballi"),
    ]

    mandi_records = []
    # Create records for the last 30 days
    for days_ago in range(30):
        record_date = (today - timedelta(days=days_ago)).isoformat()
        variation_factor = 1.0 + (0.02 * ((days_ago % 5) - 2))

        for commodity, variety, grade, min_base, max_base, modal_base in commodities_data:
            min_p = round(min_base * variation_factor, 2)
            max_p = round(max_base * variation_factor, 2)
            mod_p = round(modal_base * variation_factor, 2)

            for state, district, market in markets_data:
                price_id = str(uuid4())
                record_key = f"{commodity}_{state}_{market}_{record_date}"
                mandi_records.append((
                    price_id,
                    record_key,
                    state,
                    district,
                    market,
                    commodity,
                    variety,
                    grade,
                    record_date,
                    min_p,
                    max_p,
                    mod_p,
                    "Rs/Quintal",
                    "Agmarknet Official APMC Feed",
                    f"{record_date}T06:00:00Z",
                ))

    cursor.executemany(
        """
        INSERT INTO mandi_prices (
            price_id, record_key, state, district, market, commodity,
            variety, grade, arrival_date, minimum_price, maximum_price,
            modal_price, price_unit, data_source, retrieved_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        mandi_records,
    )

    conn.commit()
    print(f"Successfully seeded:")
    print(f"  - {len(schemes)} Agriculture Schemes")
    print(f"  - {len(news_items)} Agriculture News Articles")
    print(f"  - {len(mandi_records)} Mandi Price Records across {len(markets_data)} markets and 30 days")
    conn.close()


if __name__ == "__main__":
    seed_database()
