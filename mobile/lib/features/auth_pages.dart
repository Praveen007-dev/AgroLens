import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../services/auth_service.dart';

enum _AuthMode { login, signUp, forgotPassword }

class AuthPage extends StatefulWidget {
  const AuthPage({
    super.key,
    required this.authService,
    required this.onAuthenticated,
    this.initialError,
  });

  final AuthService authService;
  final ValueChanged<AuthSession> onAuthenticated;
  final String? initialError;

  @override
  State<AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends State<AuthPage> {
  final _formKey = GlobalKey<FormState>();
  final _identifierController = TextEditingController();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  _AuthMode _mode = _AuthMode.login;
  bool _isPasswordVisible = false;
  bool _isBusy = false;
  String? _error;
  String? _notice;

  @override
  void initState() {
    super.initState();
    _error = widget.initialError;
  }

  @override
  void dispose() {
    _identifierController.dispose();
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _switchMode(_AuthMode mode) {
    setState(() {
      _mode = mode;
      _error = null;
      _notice = null;
      _formKey.currentState?.reset();
    });
  }

  Future<void> _submit() async {
    if (_isBusy || !(_formKey.currentState?.validate() ?? false)) return;
    setState(() {
      _isBusy = true;
      _error = null;
      _notice = null;
    });

    try {
      switch (_mode) {
        case _AuthMode.login:
          final session = await widget.authService.login(
            identifier: _identifierController.text,
            password: _passwordController.text,
          );
          if (mounted) widget.onAuthenticated(session);
        case _AuthMode.signUp:
          final session = await widget.authService.signUp(
            username: _usernameController.text,
            email: _emailController.text,
            password: _passwordController.text,
          );
          if (mounted) widget.onAuthenticated(session);
        case _AuthMode.forgotPassword:
          if (mounted) {
            setState(() {
              _notice =
                  'Password reset is unavailable for locally stored accounts.';
              _mode = _AuthMode.login;
            });
          }
      }
    } on AuthException catch (error) {
      if (mounted) setState(() => _error = error.message);
    } catch (error) {
      if (mounted) {
        setState(
          () => _error =
              '${AppLocalizations.of(context)!.authUnexpectedError} ($error)',
        );
      }
    } finally {
      if (mounted) setState(() => _isBusy = false);
    }
  }

  String? _required(String? value, AppLocalizations l10n) =>
      value == null || value.trim().isEmpty ? l10n.authRequired : null;

  String? _validateEmail(String? value, AppLocalizations l10n) {
    final required = _required(value, l10n);
    if (required != null) return required;
    return RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(value!.trim())
        ? null
        : l10n.authEmailInvalid;
  }

  String? _validatePassword(String? value, AppLocalizations l10n) {
    final required = _required(value, l10n);
    if (required != null) return required;
    return value!.length >= 8 ? null : l10n.authPasswordTooShort;
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final isSignUp = _mode == _AuthMode.signUp;
    final isForgotPassword = _mode == _AuthMode.forgotPassword;

    return Scaffold(
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) => SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minHeight: constraints.maxHeight - 48,
              ),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 460),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Center(
                        child: Container(
                          width: 68,
                          height: 68,
                          decoration: BoxDecoration(
                            color: const Color(0xFFE7F1E5),
                            borderRadius: BorderRadius.circular(22),
                          ),
                          child: const Icon(
                            Icons.eco_rounded,
                            color: Color(0xFF356B46),
                            size: 38,
                          ),
                        ),
                      ),
                      const SizedBox(height: 18),
                      Text(
                        l10n.appTitle,
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.headlineSmall
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        isForgotPassword
                            ? l10n.authResetPasswordSubtitle
                            : l10n.authWelcomeSubtitle,
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                              color: const Color(0xFF5C665D),
                            ),
                      ),
                      const SizedBox(height: 26),
                      Card(
                        color: Colors.white,
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(24),
                          side: const BorderSide(color: Color(0xFFE3E9DF)),
                        ),
                        child: Padding(
                          padding: const EdgeInsets.all(22),
                          child: Form(
                            key: _formKey,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                Text(
                                  isForgotPassword
                                      ? l10n.authResetPasswordTitle
                                      : isSignUp
                                          ? l10n.authCreateAccount
                                          : l10n.authWelcomeTitle,
                                  style: Theme.of(context)
                                      .textTheme
                                      .titleLarge
                                      ?.copyWith(fontWeight: FontWeight.w700),
                                ),
                                const SizedBox(height: 20),
                                if (isSignUp) ...[
                                  _textField(
                                    key: const Key('auth-username'),
                                    controller: _usernameController,
                                    label: l10n.authUsername,
                                    icon: Icons.person_outline,
                                    validator: (value) =>
                                        _required(value, l10n),
                                  ),
                                  const SizedBox(height: 14),
                                  _emailField(l10n),
                                  const SizedBox(height: 14),
                                ] else if (isForgotPassword) ...[
                                  _emailField(l10n),
                                  const SizedBox(height: 14),
                                ] else ...[
                                  _textField(
                                    key: const Key('auth-identifier'),
                                    controller: _identifierController,
                                    label: l10n.authIdentifier,
                                    icon: Icons.person_outline,
                                    keyboardType: TextInputType.emailAddress,
                                    validator: (value) =>
                                        _required(value, l10n),
                                  ),
                                  const SizedBox(height: 14),
                                ],
                                if (!isForgotPassword) ...[
                                  _passwordField(
                                    key: const Key('auth-password'),
                                    controller: _passwordController,
                                    label: l10n.authPassword,
                                    l10n: l10n,
                                    validator: isSignUp
                                        ? (value) =>
                                            _validatePassword(value, l10n)
                                        : (value) => _required(value, l10n),
                                  ),
                                  if (isSignUp) ...[
                                    const SizedBox(height: 14),
                                    _passwordField(
                                      key: const Key('auth-confirm-password'),
                                      controller: _confirmPasswordController,
                                      label: l10n.authConfirmPassword,
                                      l10n: l10n,
                                      validator: (value) {
                                        final required =
                                            _required(value, l10n);
                                        if (required != null) return required;
                                        return value == _passwordController.text
                                            ? null
                                            : l10n.authPasswordMismatch;
                                      },
                                    ),
                                  ],
                                ],
                                if (!isSignUp && !isForgotPassword)
                                  Align(
                                    alignment: Alignment.centerRight,
                                    child: TextButton(
                                      key: const Key('auth-forgot-password'),
                                      onPressed: _isBusy
                                          ? null
                                          : () => _switchMode(
                                                _AuthMode.forgotPassword,
                                              ),
                                      child: Text(l10n.authForgotPassword),
                                    ),
                                  ),
                                if (_error case final error?) ...[
                                  const SizedBox(height: 8),
                                  _MessageBanner(message: error, isError: true),
                                ],
                                if (_notice case final notice?) ...[
                                  const SizedBox(height: 8),
                                  _MessageBanner(
                                    message: notice,
                                    isError: false,
                                  ),
                                ],
                                const SizedBox(height: 16),
                                FilledButton(
                                  key: const Key('auth-submit'),
                                  onPressed: _isBusy ? null : _submit,
                                  style: FilledButton.styleFrom(
                                    minimumSize: const Size.fromHeight(54),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(16),
                                    ),
                                  ),
                                  child: _isBusy
                                      ? Row(
                                          mainAxisSize: MainAxisSize.min,
                                          children: [
                                            SizedBox(
                                              height: 22,
                                              width: 22,
                                              child:
                                                  CircularProgressIndicator(
                                                strokeWidth: 2,
                                                color: Theme.of(context)
                                                    .colorScheme
                                                    .onPrimary,
                                              ),
                                            ),
                                            const SizedBox(width: 12),
                                            Text(
                                              isForgotPassword
                                                  ? l10n.authSendingReset
                                                  : isSignUp
                                                      ? l10n.authCreatingAccount
                                                      : l10n.authLoggingIn,
                                            ),
                                          ],
                                        )
                                      : Text(
                                          isForgotPassword
                                              ? l10n.authSendResetLink
                                              : isSignUp
                                                  ? l10n.authSignUp
                                                  : l10n.authLogin,
                                        ),
                                ),
                                const SizedBox(height: 12),
                                Center(
                                  child: TextButton(
                                    onPressed: _isBusy
                                        ? null
                                        : () => _switchMode(
                                              isForgotPassword ||
                                                      isSignUp
                                                  ? _AuthMode.login
                                                  : _AuthMode.signUp,
                                            ),
                                    child: Text(
                                      isForgotPassword
                                          ? l10n.authBackToLogin
                                          : isSignUp
                                              ? l10n.authHaveAccount
                                              : '${l10n.authNoAccount} ${l10n.authSignUp}',
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _emailField(AppLocalizations l10n) => _textField(
        key: const Key('auth-email'),
        controller: _emailController,
        label: l10n.authEmail,
        icon: Icons.email_outlined,
        keyboardType: TextInputType.emailAddress,
        validator: (value) => _validateEmail(value, l10n),
      );

  Widget _passwordField({
    required Key key,
    required TextEditingController controller,
    required String label,
    required AppLocalizations l10n,
    required FormFieldValidator<String> validator,
  }) =>
      TextFormField(
        key: key,
        controller: controller,
        obscureText: !_isPasswordVisible,
        validator: validator,
        textInputAction: TextInputAction.next,
        decoration: InputDecoration(
          labelText: label,
          prefixIcon: const Icon(Icons.lock_outline),
          suffixIcon: IconButton(
            tooltip: _isPasswordVisible
                ? l10n.authHidePassword
                : l10n.authShowPassword,
            onPressed: () =>
                setState(() => _isPasswordVisible = !_isPasswordVisible),
            icon: Icon(
              _isPasswordVisible
                  ? Icons.visibility_off_outlined
                  : Icons.visibility_outlined,
            ),
          ),
        ),
      );

  Widget _textField({
    required Key key,
    required TextEditingController controller,
    required String label,
    required IconData icon,
    required FormFieldValidator<String> validator,
    TextInputType? keyboardType,
  }) =>
      TextFormField(
        key: key,
        controller: controller,
        validator: validator,
        keyboardType: keyboardType,
        textInputAction: TextInputAction.next,
        autocorrect: false,
        decoration: InputDecoration(
          labelText: label,
          prefixIcon: Icon(icon),
        ),
      );
}

class _MessageBanner extends StatelessWidget {
  const _MessageBanner({required this.message, required this.isError});

  final String message;
  final bool isError;

  @override
  Widget build(BuildContext context) {
    final color = isError ? const Color(0xFFB3261E) : const Color(0xFF356B46);
    return Container(
      key: Key(isError ? 'auth-error' : 'auth-notice'),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            isError ? Icons.error_outline : Icons.check_circle_outline,
            color: color,
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(child: Text(message, style: TextStyle(color: color))),
        ],
      ),
    );
  }
}
