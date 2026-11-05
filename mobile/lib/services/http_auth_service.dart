import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../config/app_config.dart';
import 'auth_service.dart';

class HttpAuthService implements AuthService {
  static const _tokenKey = 'agrolens_api_access_token_v1';

  HttpAuthService({
    String? baseUrl,
    http.Client? client,
  })  : _baseUrl = (baseUrl ?? AppConfig.backendBaseUrl).replaceFirst(
          RegExp(r'/$'),
          '',
        ),
        _client = client ?? http.Client();

  final String _baseUrl;
  final http.Client _client;

  @override
  Future<AuthSession?> restoreSession() async {
    final preferences = await SharedPreferences.getInstance();
    final token = preferences.getString(_tokenKey);
    if (token == null || token.isEmpty) return null;

    try {
      final response = await _request('auth/me', token: token);
      return _sessionFrom(response, token);
    } on AuthException {
      await preferences.remove(_tokenKey);
      return null;
    }
  }

  @override
  Future<AuthSession> login({
    required String identifier,
    required String password,
  }) async {
    final response = await _request(
      'auth/login',
      method: 'POST',
      body: {'identifier': identifier.trim(), 'password': password},
    );
    return _saveSession(response);
  }

  @override
  Future<AuthSession> signUp({
    required String username,
    required String email,
    required String password,
  }) async {
    final response = await _request(
      'auth/register',
      method: 'POST',
      body: {
        'username': username.trim(),
        'email': email.trim(),
        'password': password,
      },
    );
    return _saveSession(response);
  }

  @override
  Future<void> signOut() async {
    final preferences = await SharedPreferences.getInstance();
    final token = preferences.getString(_tokenKey);
    if (token != null && token.isNotEmpty) {
      try {
        await _request('auth/logout', method: 'POST', token: token);
      } finally {
        await preferences.remove(_tokenKey);
      }
    }
  }

  Future<AuthSession> _saveSession(Map<String, dynamic> response) async {
    final token = response['access_token'] as String?;
    if (token == null || token.isEmpty) {
      throw const AuthException('The authentication service returned no session token.');
    }
    final preferences = await SharedPreferences.getInstance();
    await preferences.setString(_tokenKey, token);
    return _sessionFrom(response, token);
  }

  AuthSession _sessionFrom(Map<String, dynamic> response, String token) {
    final userRaw = response['user'];
    final user = userRaw is Map
        ? Map<String, dynamic>.from(userRaw)
        : response;
    return AuthSession(
      email: (user['email'] as String?) ?? '',
      username: user['username'] as String?,
      accessToken: token,
    );
  }

  Future<Map<String, dynamic>> _request(
    String path, {
    String method = 'GET',
    String? token,
    Map<String, dynamic>? body,
  }) async {
    final uri = Uri.parse('$_baseUrl/$path');
    final headers = <String, String>{
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-Client-App': AppConfig.appName,
      'X-Client-Version': AppConfig.appVersion,
      if (token != null) 'Authorization': 'Bearer $token',
    };
    final response = method == 'POST'
        ? await _client.post(uri, headers: headers, body: jsonEncode(body))
        : await _client.get(uri, headers: headers);
    if (response.statusCode < 200 || response.statusCode >= 300) {
      var detail = 'The authentication service returned HTTP ${response.statusCode}.';
      try {
        final decoded = jsonDecode(response.body);
        if (decoded is Map && decoded['detail'] is String) {
          detail = decoded['detail'] as String;
        }
      } on FormatException {
        // Keep the HTTP status when the server does not return JSON.
      }
      throw AuthException(detail);
    }
    final decoded = jsonDecode(response.body);
    if (decoded is! Map) {
      throw const AuthException('The authentication service returned invalid data.');
    }
    return Map<String, dynamic>.from(decoded);
  }
}
