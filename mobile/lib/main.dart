import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:uuid/uuid.dart';

import 'config/app_config.dart';
import 'features/auth_pages.dart';
import 'l10n/app_localizations.dart';
import 'models/inference_result.dart';
import 'models/scan_record.dart';
import 'features/agriculture_pages.dart';
import 'services/agriculture_data_service.dart';
import 'services/auth_service.dart';
import 'services/http_agriculture_data_service.dart';
import 'services/inference_service.dart';
import 'services/local_auth_service.dart';
import 'services/location_service.dart';
import 'services/mock_agriculture_data_service.dart';
import 'services/mock_inference_service.dart';
import 'services/storage_service.dart';
import 'services/tflite_inference_service.dart';

const _supportedLocales = <Locale>[
  Locale('en'),
  Locale('hi'),
  Locale('te'),
  Locale('ta'),
  Locale('kn'),
];

enum _LocationSettingsTarget { app, location }

void main() {
  runApp(const AgroLensApp());
}

AgricultureDataService _createAgricultureDataService() => AppConfig.useMockApi
    ? MockAgricultureDataService()
    : HttpAgricultureDataService();

class AgroLensApp extends StatefulWidget {
  const AgroLensApp({
    super.key,
    this.inferenceService,
    this.locationService,
    this.storageService,
    this.agricultureDataService,
    this.authService,
    this.initialLocale = const Locale('en'),
  });

  final InferenceService? inferenceService;
  final LocationService? locationService;
  final StorageService? storageService;
  final AgricultureDataService? agricultureDataService;
  final AuthService? authService;
  final Locale initialLocale;

  @override
  State<AgroLensApp> createState() => _AgroLensAppState();
}

class _AgroLensAppState extends State<AgroLensApp> {
  late Locale _locale = widget.initialLocale;
  late final AgricultureDataService _agricultureService;
  late final bool _ownsAgricultureService;
  late final AuthService _authService;
  AuthSession? _session;
  bool _isRestoringSession = true;
  String? _restoreError;

  @override
  void initState() {
    super.initState();
    _ownsAgricultureService = widget.agricultureDataService == null;
    _agricultureService =
        widget.agricultureDataService ?? _createAgricultureDataService();
    _authService = widget.authService ?? LocalAuthService();
    _restoreSession();
  }

  Future<void> _restoreSession() async {
    try {
      final session = await _authService.restoreSession();
      if (mounted) setState(() => _session = session);
    } catch (error) {
      if (mounted) setState(() => _restoreError = error.toString());
    } finally {
      if (mounted) setState(() => _isRestoringSession = false);
    }
  }

  void _onAuthenticated(AuthSession session) {
    setState(() {
      _session = session;
      _restoreError = null;
    });
  }

  Future<void> _signOut() async {
    try {
      await _authService.signOut();
      if (mounted) setState(() => _session = null);
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not sign out: $error')),
      );
    }
  }

  @override
  void dispose() {
    if (_ownsAgricultureService) _agricultureService.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      key: ValueKey(_session == null ? 'signed-out' : 'signed-in'),
      title: AppConfig.appName,
      locale: _locale,
      supportedLocales: _supportedLocales,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF356B46),
          surface: const Color(0xFFF6F8F3),
        ),
        scaffoldBackgroundColor: const Color(0xFFF6F8F3),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFFF6F8F3),
          surfaceTintColor: Colors.transparent,
        ),
        useMaterial3: true,
      ),
      home: _isRestoringSession
          ? const Scaffold(
              body: Center(child: CircularProgressIndicator()),
            )
          : _session == null
              ? AuthPage(
                  key: const Key('agrolens-auth-page'),
                  authService: _authService,
                  onAuthenticated: _onAuthenticated,
                  initialError: _restoreError,
                )
              : ScanPage(
                  locale: _locale,
                  onLocaleChanged: (locale) => setState(() => _locale = locale),
                  agricultureDataService: _agricultureService,
                  inferenceService: widget.inferenceService ??
                      (AppConfig.useMockInference
                          ? MockInferenceService()
                          : TFLiteInferenceService()),
                  locationService: widget.locationService ?? LocationService(),
                  storageService: widget.storageService,
                  session: _session!,
                  onSignOut: _signOut,
                ),
    );
  }
}

