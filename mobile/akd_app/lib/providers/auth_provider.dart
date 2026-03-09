import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import '../models/user.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';

/// Auth state provider — manages login/signup/logout and current user.
class AuthProvider extends ChangeNotifier {
  final ApiClient api;
  late final AuthService _authService;

  User? _user;
  bool _loading = true;
  String? _error;

  AuthProvider({required this.api}) {
    _authService = AuthService(api);
    _tryAutoLogin();
  }

  User? get user => _user;
  bool get isLoggedIn => _user != null;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> _tryAutoLogin() async {
    try {
      await api.loadTokens();
      if (api.hasToken) {
        _user = await _authService.getProfile();
      }
    } catch (_) {
      await api.clearTokens();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<bool> login(String email, String password) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      final data = await _authService.login(email: email, password: password);
      _user = User.fromJson(data['user']);
      _loading = false;
      notifyListeners();
      return true;
    } on DioException catch (e) {
      _error = api.errorMessage(e);
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> signup(String email, String password, String displayName) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      final data = await _authService.signup(
        email: email,
        password: password,
        displayName: displayName,
      );
      _user = User.fromJson(data['user']);
      _loading = false;
      notifyListeners();
      return true;
    } on DioException catch (e) {
      _error = api.errorMessage(e);
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> refreshProfile() async {
    try {
      _user = await _authService.getProfile();
      notifyListeners();
    } catch (_) {}
  }

  Future<void> updateProfile(Map<String, dynamic> fields) async {
    try {
      _user = await _authService.updateProfile(fields);
      notifyListeners();
    } on DioException catch (e) {
      _error = api.errorMessage(e);
      notifyListeners();
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    _user = null;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
