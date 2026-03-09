// Auth service — login, signup, refresh, profile CRUD.
import '../models/user.dart';
import 'api_client.dart';

/// Authentication service — login, signup, refresh, profile CRUD.
class AuthService {
  final ApiClient _api;

  AuthService(this._api);

  /// POST /auth/signup
  Future<Map<String, dynamic>> signup({
    required String email,
    required String password,
    required String displayName,
  }) async {
    final res = await _api.dio.post(
      '/auth/signup',
      data: {'email': email, 'password': password, 'display_name': displayName},
    );
    await _api.setTokens(res.data['access_token'], res.data['refresh_token']);
    return res.data;
  }

  /// POST /auth/login
  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final res = await _api.dio.post(
      '/auth/login',
      data: {'email': email, 'password': password},
    );
    await _api.setTokens(res.data['access_token'], res.data['refresh_token']);
    return res.data;
  }

  /// GET /auth/profile
  Future<User> getProfile() async {
    final res = await _api.dio.get('/auth/profile');
    return User.fromJson(res.data);
  }

  /// PUT /auth/profile
  Future<User> updateProfile(Map<String, dynamic> fields) async {
    final res = await _api.dio.put('/auth/profile', data: fields);
    return User.fromJson(res.data);
  }

  Future<void> logout() async {
    await _api.clearTokens();
  }
}
