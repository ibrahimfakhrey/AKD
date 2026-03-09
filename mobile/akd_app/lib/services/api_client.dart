import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Dio HTTP client with JWT interceptor and auto-refresh.
class ApiClient {
  // ───────────────────────────────────────────────────────────────────────────
  // BASE URL — change this to match your dev environment:
  //   • iOS Simulator / Desktop       → 'http://localhost:5000/api/v1'
  //   • Android Emulator              → 'http://10.0.2.2:5000/api/v1'
  //   • Real device (same LAN)        → 'http://192.168.1.X:5000/api/v1'
  // ───────────────────────────────────────────────────────────────────────────
  static const String _devBaseUrl = 'http://localhost:5000/api/v1';

  static String get _defaultBaseUrl {
    if (kIsWeb) return 'http://localhost:5000/api/v1';
    return _devBaseUrl;
  }

  static const _storage = FlutterSecureStorage();

  late final Dio dio;
  String? _accessToken;
  String? _refreshToken;

  ApiClient({String? baseUrl}) {
    dio = Dio(
      BaseOptions(
        baseUrl: baseUrl ?? _defaultBaseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {'Content-Type': 'application/json'},
      ),
    );

    dio.interceptors.add(
      InterceptorsWrapper(onRequest: _onRequest, onError: _onError),
    );
  }

  // ---------- Token management ----------

  Future<void> setTokens(String access, String refresh) async {
    _accessToken = access;
    _refreshToken = refresh;
    await _storage.write(key: 'access_token', value: access);
    await _storage.write(key: 'refresh_token', value: refresh);
  }

  Future<void> loadTokens() async {
    _accessToken = await _storage.read(key: 'access_token');
    _refreshToken = await _storage.read(key: 'refresh_token');
  }

  Future<void> clearTokens() async {
    _accessToken = null;
    _refreshToken = null;
    await _storage.deleteAll();
  }

  bool get hasToken => _accessToken != null;

  // ---------- Interceptors ----------

  void _onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (_accessToken != null) {
      options.headers['Authorization'] = 'Bearer $_accessToken';
    }
    handler.next(options);
  }

  Future<void> _onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401 && _refreshToken != null) {
      try {
        final refreshDio = Dio(
          BaseOptions(
            baseUrl: dio.options.baseUrl,
            headers: {'Content-Type': 'application/json'},
          ),
        );

        final res = await refreshDio.post(
          '/auth/refresh',
          options: Options(headers: {'Authorization': 'Bearer $_refreshToken'}),
        );

        final newAccess = res.data['access_token'] as String;
        _accessToken = newAccess;
        await _storage.write(key: 'access_token', value: newAccess);

        // Retry original request with new token
        err.requestOptions.headers['Authorization'] = 'Bearer $newAccess';
        final retryRes = await dio.fetch(err.requestOptions);
        return handler.resolve(retryRes);
      } catch (_) {
        await clearTokens();
      }
    }
    handler.next(err);
  }

  // ---------- Helpers ----------

  String errorMessage(DioException e) {
    if (e.response?.data is Map) {
      return (e.response!.data as Map)['error'] ??
          (e.response!.data as Map)['message'] ??
          'Something went wrong';
    }
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return 'Connection timed out. Check your network.';
    }
    return 'Could not connect to server';
  }
}
