class AuthSession {
  const AuthSession({
    required this.email,
    this.username,
  });

  final String email;
  final String? username;

  String get displayName =>
      username?.trim().isNotEmpty == true ? username! : email;
}

class AuthException implements Exception {
  const AuthException(this.message);

  final String message;

  @override
  String toString() => message;
}

/// UI-facing auth contract; implementations can be swapped for a backend later.
abstract interface class AuthService {
  Future<AuthSession?> restoreSession();
  Future<AuthSession> login({
    required String identifier,
    required String password,
  });
  Future<AuthSession> signUp({
    required String username,
    required String email,
    required String password,
  });
  Future<void> signOut();
}
