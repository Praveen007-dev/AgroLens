import 'dart:convert';
import 'dart:math';

import 'package:crypto/crypto.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'auth_service.dart';

/// Development-only authentication backed by local device preferences.
///
/// Passwords are salted and hashed, but this local store is not a substitute
/// for production authentication or server-side password protection.
class LocalAuthService implements AuthService {
  static const _accountsKey = 'agrolens_local_accounts_v1';
  static const _sessionKey = 'agrolens_local_session_v1';

  @override
  Future<AuthSession?> restoreSession() async {
    final preferences = await SharedPreferences.getInstance();
    final email = preferences.getString(_sessionKey);
    if (email == null || email.isEmpty) return null;

    final account = (await _readAccounts(preferences)).where(
      (item) => item['email'] == email,
    );
    if (account.isEmpty) {
      await preferences.remove(_sessionKey);
      return null;
    }
    return _sessionFrom(account.first);
  }

  @override
  Future<AuthSession> signUp({
    required String username,
    required String email,
    required String password,
  }) async {
    final normalizedUsername = username.trim();
    final normalizedEmail = email.trim().toLowerCase();
    if (normalizedUsername.isEmpty) {
      throw const AuthException('Enter a username.');
    }
    if (!_validEmail.hasMatch(normalizedEmail)) {
      throw const AuthException('Enter a valid email address.');
    }
    if (password.length < 8) {
      throw const AuthException('Use a password with at least 8 characters.');
    }

    final preferences = await SharedPreferences.getInstance();
    final accounts = await _readAccounts(preferences);
    final normalizedUsernameKey = normalizedUsername.toLowerCase();
    if (accounts.any(
      (account) =>
          account['email'] == normalizedEmail ||
          (account['username'] as String).toLowerCase() ==
              normalizedUsernameKey,
    )) {
      throw const AuthException(
        'An account with that email or username already exists.',
      );
    }

    final salt = _newSalt();
    final account = <String, dynamic>{
      'email': normalizedEmail,
      'username': normalizedUsername,
      'salt': salt,
      'password_hash': _passwordHash(password, salt),
    };
    accounts.add(account);
    await preferences.setString(_accountsKey, jsonEncode(accounts));
    await preferences.setString(_sessionKey, normalizedEmail);
    return _sessionFrom(account);
  }

  @override
  Future<AuthSession> login({
    required String identifier,
    required String password,
  }) async {
    final normalizedIdentifier = identifier.trim().toLowerCase();
    if (normalizedIdentifier.isEmpty || password.isEmpty) {
      throw const AuthException('Enter your email/username and password.');
    }

    final preferences = await SharedPreferences.getInstance();
    final accounts = await _readAccounts(preferences);
    for (final account in accounts) {
      final email = account['email'] as String;
      final username = (account['username'] as String).toLowerCase();
      if (normalizedIdentifier == email || normalizedIdentifier == username) {
        final salt = account['salt'] as String;
        if (_passwordHash(password, salt) != account['password_hash']) {
          break;
        }
        await preferences.setString(_sessionKey, email);
        return _sessionFrom(account);
      }
    }
    throw const AuthException('The email/username or password is incorrect.');
  }

  @override
  Future<void> signOut() async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.remove(_sessionKey);
  }

  Future<List<Map<String, dynamic>>> _readAccounts(
    SharedPreferences preferences,
  ) {
    final encoded = preferences.getString(_accountsKey);
    if (encoded == null) {
      return Future.value(<Map<String, dynamic>>[]);
    }
    try {
      final decoded = jsonDecode(encoded);
      if (decoded is! List) throw const FormatException();
      return Future.value(
        decoded.map((item) => Map<String, dynamic>.from(item as Map)).toList(),
      );
    } on FormatException {
      throw const AuthException(
        'Local account data is unreadable. Clear app data and sign up again.',
      );
    } on TypeError {
      throw const AuthException(
        'Local account data is unreadable. Clear app data and sign up again.',
      );
    }
  }

  static AuthSession _sessionFrom(Map<String, dynamic> account) => AuthSession(
        email: account['email'] as String,
        username: account['username'] as String?,
      );

  static String _newSalt() {
    final random = Random.secure();
    return base64UrlEncode(List<int>.generate(16, (_) => random.nextInt(256)));
  }

  static String _passwordHash(String password, String salt) =>
      sha256.convert(utf8.encode('$salt:$password')).toString();

  static final _validEmail = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');
}
