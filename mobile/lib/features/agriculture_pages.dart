import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/agriculture_data.dart';
import '../models/scan_record.dart';
import '../services/agriculture_data_service.dart';
import '../services/storage_service.dart';

const _states = ['All states', 'Karnataka', 'Maharashtra', 'Tamil Nadu'];
const _schemeCategories = [
  'All categories',
  'Input support',
  'Insurance',
  'Irrigation',
  'Credit',
];
const _commodities = ['Tomato', 'Potato', 'Rice', 'Maize'];
const _markets = ['Bengaluru', 'Mysuru', 'Hubballi'];

class AgricultureHubPage extends StatelessWidget {
  const AgricultureHubPage({
    super.key,
    required this.service,
    this.storageService,
  });

  final AgricultureDataService service;
  final StorageService? storageService;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Agriculture tools')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          if (service.isDemo) const _DevelopmentDataBanner(),
          const Text(
            'Explore information provided by the agriculture service.',
          ),
          const SizedBox(height: 16),
          _HubTile(
            key: const Key('agriculture-weather'),
            icon: Icons.cloud_outlined,
            title: 'Weather & advisory',
            subtitle: 'Current conditions and forecast',
            onTap: () => _open(context, WeatherPage(service: service)),
          ),
          _HubTile(
            key: const Key('agriculture-schemes'),
            icon: Icons.account_balance_outlined,
            title: 'Schemes & subsidies',
            subtitle: 'Eligibility, benefits and official links',
            onTap: () => _open(context, SchemesPage(service: service)),
          ),
          _HubTile(
            key: const Key('agriculture-news'),
            icon: Icons.newspaper_outlined,
            title: 'Agriculture news',
            subtitle: 'Article summaries and original sources',
            onTap: () => _open(context, NewsPage(service: service)),
          ),
          _HubTile(
            key: const Key('agriculture-markets'),
            icon: Icons.show_chart,
            title: 'Mandi market prices',
            subtitle: 'Latest prices, history and estimates',
            onTap: () => _open(context, MarketPage(service: service)),
          ),
          _HubTile(
            key: const Key('agriculture-scan-history'),
            icon: Icons.history,
            title: 'Scan history',
            subtitle: 'Saved disease scans on this device',
            onTap: () => _open(
              context,
              ScanHistoryPage(storageService: storageService),
            ),
          ),
        ],
      ),
    );
  }

  void _open(BuildContext context, Widget page) {
    Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => page));
  }
}

class WeatherPage extends StatefulWidget {
  const WeatherPage({super.key, required this.service});

  final AgricultureDataService service;

  @override
  State<WeatherPage> createState() => _WeatherPageState();
}

class _WeatherPageState extends State<WeatherPage> {
  final _locationController = TextEditingController();
  Future<WeatherData>? _weather;
  String? _locationError;

  @override
  void dispose() {
    _locationController.dispose();
    super.dispose();
  }

  void _loadWeather() {
    final location = _locationController.text.trim();
    if (location.isEmpty) {
      setState(() {
        _weather = null;
        _locationError = 'Enter a location to request weather information.';
      });
      return;
    }
    setState(() {
      _locationError = null;
      _weather = widget.service.fetchWeather(location);
    });
  }

  @override
  Widget build(BuildContext context) {
    return _FeatureScaffold(
      title: 'Weather & advisory',
      isDemo: widget.service.isDemo,
      children: [
        TextField(
          key: const Key('weather-location'),
          controller: _locationController,
          textCapitalization: TextCapitalization.words,
          onSubmitted: (_) => _loadWeather(),
          decoration: const InputDecoration(
            labelText: 'Location',
            hintText: 'Enter a town, district or location',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 8),
        FilledButton.icon(
          key: const Key('weather-load'),
          onPressed: _loadWeather,
          icon: const Icon(Icons.search),
          label: const Text('Get weather'),
        ),
        if (_locationError case final error?) ...[
          const SizedBox(height: 8),
          Text(error, key: const Key('weather-location-error')),
        ],
        if (_weather case final future?) ...[
          const SizedBox(height: 16),
          _AsyncSection<WeatherData>(
            key: const Key('weather-results'),
            future: future,
            isEmpty: (_) => false,
            emptyMessage: 'Weather information is unavailable.',
            onRetry: _loadWeather,
            builder: (weather) => _WeatherDetails(weather: weather),
          ),
        ],
      ],
    );
  }
}

class _WeatherDetails extends StatelessWidget {
  const _WeatherDetails({required this.weather});