class ScanPage extends StatefulWidget {
  const ScanPage({
    super.key,
    required this.locale,
    required this.onLocaleChanged,
    this.agricultureDataService,
    required this.inferenceService,
    required this.locationService,
    required this.session,
    required this.onSignOut,
    this.storageService,
  });

  final Locale locale;
  final ValueChanged<Locale> onLocaleChanged;
  final AgricultureDataService? agricultureDataService;
  final InferenceService inferenceService;
  final LocationService locationService;
  final AuthSession session;
  final Future<void> Function() onSignOut;
  final StorageService? storageService;

  @override
  State<ScanPage> createState() => _ScanPageState();
}

class _ScanPageState extends State<ScanPage> {
  static const _uuid = Uuid();

  final ImagePicker _imagePicker = ImagePicker();
  final TextEditingController _cropController = TextEditingController(
    text: AppConfig.supportedCrops.first,
  );
  XFile? _image;
  InferenceResult? _result;
  ScanRecord? _scanRecord;
  ScanLocation? _location;
  String _crop = AppConfig.supportedCrops.first;
  String? _error;
  _LocationSettingsTarget? _locationSettingsTarget;
  bool _isScanning = false;
  bool _isGettingLocation = false;
  bool _scanSavedLocally = false;

  @override
  void dispose() {
    _cropController.dispose();
    widget.inferenceService.dispose();
    super.dispose();
  }

  void _setCrop(String crop) {
    final trimmedCrop = crop.trim();
    setState(() {
      _crop = trimmedCrop;
      _result = null;
      _scanRecord = null;
      _scanSavedLocally = false;
      _error = null;
      _locationSettingsTarget = null;
    });
  }

