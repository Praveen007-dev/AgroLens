import 'dart:async';

import 'package:geolocator/geolocator.dart';

import '../models/scan_record.dart';

enum LocationFailure {
  servicesDisabled,
  permissionDenied,
  permissionDeniedForever,
  positionUnavailable,
}

class LocationServiceException implements Exception {
  const LocationServiceException(this.failure);

  final LocationFailure failure;
}

/// Requests the device location only after the user explicitly asks to use it.
class LocationService {
  Future<ScanLocation> getCurrentLocation() async {
    try {
      if (!await Geolocator.isLocationServiceEnabled()) {
        throw const LocationServiceException(LocationFailure.servicesDisabled);
      }

      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }

      if (permission == LocationPermission.denied) {
        throw const LocationServiceException(LocationFailure.permissionDenied);
      }
      if (permission == LocationPermission.deniedForever) {
        throw const LocationServiceException(
          LocationFailure.permissionDeniedForever,
        );
      }

      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.medium,
          timeLimit: Duration(seconds: 60),
        ),
      );

      return ScanLocation(
        latitude: position.latitude,
        longitude: position.longitude,
        hasConsent: true,
      );
    } on LocationServiceException {
      rethrow;
    } on TimeoutException {
      throw const LocationServiceException(LocationFailure.positionUnavailable);
    } on LocationServiceDisabledException {
      throw const LocationServiceException(LocationFailure.servicesDisabled);
    } on PermissionDeniedException {
      throw const LocationServiceException(LocationFailure.permissionDenied);
    }
  }

  Future<bool> openAppSettings() => Geolocator.openAppSettings();

  Future<bool> openLocationSettings() => Geolocator.openLocationSettings();
}
