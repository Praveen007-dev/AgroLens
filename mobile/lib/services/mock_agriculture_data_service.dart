import '../models/agriculture_data.dart';
import 'agriculture_data_service.dart';

/// Development-only responses. These values are not live agriculture data.
class MockAgricultureDataService implements AgricultureDataService {
  @override
  bool get isDemo => true;

  @override
  void close() {}

  @override
  Future<WeatherData> fetchWeather(String location) async {
    return WeatherData(
      location: location,
      condition: 'Sample conditions',
      temperatureC: 27,
      rainfallMm: 0,
      rainProbabilityPct: 20,
      humidityPct: 62,
      windSpeedKph: 11,
      windDirection: 'SW',
      forecast: const [
        WeatherForecastDay(
          date: 'Day 1',
          condition: 'Sample conditions',
          minTemperatureC: 20,
          maxTemperatureC: 28,
          rainfallMm: 0,
          rainProbabilityPct: 20,
        ),
        WeatherForecastDay(
          date: 'Day 2',
          condition: 'Sample conditions',
          minTemperatureC: 19,
          maxTemperatureC: 29,
          rainfallMm: 2,
          rainProbabilityPct: 35,
        ),
      ],
    );
  }

  @override
  Future<List<AgricultureScheme>> fetchSchemes({
    String? state,
    String? category,
  }) async {
    if (state != null && state != 'Karnataka' && state != 'All states') {
      return const [];
    }
    if (category != null &&
        category != 'All categories' &&
        category != 'Input support') {
      return const [];
    }
    return const [
      AgricultureScheme(
        name: 'Sample agriculture support scheme',
        scope: 'Central',
        state: 'All states',
        category: 'Input support',
        description:
            'Illustrative development content; replace with verified backend information.',
      ),
    ];
  }

  @override
  Future<List<AgricultureNewsArticle>> fetchNews({String? category}) async {
    return const [
      AgricultureNewsArticle(
        title: 'Sample agriculture market update',
        summary:
            'This is illustrative development content, not a current news report.',
        source: 'AgroLens development sample',
        publishedAt: 'Sample date unavailable',
        category: 'Markets',
      ),
    ];
  }

  @override
  Future<List<MandiPrice>> fetchMandiPrices({
    required String commodity,
    String? state,
    String? district,
    String? market,
  }) async {
    return [
      MandiPrice(
        commodity: commodity,
        state: state,
        district: district,
        market: market,
        minPrice: 1800,
        modalPrice: 2200,
        maxPrice: 2600,
        currency: 'INR',
        unit: 'quintal',
        priceDate: 'Sample date',
      ),
    ];
  }

  @override
  Future<List<MandiPricePoint>> fetchPriceHistory({
    required String commodity,
    String? market,
    int days = 30,
  }) async {
    return const [
      MandiPricePoint(
          date: 'Day 1', modalPrice: 1900, currency: 'INR', unit: 'quintal'),
      MandiPricePoint(
          date: 'Day 2', modalPrice: 2050, currency: 'INR', unit: 'quintal'),
      MandiPricePoint(
          date: 'Day 3', modalPrice: 1980, currency: 'INR', unit: 'quintal'),
      MandiPricePoint(
          date: 'Day 4', modalPrice: 2150, currency: 'INR', unit: 'quintal'),
      MandiPricePoint(
          date: 'Day 5', modalPrice: 2100, currency: 'INR', unit: 'quintal'),
      MandiPricePoint(
          date: 'Day 6', modalPrice: 2250, currency: 'INR', unit: 'quintal'),
      MandiPricePoint(
          date: 'Day 7', modalPrice: 2200, currency: 'INR', unit: 'quintal'),
    ];
  }

  @override
  Future<List<MandiPriceForecast>> fetchPriceForecast({
    required String commodity,
    String? market,
    int days = 5,
  }) async {
    return const [
      MandiPriceForecast(
        date: 'Day 1',
        predictedModalPrice: 2220,
        currency: 'INR',
        unit: 'quintal',
      ),
      MandiPriceForecast(
        date: 'Day 2',
        predictedModalPrice: 2190,
        currency: 'INR',
        unit: 'quintal',
      ),
      MandiPriceForecast(
        date: 'Day 3',
        predictedModalPrice: 2260,
        currency: 'INR',
        unit: 'quintal',
      ),
      MandiPriceForecast(
        date: 'Day 4',
        predictedModalPrice: 2300,
        currency: 'INR',
        unit: 'quintal',
      ),
      MandiPriceForecast(
        date: 'Day 5',
        predictedModalPrice: 2275,
        currency: 'INR',
        unit: 'quintal',
      ),
    ];
  }
}