  final WeatherData weather;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _DataCard(
          title: weather.location ?? 'Location unavailable',
          children: [
            _DetailRow('Conditions', _available(weather.condition)),
            _DetailRow('Temperature', _temperature(weather.temperatureC)),
            _DetailRow('Rainfall', _measurement(weather.rainfallMm, 'mm')),
            _DetailRow(
              'Rain probability',
              _measurement(weather.rainProbabilityPct, '%'),
            ),
            _DetailRow('Humidity', _measurement(weather.humidityPct, '%')),
            _DetailRow(
              'Wind',
              weather.windSpeedKph == null
                  ? 'Unavailable'
                  : '${_measurement(weather.windSpeedKph, 'km/h')}${weather.windDirection == null ? '' : ' ${weather.windDirection}'}',
            ),
            _DetailRow('Crop advisory', _available(weather.advisory)),
          ],
        ),
        const SizedBox(height: 16),
        Text('Forecast', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 8),
        if (weather.forecast.isEmpty)
          const _EmptyMessage('Forecast unavailable.')
        else
          ...weather.forecast.map(
            (day) => _DataCard(
              title: _available(day.date),
              children: [
                _DetailRow('Conditions', _available(day.condition)),
                _DetailRow(
                  'Temperature',
                  '${_temperature(day.minTemperatureC)} to ${_temperature(day.maxTemperatureC)}',
                ),
                _DetailRow('Rainfall', _measurement(day.rainfallMm, 'mm')),
                _DetailRow(
                  'Rain probability',
                  _measurement(day.rainProbabilityPct, '%'),
                ),
                _DetailRow('Humidity', _measurement(day.humidityPct, '%')),
                _DetailRow(
                  'Wind',
                  _measurement(day.windSpeedKph, 'km/h'),
                ),
              ],
            ),
          ),
      ],
    );
  }
}

class SchemesPage extends StatefulWidget {
  const SchemesPage({super.key, required this.service});

  final AgricultureDataService service;

  @override
  State<SchemesPage> createState() => _SchemesPageState();
}

class _SchemesPageState extends State<SchemesPage> {
  String _state = _states.first;
  String _category = _schemeCategories.first;
  late Future<List<AgricultureScheme>> _schemes = _load();

  Future<List<AgricultureScheme>> _load() {
    return widget.service.fetchSchemes(
      state: _state == _states.first ? null : _state,
      category: _category == _schemeCategories.first ? null : _category,
    );
  }

  void _applyFilters() {
    setState(() {
      _schemes = _load();
    });
  }