  Future<void> _pickImage(ImageSource source) async {
    final l10n = AppLocalizations.of(context)!;
    try {
      final image = await _imagePicker.pickImage(
        source: source,
        imageQuality: 85,
      );
      if (!mounted || image == null) return;

      setState(() {
        _image = image;
        _result = null;
        _scanRecord = null;
        _scanSavedLocally = false;
        _error = null;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() => _error = l10n.errorCouldNotOpenPhoto(error.toString()));
    }
  }

  Future<StorageService> _getStorage() async {
    final storage = widget.storageService;
    if (storage != null) return storage;
    return StorageService.initialize();
  }

  Future<void> _addLocation() async {
    if (_isGettingLocation || _isScanning) return;
    setState(() {
      _isGettingLocation = true;
      _error = null;
      _locationSettingsTarget = null;
    });

    try {
      final location = await widget.locationService.getCurrentLocation();
      var updatedRecord = _scanRecord;
      if (updatedRecord != null) {
        updatedRecord = updatedRecord.copyWith(location: location);
        await (await _getStorage()).saveScan(updatedRecord);
      }
      if (!mounted) return;
      setState(() {
        _location = location;
        _scanRecord = updatedRecord;
        if (updatedRecord != null) _scanSavedLocally = true;
      });
    } on LocationServiceException catch (error) {
      if (!mounted) return;
      final l10n = AppLocalizations.of(context)!;
      final message = switch (error.failure) {
        LocationFailure.servicesDisabled => l10n.locationServiceDisabled,
        LocationFailure.permissionDenied => l10n.locationPermissionDenied,
        LocationFailure.permissionDeniedForever =>
          l10n.locationPermissionDeniedForever,
        LocationFailure.positionUnavailable => l10n.locationPositionUnavailable,
      };
      setState(() {
        _error = message;
        _locationSettingsTarget = switch (error.failure) {
          LocationFailure.servicesDisabled => _LocationSettingsTarget.location,
          LocationFailure.permissionDeniedForever =>
            _LocationSettingsTarget.app,
          _ => null,
        };
      });
    } catch (error) {
      if (!mounted) return;
      setState(
        () => _error = AppLocalizations.of(
          context,
        )!
            .locationRequestFailed(error.toString()),
      );
    } finally {
      if (mounted) setState(() => _isGettingLocation = false);
    }
  }

  Future<void> _openLocationSettings() async {
    final target = _locationSettingsTarget;
    if (target == null) return;

    final opened = switch (target) {
      _LocationSettingsTarget.app =>
        await widget.locationService.openAppSettings(),
      _LocationSettingsTarget.location =>
        await widget.locationService.openLocationSettings(),
    };
    if (!mounted || opened) return;

    setState(() {
      _error = AppLocalizations.of(context)!.locationSettingsUnavailable;
      _locationSettingsTarget = null;
    });
  }

  Future<void> _scan() async {
    final image = _image;
    if (image == null || _isScanning) return;
    final crop = _crop.trim();
    final l10n = AppLocalizations.of(context)!;
    if (_location == null) {
      setState(() => _error = l10n.locationRequired);
      return;
    }
    if (crop.isEmpty) {
      setState(() => _error = l10n.plantNameRequired);
      return;
    }

    setState(() {
      _isScanning = true;
      _error = null;
      _result = null;
      _scanRecord = null;
      _scanSavedLocally = false;
    });

    try {
      final result = await widget.inferenceService.runInference(
        imagePath: image.path,
        cropHint: crop,
      );
      if (!mounted) return;

      final record = ScanRecord(
        scanId: _uuid.v4(),
        timestamp: DateTime.now().toUtc().toIso8601String(),
        crop: crop,
        imagePath: image.path,
        aiPrediction: result,
        location: _location,
        syncStatus: SyncStatus.pending,
      );
      setState(() {
        _result = result;
        _scanRecord = record;
      });

      try {
        await (await _getStorage()).saveScan(record);
        if (!mounted) return;
        setState(() => _scanSavedLocally = true);
      } catch (error) {
        if (!mounted) return;
        setState(
          () => _error = AppLocalizations.of(
            context,
          )!
              .errorCouldNotSaveScan(error.toString()),
        );
      }
    } catch (error) {
      if (!mounted) return;
      if (error is UnsupportedError) {
        setState(() => _error = l10n.cropNotSupported(crop));
        return;
      }
      setState(
        () => _error = AppLocalizations.of(
          context,
        )!
            .errorCouldNotAnalyzePhoto(error.toString()),
      );
    } finally {
      if (mounted) setState(() => _isScanning = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.eco_rounded, color: Color(0xFF356B46)),
            const SizedBox(width: 8),
            Text(
              l10n.appTitle,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
          ],
        ),
        centerTitle: false,
        actions: [
          IconButton(
            key: const Key('auth-sign-out'),
            tooltip:
                '${l10n.authLogOut} (${l10n.authLoggedInAs(widget.session.displayName)})',
            icon: const Icon(Icons.logout),
            onPressed: widget.onSignOut,
          ),
          IconButton(
            key: const Key('open-agriculture-tools'),
            tooltip: 'Agriculture tools',
            icon: const Icon(Icons.grid_view_rounded),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute<void>(
                  builder: (_) => AgricultureHubPage(
                    service: widget.agricultureDataService ??
                        _createAgricultureDataService(),
                    storageService: widget.storageService,
                  ),
                ),
              );
            },
          ),
          Tooltip(
            message: l10n.languageLabel,
            child: DropdownButton<Locale>(
              key: const Key('language-selector'),
              value: widget.locale,
              underline: const SizedBox.shrink(),
              icon: const Icon(Icons.language),
              items: [
                DropdownMenuItem(
                  value: const Locale('en'),
                  child: Text(l10n.languageEnglish),
                ),
                DropdownMenuItem(
                  value: const Locale('hi'),
                  child: Text(l10n.languageHindi),
                ),
                DropdownMenuItem(
                  value: const Locale('te'),
                  child: Text(l10n.languageTelugu),
                ),
                DropdownMenuItem(
                  value: const Locale('ta'),
                  child: Text(l10n.languageTamil),
                ),
                DropdownMenuItem(
                  value: const Locale('kn'),
                  child: Text(l10n.languageKannada),
                ),
              ],
              onChanged: (locale) {
                if (locale != null) widget.onLocaleChanged(locale);
              },
            ),
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 620),
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 36),
            children: [
              _WelcomeCard(
                title: l10n.checkYourCrop,
                subtitle: l10n.scanIntroduction,
              ),
              if (AppConfig.useMockInference) ...[
                const SizedBox(height: 16),
                _InfoCard(
                  icon: Icons.science_outlined,
                  message: l10n.demoModeNotice,
                ),
              ],
              const SizedBox(height: 24),
              _SectionHeading(
                key: const Key('photo-section-heading'),
                number: '01',
                title: l10n.choosePhoto,
              ),
              const SizedBox(height: 10),
              _PhotoPickerCard(
                image: _image,
                isBusy: _isScanning,
                onGallery: () => _pickImage(ImageSource.gallery),
                onCamera: () => _pickImage(ImageSource.camera),
              ),
              const SizedBox(height: 24),
              _SectionHeading(
                key: const Key('crop-section-heading'),
                number: '02',
                title: l10n.plantNameLabel,
              ),
              const SizedBox(height: 10),
              TextField(
                key: const Key('plant-name-field'),
                controller: _cropController,
                textCapitalization: TextCapitalization.words,
                enabled: !_isScanning,
                onChanged: _setCrop,
                decoration: InputDecoration(
                  hintText: l10n.plantNameHint,
                  prefixIcon: const Icon(Icons.eco_outlined),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(18),
                    borderSide: BorderSide.none,
                  ),
                  filled: true,
                  fillColor: Colors.white,
                ),
              ),
              const SizedBox(height: 14),
              Text(
                l10n.supportedCropsTitle,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: AppConfig.supportedCrops
                    .where((crop) => crop != 'Other / Unspecified')
                    .map(
                      (crop) => ChoiceChip(
                        key: Key('crop-chip-$crop'),
                        label: Text(_localizedCrop(l10n, crop)),
                        selected: _crop.toLowerCase() == crop.toLowerCase(),
                        onSelected: _isScanning
                            ? null
                            : (selected) {
                                if (!selected) return;
                                _cropController.text = crop;
                                _cropController.selection =
                                    TextSelection.collapsed(
                                  offset: _cropController.text.length,
                                );
                                _setCrop(crop);
                              },
                      ),
                    )
                    .toList(),
              ),
              const SizedBox(height: 12),
              _InfoCard(
                icon: Icons.info_outline,
                message: l10n.modelCoverageNotice,
                compact: true,
              ),
              const SizedBox(height: 24),
              _SectionHeading(
                key: const Key('location-section-heading'),
                number: '03',
                title: l10n.locationTitle,
              ),
              const SizedBox(height: 10),
              _LocationCard(
                location: _location,
                isLoading: _isGettingLocation,
                onAdd: _addLocation,
              ),
              const SizedBox(height: 16),
              FilledButton.icon(
                key: const Key('analyze-photo'),
                style: FilledButton.styleFrom(
                  minimumSize: const Size.fromHeight(56),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(18),
                  ),
                ),
                onPressed: _image == null ||
                        _location == null ||
                        _isScanning ||
                        _isGettingLocation
                    ? null
                    : _scan,
                icon: _isScanning
                    ? const SizedBox.square(
                        dimension: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.auto_awesome),
                label: Text(_isScanning ? l10n.analyzing : l10n.analyzePhoto),
              ),
              if (_error case final error?) ...[
                const SizedBox(height: 16),
                _InfoCard(icon: Icons.error_outline, message: error),
                if (_locationSettingsTarget != null)
                  Align(
                    alignment: Alignment.centerLeft,
                    child: TextButton.icon(
                      key: const Key('open-location-settings'),
                      onPressed: _openLocationSettings,
                      icon: const Icon(Icons.settings),
                      label: Text(AppLocalizations.of(context)!.openSettings),
                    ),
                  ),
              ],
              if (_result case final result?) ...[
                const SizedBox(height: 24),
                _ResultCard(
                  result: result,
                  location: _scanRecord?.location,
                  isSavedLocally: _scanSavedLocally,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _WelcomeCard extends StatelessWidget {
  const _WelcomeCard({required this.title, required this.subtitle});

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF315F40), Color(0xFF4E8056)],
        ),
        borderRadius: BorderRadius.circular(28),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF315F40).withValues(alpha: 0.18),
            blurRadius: 24,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: theme.textTheme.headlineSmall?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.w700,
                    height: 1.15,
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  subtitle,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: Colors.white.withValues(alpha: 0.9),
                    height: 1.45,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Icon(
            Icons.eco_rounded,
            size: 64,
            color: Colors.white.withValues(alpha: 0.92),
          ),
        ],
      ),
    );
  }
}

