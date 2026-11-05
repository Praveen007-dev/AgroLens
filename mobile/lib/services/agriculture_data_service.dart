import '../models/agriculture_data.dart';

abstract interface class AgricultureDataService {
  bool get isDemo;

  Future<WeatherData> fetchWeather(String location);

  Future<List<AgricultureScheme>> fetchSchemes({
    String? state,
    String? category,
  });

  Future<List<AgricultureNewsArticle>> fetchNews({String? category});

  Future<List<MandiPrice>> fetchMandiPrices({
    required String commodity,
    String? state,
    String? district,
    String? market,
  });

  Future<List<MandiPricePoint>> fetchPriceHistory({
    required String commodity,
    String? market,
    int days = 30,
  });

  Future<List<MandiPriceForecast>> fetchPriceForecast({
    required String commodity,
    String? market,
    int days = 5,
  });

  void close();
}
