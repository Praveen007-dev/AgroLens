class WeatherData {
  const WeatherData({
    required this.location,
    this.condition,
    this.temperatureC,
    this.rainfallMm,
    this.rainProbabilityPct,
    this.humidityPct,
    this.windSpeedKph,
    this.windDirection,
    this.advisory,
    this.forecast = const [],
  });

  final String? location;
  final String? condition;
  final double? temperatureC;
  final double? rainfallMm;
  final double? rainProbabilityPct;
  final double? humidityPct;
  final double? windSpeedKph;
  final String? windDirection;
  final String? advisory;
  final List<WeatherForecastDay> forecast;

  factory WeatherData.fromJson(Map<String, dynamic> json) {
    final forecast = _listOfMaps(json['forecast'])
        .map(WeatherForecastDay.fromJson)
        .toList(growable: false);
    return WeatherData(
      location: _string(json['location']),
      condition: _string(json['condition']),
      temperatureC: _number(json['temperature_c']),
      rainfallMm: _number(json['rainfall_mm']),
      rainProbabilityPct: _number(json['rain_probability_pct']),
      humidityPct: _number(json['humidity_pct']),
      windSpeedKph: _number(json['wind_speed_kph']),
      windDirection: _string(json['wind_direction']),
      advisory: _string(json['advisory']),
      forecast: forecast,
    );
  }
}

class WeatherForecastDay {
  const WeatherForecastDay({
    required this.date,
    this.condition,
    this.minTemperatureC,
    this.maxTemperatureC,
    this.rainfallMm,
    this.rainProbabilityPct,
    this.humidityPct,
    this.windSpeedKph,
  });

  final String? date;
  final String? condition;
  final double? minTemperatureC;
  final double? maxTemperatureC;
  final double? rainfallMm;
  final double? rainProbabilityPct;
  final double? humidityPct;
  final double? windSpeedKph;

  factory WeatherForecastDay.fromJson(Map<String, dynamic> json) {
    return WeatherForecastDay(
      date: _string(json['date']),
      condition: _string(json['condition']),
      minTemperatureC: _number(json['min_temperature_c']),
      maxTemperatureC: _number(json['max_temperature_c']),
      rainfallMm: _number(json['rainfall_mm']),
      rainProbabilityPct: _number(json['rain_probability_pct']),
      humidityPct: _number(json['humidity_pct']),
      windSpeedKph: _number(json['wind_speed_kph']),
    );
  }
}

class AgricultureScheme {
  const AgricultureScheme({
    required this.name,
    this.scope,
    this.state,
    this.category,
    this.description,
    this.eligibility,
    this.benefits,
    this.requiredDocuments,
    this.applicationDeadline,
    this.officialUrl,
  });

  final String? name;
  final String? scope;
  final String? state;
  final String? category;
  final String? description;
  final String? eligibility;
  final String? benefits;
  final List<String>? requiredDocuments;
  final String? applicationDeadline;
  final String? officialUrl;

  factory AgricultureScheme.fromJson(Map<String, dynamic> json) {
    return AgricultureScheme(
      name: _string(json['name'] ?? json['title']),
      scope: _string(json['scope']),
      state: _string(json['state']),
      category: _string(json['category']),
      description: _string(json['description']),
      eligibility: _string(json['eligibility']),
      benefits: _string(json['benefits']),
      requiredDocuments: _nullableStringList(json['required_documents']),
      applicationDeadline: _string(json['application_deadline']),
      officialUrl: _string(json['official_url']),
    );
  }
}

class AgricultureNewsArticle {
  const AgricultureNewsArticle({
    required this.title,
    this.summary,
    this.source,
    this.publishedAt,
    this.category,
    this.originalUrl,
  });

  final String? title;
  final String? summary;
  final String? source;
  final String? publishedAt;
  final String? category;
  final String? originalUrl;

  factory AgricultureNewsArticle.fromJson(Map<String, dynamic> json) {
    return AgricultureNewsArticle(
      title: _string(json['title']),
      summary: _string(json['summary']),
      source: _string(json['source']),
      publishedAt: _string(json['published_at']),
      category: _string(json['category']),
      originalUrl: _string(json['original_url']),
    );
  }
}

class MandiPrice {
  const MandiPrice({
    required this.commodity,
    required this.modalPrice,
    required this.unit,
    this.state,
    this.district,
    this.market,
    this.minPrice,
    this.maxPrice,
    this.currency,
    this.priceDate,
  });

  final String? commodity;
  final String? state;
  final String? district;
  final String? market;
  final double? minPrice;
  final double? modalPrice;
  final double? maxPrice;
  final String? currency;
  final String? unit;
  final String? priceDate;

  factory MandiPrice.fromJson(Map<String, dynamic> json) {
    return MandiPrice(
      commodity: _string(json['commodity']),
      state: _string(json['state']),
      district: _string(json['district']),
      market: _string(json['market']),
      minPrice: _number(json['min_price']),
      modalPrice: _number(json['modal_price']),
      maxPrice: _number(json['max_price']),
      currency: _string(json['currency']),
      unit: _string(json['unit']),
      priceDate: _string(json['price_date']),
    );
  }
}

class MandiPricePoint {
  const MandiPricePoint({
    required this.date,
    required this.modalPrice,
    this.currency,
    this.unit,
  });

  final String? date;
  final double? modalPrice;
  final String? currency;
  final String? unit;

  factory MandiPricePoint.fromJson(Map<String, dynamic> json) {
    return MandiPricePoint(
      date: _string(json['date']),
      modalPrice: _number(json['modal_price']),
      currency: _string(json['currency']),
      unit: _string(json['unit']),
    );
  }
}

class MandiPriceForecast {
  const MandiPriceForecast({
    required this.date,
    required this.predictedModalPrice,
    this.currency,
    this.unit,
  });

  final String? date;
  final double? predictedModalPrice;
  final String? currency;
  final String? unit;

  factory MandiPriceForecast.fromJson(Map<String, dynamic> json) {
    return MandiPriceForecast(
      date: _string(json['date']),
      predictedModalPrice: _number(json['predicted_modal_price']),
      currency: _string(json['currency']),
      unit: _string(json['unit']),
    );
  }
}

List<Map<String, dynamic>> _listOfMaps(dynamic value) {
  if (value is! List) return const [];
  return value.whereType<Map<String, dynamic>>().toList(growable: false);
}

List<String>? _nullableStringList(dynamic value) {
  if (value is! List) return null;
  return value.whereType<String>().toList(growable: false);
}

String? _string(dynamic value) {
  if (value is! String || value.trim().isEmpty) return null;
  return value.trim();
}

double? _number(dynamic value) {
  if (value is num && value.isFinite) return value.toDouble();
  return null;
}