class _SectionHeading extends StatelessWidget {
  const _SectionHeading({
    super.key,
    required this.number,
    required this.title,
  });

  final String number;
  final String title;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 30,
          height: 30,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: const Color(0xFFE2EBDF),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            number,
            style: const TextStyle(
              color: Color(0xFF315F40),
              fontSize: 12,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
        ),
      ],
    );
  }
}

class _PhotoPickerCard extends StatelessWidget {
  const _PhotoPickerCard({
    required this.image,
    required this.isBusy,
    required this.onGallery,
    required this.onCamera,
  });

  final XFile? image;
  final bool isBusy;
  final VoidCallback onGallery;
  final VoidCallback onCamera;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFE3E9DF)),
      ),
      child: Column(
        children: [
          if (image case final selectedImage?) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              decoration: BoxDecoration(
                color: const Color(0xFFF2F6EF),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Row(
                children: [
                  const Icon(Icons.check_circle, color: Color(0xFF356B46)),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      selectedImage.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
          ] else ...[
            const Icon(
              Icons.add_photo_alternate_outlined,
              size: 38,
              color: Color(0xFF52745A),
            ),
            const SizedBox(height: 6),
            Text(
              l10n.photoActionsHint,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 12),
          ],
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: isBusy ? null : onGallery,
                  icon: const Icon(Icons.photo_library_outlined),
                  label: Text(l10n.choosePhoto),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size.fromHeight(48),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: isBusy ? null : onCamera,
                  icon: const Icon(Icons.camera_alt_outlined),
                  label: Text(l10n.takePhoto),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size.fromHeight(48),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _LocationCard extends StatelessWidget {
  const _LocationCard({
    required this.location,
    required this.isLoading,
    required this.onAdd,
  });

  final ScanLocation? location;
  final bool isLoading;
  final VoidCallback onAdd;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Card(
      color: Colors.white,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(22),
        side: BorderSide(
          color: location == null
              ? const Color(0xFFDBB965)
              : const Color(0xFFB7D0B8),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: location == null
                    ? const Color(0xFFFFF3D6)
                    : const Color(0xFFE7F1E5),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(
                location == null ? Icons.location_searching : Icons.location_on,
                color: const Color(0xFF356B46),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          l10n.locationTitle,
                          style: Theme.of(context)
                              .textTheme
                              .titleMedium
                              ?.copyWith(fontWeight: FontWeight.w700),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: location == null
                              ? const Color(0xFFFFF3D6)
                              : const Color(0xFFE7F1E5),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          location == null
                              ? l10n.requiredLabel
                              : l10n.readyLabel,
                          style:
                              Theme.of(context).textTheme.labelSmall?.copyWith(
                                    color: const Color(0xFF315F40),
                                    fontWeight: FontWeight.w700,
                                  ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(l10n.locationPrivacyNotice),
                  if (location case final currentLocation?) ...[
                    const SizedBox(height: 10),
                    Text(
                      l10n.locationCoordinates(
                        currentLocation.latitude.toStringAsFixed(4),
                        currentLocation.longitude.toStringAsFixed(4),
                      ),
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                  ],
                  const SizedBox(height: 12),
                  FilledButton.tonalIcon(
                    key: const Key('set-required-location'),
                    onPressed: isLoading ? null : onAdd,
                    icon: isLoading
                        ? const SizedBox.square(
                            dimension: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : Icon(
                            location == null
                                ? Icons.my_location
                                : Icons.refresh,
                          ),
                    label: Text(
                      isLoading
                          ? l10n.gettingLocation
                          : location == null
                              ? l10n.addLocation
                              : l10n.updateLocation,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({
    required this.icon,
    required this.message,
    this.compact = false,
  });

  final IconData icon;
  final String message;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFFEDF2E9),
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      child: Padding(
        padding: EdgeInsets.all(compact ? 12 : 16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, size: compact ? 20 : 22, color: const Color(0xFF52745A)),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                message,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      height: 1.4,
                    ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ResultCard extends StatelessWidget {
  const _ResultCard({
    required this.result,
    required this.location,
    required this.isSavedLocally,
  });

  final InferenceResult result;
  final ScanLocation? location;
  final bool isSavedLocally;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Card(
      color: Colors.white,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: Color(0xFFE3E9DF)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.predictionTitle,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            Text(
              _localizedDiseaseName(l10n, result.diseaseLabel),
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 4),
            Text(
              l10n.resultSummary(
                _localizedCrop(l10n, result.crop),
                result.formattedConfidence,
              ),
            ),
            if (result.isLowConfidence) ...[
              const SizedBox(height: 12),
              _InfoCard(
                icon: Icons.warning_amber_outlined,
                message: l10n.lowConfidenceWarning,
              ),
            ],
            if (location case final currentLocation?) ...[
              const SizedBox(height: 12),
              Text(
                l10n.locationCoordinates(
                  currentLocation.latitude.toStringAsFixed(4),
                  currentLocation.longitude.toStringAsFixed(4),
                ),
              ),
            ],
            const SizedBox(height: 12),
            Text(l10n.modelVersion(result.modelVersion)),
            if (isSavedLocally) ...[
              const SizedBox(height: 8),
              Text(l10n.scanSavedLocally),
            ],
          ],
        ),
      ),
    );
  }
}

String _localizedCrop(AppLocalizations l10n, String crop) => switch (crop) {
      'Tomato' => l10n.cropTomato,
      'Potato' => l10n.cropPotato,
      'Corn' => l10n.cropCorn,
      'Pepper (Bell)' => l10n.cropPepper,
      'Rice' => l10n.cropRice,
      _ => crop,
    };

String _localizedDiseaseName(AppLocalizations l10n, String label) {
  final prefixEnd = label.lastIndexOf('___');
  if (prefixEnd < 0) return label.replaceAll('_', ' ');
  final normalized =
      label.substring(prefixEnd + 3).replaceAll('_', '').toLowerCase();
  return switch (normalized) {
    'healthy' => l10n.diseaseHealthy,
    'bacterialspot' => l10n.diseaseBacterialSpot,
    'earlyblight' => l10n.diseaseEarlyBlight,
    'lateblight' => l10n.diseaseLateBlight,
    'leafmold' => l10n.diseaseLeafMold,
    'septorialeafspot' => l10n.diseaseSeptoriaLeafSpot,
    'spidermitestwospottedspidermite' => l10n.diseaseSpiderMites,
    'targetspot' => l10n.diseaseTargetSpot,
    'tomatoyellowleafcurlvirus' => l10n.diseaseYellowLeafCurlVirus,
    'tomatomosaicvirus' || 'mosaicvirus' => l10n.diseaseMosaicVirus,
    'commonrust' => l10n.diseaseCommonRust,
    'northernleafblight' => l10n.diseaseNorthernLeafBlight,
    'brownspot' => l10n.diseaseBrownSpot,
    'leafblast' => l10n.diseaseLeafBlast,
    _ => label.replaceAll('_', ' '),
  };
}