  @override
  Widget build(BuildContext context) {
    return _FeatureScaffold(
      title: 'Schemes & subsidies',
      isDemo: widget.service.isDemo,
      children: [
        Row(
          children: [
            Expanded(
              child: _ChoiceDropdown(
                key: const Key('schemes-state'),
                label: 'State',
                value: _state,
                values: _states,
                onChanged: (value) {
                  _state = value;
                  _applyFilters();
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _ChoiceDropdown(
                key: const Key('schemes-category'),
                label: 'Category',
                value: _category,
                values: _schemeCategories,
                onChanged: (value) {
                  _category = value;
                  _applyFilters();
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        _AsyncSection<List<AgricultureScheme>>(
          key: const Key('schemes-results'),
          future: _schemes,
          isEmpty: (schemes) => schemes.isEmpty,
          emptyMessage: 'No schemes are available for these filters.',
          onRetry: _applyFilters,
          builder: (schemes) => Column(
            children: schemes
                .map((scheme) => _SchemeCard(scheme: scheme))
                .toList(growable: false),
          ),
        ),
      ],
    );
  }
}

class _SchemeCard extends StatelessWidget {
  const _SchemeCard({required this.scheme});

  final AgricultureScheme scheme;

  @override
  Widget build(BuildContext context) {
    final documents = scheme.requiredDocuments;
    return _DataCard(
      title: _available(scheme.name),
      children: [
        _DetailRow('Scope', _available(scheme.scope)),
        _DetailRow('State', _available(scheme.state)),
        _DetailRow('Category', _available(scheme.category)),
        _DetailRow('Details', _available(scheme.description)),
        _DetailRow('Eligibility', _available(scheme.eligibility)),
        _DetailRow('Benefits / subsidy', _available(scheme.benefits)),
        _DetailRow(
          'Required documents',
          documents == null || documents.isEmpty
              ? 'Unavailable'
              : documents.join(', '),
        ),
        _DetailRow(
            'Application deadline', _available(scheme.applicationDeadline)),
        if (_isHttpUrl(scheme.officialUrl))
          Align(
            alignment: AlignmentDirectional.centerStart,
            child: TextButton.icon(
              key: const Key('scheme-official-link'),
              onPressed: () => _openExternalLink(
                context,
                scheme.officialUrl!,
                'Could not open the official scheme link.',
              ),
              icon: const Icon(Icons.open_in_new),
              label: const Text('Official information / application'),
            ),
          )
        else
          const _DetailRow('Official link', 'Unavailable'),
      ],
    );
  }
}

class NewsPage extends StatefulWidget {
  const NewsPage({super.key, required this.service});

  final AgricultureDataService service;

  @override
  State<NewsPage> createState() => _NewsPageState();
}

class _NewsPageState extends State<NewsPage> {
  late Future<List<AgricultureNewsArticle>> _articles = _load();

  Future<List<AgricultureNewsArticle>> _load() => widget.service.fetchNews();

  void _retry() {
    setState(() {
      _articles = _load();
    });
  }

  @override
  Widget build(BuildContext context) {
    return _FeatureScaffold(
      title: 'Agriculture news',
      isDemo: widget.service.isDemo,
      children: [
        _AsyncSection<List<AgricultureNewsArticle>>(
          key: const Key('news-results'),
          future: _articles,
          isEmpty: (articles) => articles.isEmpty,
          emptyMessage: 'No news articles are available.',
          onRetry: _retry,
          builder: (articles) => Column(
            children: articles
                .map((article) => _NewsCard(article: article))
                .toList(growable: false),
          ),
        ),
      ],
    );
  }
}

class _NewsCard extends StatelessWidget {
  const _NewsCard({required this.article});

  final AgricultureNewsArticle article;

  @override
  Widget build(BuildContext context) {
    return _DataCard(
      title: _available(article.title),
      children: [
        _DetailRow('Source', _available(article.source)),
        _DetailRow('Date', _available(article.publishedAt)),
        _DetailRow('Category', _available(article.category)),
        const Padding(
          padding: EdgeInsets.only(top: 8),
          child: Text(
            'Summary',
            style: TextStyle(fontWeight: FontWeight.w700),
          ),
        ),
        Text(_available(article.summary)),
        if (_isHttpUrl(article.originalUrl))
          Align(
            alignment: AlignmentDirectional.centerStart,
            child: TextButton.icon(
              key: const Key('news-original-link'),
              onPressed: () => _openExternalLink(
                context,
                article.originalUrl!,
                'Could not open the original article.',
              ),
              icon: const Icon(Icons.open_in_new),
              label: const Text('Read original article'),
            ),
          )
        else
          const _DetailRow('Original article link', 'Unavailable'),
      ],
    );
  }
}

class MarketPage extends StatefulWidget {
  const MarketPage({super.key, required this.service});

  final AgricultureDataService service;

  @override
  State<MarketPage> createState() => _MarketPageState();
}

class _MarketPageState extends State<MarketPage> {
  String _commodity = _commodities.first;
  String _state = 'Karnataka';
  String _market = _markets.first;
  late Future<List<MandiPrice>> _prices = _loadPrices();
  late Future<List<MandiPricePoint>> _history = _loadHistory();
  late Future<List<MandiPriceForecast>> _forecast = _loadForecast();

  Future<List<MandiPrice>> _loadPrices() => widget.service.fetchMandiPrices(
        commodity: _commodity,
        state: _state,
        market: _market,
      );

  Future<List<MandiPricePoint>> _loadHistory() =>
      widget.service.fetchPriceHistory(
        commodity: _commodity,
        market: _market,
        days: 30,
      );

  Future<List<MandiPriceForecast>> _loadForecast() =>
      widget.service.fetchPriceForecast(
        commodity: _commodity,
        market: _market,
        days: 5,
      );

  void _applyFilters() {
    setState(() {
      _prices = _loadPrices();
      _history = _loadHistory();
      _forecast = _loadForecast();
    });
  }

  @override
  Widget build(BuildContext context) {
    return _FeatureScaffold(
      title: 'Mandi market prices',
      isDemo: widget.service.isDemo,
      children: [
        _ChoiceDropdown(
          key: const Key('market-commodity'),
          label: 'Crop / commodity',
          value: _commodity,
          values: _commodities,
          onChanged: (value) {
            _commodity = value;
            _applyFilters();
          },
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _ChoiceDropdown(
                key: const Key('market-state'),
                label: 'State',
                value: _state,
                values: const ['Karnataka', 'Maharashtra', 'Tamil Nadu'],
                onChanged: (value) {
                  _state = value;
                  _applyFilters();
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _ChoiceDropdown(
                key: const Key('market-market'),
                label: 'Market',
                value: _market,
                values: _markets,
                onChanged: (value) {
                  _market = value;
                  _applyFilters();
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),
        Text('Latest available prices',
            style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 8),
        _AsyncSection<List<MandiPrice>>(
          key: const Key('market-latest'),
          future: _prices,
          isEmpty: (prices) => prices.isEmpty,
          emptyMessage: 'No mandi prices are available for this selection.',
          onRetry: _applyFilters,
          builder: (prices) => Column(
            children: prices.map((price) => _PriceCard(price: price)).toList(),
          ),
        ),
        const SizedBox(height: 20),
        Text('Historical modal prices',
            style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 8),
        _AsyncSection<List<MandiPricePoint>>(
          key: const Key('market-history'),
          future: _history,
          isEmpty: (points) => points.isEmpty,
          emptyMessage: 'Historical prices are unavailable.',
          onRetry: _applyFilters,
          builder: (points) => _HistoryCard(
            commodity: _commodity,
            points: points,
          ),
        ),
        const SizedBox(height: 20),
        Text('5-day price forecast',
            style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 4),
        const Text('Forecasts are estimates, not guaranteed prices.'),
        const SizedBox(height: 8),
        _AsyncSection<List<MandiPriceForecast>>(
          key: const Key('market-forecast'),
          future: _forecast,
          isEmpty: (forecasts) => forecasts.isEmpty,
          emptyMessage: 'No price forecast is available.',
          onRetry: _applyFilters,
          builder: (forecasts) => Column(
            children: forecasts
                .take(5)
                .map(
                  (forecast) => _ForecastRow(forecast: forecast),
                )
                .toList(growable: false),
          ),
        ),
      ],
    );
  }
}

class _PriceCard extends StatelessWidget {
  const _PriceCard({required this.price});

  final MandiPrice price;

  @override
  Widget build(BuildContext context) {
    return _DataCard(
      title: '${_available(price.commodity)} · ${_available(price.market)}',
      children: [
        _DetailRow(
          'Location',
          '${_available(price.district)}, ${_available(price.state)}',
        ),
        _DetailRow('Date', _available(price.priceDate)),
        _DetailRow(
          'Minimum price',
          _price(price.minPrice, price.currency, price.unit),
        ),
        _DetailRow(
          'Modal price',
          _price(price.modalPrice, price.currency, price.unit),
        ),
        _DetailRow(
          'Maximum price',
          _price(price.maxPrice, price.currency, price.unit),
        ),
      ],
    );
  }
}

class _HistoryCard extends StatelessWidget {
  const _HistoryCard({required this.commodity, required this.points});

  final String commodity;
  final List<MandiPricePoint> points;

  @override
  Widget build(BuildContext context) {
    final unitSource = points.firstWhere(
      (point) => point.modalPrice != null,
      orElse: () => points.first,
    );
    return _DataCard(
      title:
          '$commodity modal price (${_available(unitSource.currency)} / ${_available(unitSource.unit)})',
      children: [
        Semantics(
          label:
              'Historical modal prices for $commodity: ${points.map((point) => '${_available(point.date)} ${_price(point.modalPrice, point.currency, point.unit)}').join(', ')}',
          child: SizedBox(
            height: 190,
            child: CustomPaint(
              key: const Key('market-price-chart'),
              painter: _PriceChartPainter(points),
              child: const SizedBox.expand(),
            ),
          ),
        ),
        if (points.length < 2)
          const _EmptyMessage('Not enough historical prices to draw a chart.'),
        ...points.map(
          (point) => _DetailRow(
            _available(point.date),
            _price(point.modalPrice, point.currency, point.unit),
          ),
        ),
      ],
    );
  }
}

class _PriceChartPainter extends CustomPainter {
  const _PriceChartPainter(this.points);

  final List<MandiPricePoint> points;

  @override
  void paint(Canvas canvas, Size size) {
    final validPoints = points
        .where((point) => point.modalPrice != null)
        .toList(growable: false);
    if (validPoints.isEmpty || size.width <= 0 || size.height <= 0) return;

    final values = validPoints.map((point) => point.modalPrice!).toList();
    final minimum = values.reduce((a, b) => a < b ? a : b);
    final maximum = values.reduce((a, b) => a > b ? a : b);
    final range = maximum - minimum;
    const horizontalInset = 12.0;
    const verticalInset = 12.0;
    final plotWidth = size.width - horizontalInset * 2;
    final plotHeight = size.height - verticalInset * 2;
    final line = Paint()
      ..color = const Color(0xFF356B46)
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    final grid = Paint()
      ..color = const Color(0xFFE3E9DF)
      ..strokeWidth = 1;
    for (var index = 0; index < 4; index++) {
      final y = verticalInset + plotHeight * index / 3;
      canvas.drawLine(Offset(horizontalInset, y),
          Offset(size.width - horizontalInset, y), grid);
    }

    final path = Path();
    for (var index = 0; index < values.length; index++) {
      final x = values.length == 1
          ? size.width / 2
          : horizontalInset + plotWidth * index / (values.length - 1);
      final normalized = range == 0 ? 0.5 : (values[index] - minimum) / range;
      final y = verticalInset + plotHeight * (1 - normalized);
      if (index == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    canvas.drawPath(path, line);
    for (var index = 0; index < values.length; index++) {
      final x = values.length == 1
          ? size.width / 2
          : horizontalInset + plotWidth * index / (values.length - 1);
      final normalized = range == 0 ? 0.5 : (values[index] - minimum) / range;
      final y = verticalInset + plotHeight * (1 - normalized);
      canvas.drawCircle(
        Offset(x, y),
        4,
        Paint()..color = const Color(0xFF356B46),
      );
    }
  }

  @override
  bool shouldRepaint(covariant _PriceChartPainter oldDelegate) =>
      oldDelegate.points != points;
}

class _ForecastRow extends StatelessWidget {
  const _ForecastRow({required this.forecast});

  final MandiPriceForecast forecast;

  @override
  Widget build(BuildContext context) {
    return _DetailRow(
      _available(forecast.date),
      _price(
        forecast.predictedModalPrice,
        forecast.currency,
        forecast.unit,
      ),
    );
  }
}

class ScanHistoryPage extends StatefulWidget {
  const ScanHistoryPage({super.key, this.storageService});

  final StorageService? storageService;

  @override
  State<ScanHistoryPage> createState() => _ScanHistoryPageState();
}

class _ScanHistoryPageState extends State<ScanHistoryPage> {
  late Future<List<ScanRecord>> _records = _load();

  Future<List<ScanRecord>> _load() async {
    final storage = widget.storageService ?? await StorageService.initialize();
    return storage.getCachedScans();
  }

  void _retry() {
    setState(() {
      _records = _load();
    });
  }

  @override
  Widget build(BuildContext context) {
    return _FeatureScaffold(
      title: 'Scan history',
      children: [
        _AsyncSection<List<ScanRecord>>(
          key: const Key('scan-history-results'),
          future: _records,
          isEmpty: (records) => records.isEmpty,
          emptyMessage: 'No scans have been saved on this device yet.',
          onRetry: _retry,
          builder: (records) => Column(
            children: records
                .map(
                  (record) => _DataCard(
                    title: record.crop,
                    children: [
                      _DetailRow(
                        'AI prediction',
                        record.aiPrediction.diseaseLabel
                            .replaceFirst(RegExp(r'^.*___'), '')
                            .replaceAll('_', ' '),
                      ),
                      _DetailRow(
                        'Confidence',
                        '${(record.aiPrediction.confidence * 100).toStringAsFixed(0)}%',
                      ),
                      _DetailRow('Scan time', record.timestamp),
                      _DetailRow('Sync status', record.syncStatus.name),
                    ],
                  ),
                )
                .toList(growable: false),
          ),
        ),
      ],
    );
  }
}

class _FeatureScaffold extends StatelessWidget {
  const _FeatureScaffold({
    required this.title,
    required this.children,
    this.isDemo = false,
  });

  final String title;
  final List<Widget> children;
  final bool isDemo;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          if (isDemo) const _DevelopmentDataBanner(),
          ...children,
        ],
      ),
    );
  }
}

class _DevelopmentDataBanner extends StatelessWidget {
  const _DevelopmentDataBanner();

  @override
  Widget build(BuildContext context) {
    return const Card(
      color: Color(0xFFFFF3D6),
      child: Padding(
        padding: EdgeInsets.all(12),
        child: Text(
          'Development sample data - not live information or advice.',
          key: Key('development-data-banner'),
        ),
      ),
    );
  }
}

class _HubTile extends StatelessWidget {
  const _HubTile({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Icon(icon, color: const Color(0xFF356B46)),
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}

class _ChoiceDropdown extends StatelessWidget {
  const _ChoiceDropdown({
    Key? key,
    required this.label,
    required this.value,
    required this.values,
    required this.onChanged,
  }) : fieldKey = key;

  final Key? fieldKey;
  final String label;
  final String value;
  final List<String> values;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField<String>(
      key: fieldKey,
      initialValue: value,
      isExpanded: true,
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      ),
      items: values
          .map((choice) => DropdownMenuItem(value: choice, child: Text(choice)))
          .toList(growable: false),
      onChanged: (choice) {
        if (choice != null && choice != value) onChanged(choice);
      },
    );
  }
}

class _AsyncSection<T> extends StatelessWidget {
  const _AsyncSection({
    super.key,
    required this.future,
    required this.isEmpty,
    required this.emptyMessage,
    required this.onRetry,
    required this.builder,
  });

  final Future<T> future;
  final bool Function(T value) isEmpty;
  final String emptyMessage;
  final VoidCallback onRetry;
  final Widget Function(T value) builder;

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<T>(
      future: future,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Padding(
            padding: EdgeInsets.all(24),
            child: Center(child: CircularProgressIndicator()),
          );
        }
        if (snapshot.hasError) {
          return Column(
            children: [
              _EmptyMessage('Could not load data: ${snapshot.error}'),
              TextButton.icon(
                key: const Key('feature-retry'),
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: const Text('Try again'),
              ),
            ],
          );
        }
        final value = snapshot.data;
        if (value == null || isEmpty(value)) {
          return _EmptyMessage(emptyMessage);
        }
        return builder(value);
      },
    );
  }
}

class _DataCard extends StatelessWidget {
  const _DataCard({required this.title, required this.children});

  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.white,
      elevation: 0,
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: const BorderSide(color: Color(0xFFE3E9DF)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 8),
            ...children,
          ],
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow(this.label, this.value);

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 140,
            child: Text(label,
                style: const TextStyle(fontWeight: FontWeight.w600)),
          ),
          const SizedBox(width: 8),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}

class _EmptyMessage extends StatelessWidget {
  const _EmptyMessage(this.message);

  final String message;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Text(message),
    );
  }
}

String _available(String? value) =>
    value == null || value.trim().isEmpty ? 'Unavailable' : value;

String _measurement(double? value, String unit) {
  if (value == null) return 'Unavailable';
  return '${value.toStringAsFixed(value.truncateToDouble() == value ? 0 : 1)} $unit';
}

String _temperature(double? value) =>
    value == null ? 'Unavailable' : _measurement(value, '°C');

String _price(double? value, String? currency, String? unit) {
  if (value == null) return 'Unavailable';
  final amount = '${_available(currency)} ${value.toStringAsFixed(2)}';
  return unit == null || unit.trim().isEmpty
      ? '$amount / unit unavailable'
      : '$amount / $unit';
}

bool _isHttpUrl(String? rawUrl) {
  if (rawUrl == null) return false;
  final uri = Uri.tryParse(rawUrl);
  return uri != null &&
      (uri.scheme == 'https' || uri.scheme == 'http') &&
      uri.host.isNotEmpty;
}

Future<void> _openExternalLink(
  BuildContext context,
  String rawUrl,
  String failureMessage,
) async {
  final uri = Uri.tryParse(rawUrl);
  if (uri == null ||
      (uri.scheme != 'https' && uri.scheme != 'http') ||
      uri.host.isEmpty) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('This link is not a valid web address.')),
    );
    return;
  }
  try {
    final opened = await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!opened && context.mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(failureMessage)));
    }
  } catch (error) {
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('$failureMessage $error')),
    );
  }
}
