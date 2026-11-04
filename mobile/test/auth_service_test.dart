import 'dart:convert';

import 'package:agrolens/services/auth_service.dart';
import 'package:agrolens/services/local_auth_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  test('registers then logs in with email or username', () async {
    final service = LocalAuthService();
    final registered = await service.signUp(
      username: 'FarmUser',
      email: 'Farmer@Example.test',
      password: 'secure-password',
    );

    expect(registered.email, 'farmer@example.test');
    expect(registered.displayName, 'FarmUser');
    expect(
      (await service.login(
        identifier: 'farmer@example.test',
        password: 'secure-password',
      ))
          .email,
      'farmer@example.test',
    );
    expect(
      (await service.login(
        identifier: 'FARMUSER',
        password: 'secure-password',
      ))
          .username,
      'FarmUser',
    );
  });

  test('persists account and session across service instances', () async {
    final service = LocalAuthService();
    await service.signUp(
      username: 'Farmer',
      email: 'farmer@example.test',
      password: 'secure-password',
    );

    final restored = await LocalAuthService().restoreSession();
    expect(restored?.email, 'farmer@example.test');
    expect(restored?.username, 'Farmer');
  });

  test('logout clears only the session and leaves the account available', () async {
    final service = LocalAuthService();
    await service.signUp(
      username: 'Farmer',
      email: 'farmer@example.test',
      password: 'secure-password',
    );

    await service.signOut();
    expect(await service.restoreSession(), isNull);
    expect(
      (await service.login(
        identifier: 'Farmer',
        password: 'secure-password',
      ))
          .email,
      'farmer@example.test',
    );
  });

  test('rejects duplicate email and username without overwriting account',
      () async {
    final service = LocalAuthService();
    await service.signUp(
      username: 'Farmer',
      email: 'farmer@example.test',
      password: 'secure-password',
    );

    await expectLater(
      service.signUp(
        username: 'Another',
        email: 'FARMER@example.test',
        password: 'another-password',
      ),
      throwsA(isA<AuthException>()),
    );
    await expectLater(
      service.signUp(
        username: 'FARMER',
        email: 'another@example.test',
        password: 'another-password',
      ),
      throwsA(isA<AuthException>()),
    );
    expect(
      (await service.login(
        identifier: 'Farmer',
        password: 'secure-password',
      ))
          .email,
      'farmer@example.test',
    );
  });

  test('rejects invalid credentials and does not create a session', () async {
    final service = LocalAuthService();
    await service.signUp(
      username: 'Farmer',
      email: 'farmer@example.test',
      password: 'secure-password',
    );
    await service.signOut();

    await expectLater(
      service.login(
        identifier: 'farmer@example.test',
        password: 'incorrect-password',
      ),
      throwsA(isA<AuthException>()),
    );
    expect(await service.restoreSession(), isNull);
  });

  test('validates account data in the service layer', () async {
    final service = LocalAuthService();
    await expectLater(
      service.signUp(
        username: 'Farmer',
        email: 'not-an-email',
        password: 'secure-password',
      ),
      throwsA(isA<AuthException>()),
    );
    await expectLater(
      service.signUp(
        username: 'Farmer',
        email: 'farmer@example.test',
        password: 'short',
      ),
      throwsA(isA<AuthException>()),
    );
  });

  test('stores salted password hashes, not plaintext passwords', () async {
    final service = LocalAuthService();
    await service.signUp(
      username: 'Farmer',
      email: 'farmer@example.test',
      password: 'secure-password',
    );
    final preferences = await SharedPreferences.getInstance();
    final accounts =
        jsonDecode(preferences.getString('agrolens_local_accounts_v1')!)
            as List<dynamic>;
    final account = accounts.single as Map<String, dynamic>;

    expect(account['password_hash'], isNot('secure-password'));
    expect(account['salt'], isNotEmpty);
    expect(account['password_hash'], isNot(account['salt']));
  });
}
