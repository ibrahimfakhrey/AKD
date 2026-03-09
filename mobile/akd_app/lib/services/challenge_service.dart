import 'package:dio/dio.dart';
import '../models/challenge.dart';
import 'api_client.dart';

/// Challenge service — start, submit, send to friends, list timed challenges.
class ChallengeService {
  final ApiClient _api;

  ChallengeService(this._api);

  /// POST /challenges/start — start a self-challenge (costs 10 pts)
  Future<Challenge> start({String? description}) async {
    final res = await _api.dio.post(
      '/challenges/start',
      data: {if (description != null) 'description': description},
    );
    return Challenge.fromJson(res.data);
  }

  /// POST /challenges/send — send a challenge to a friend (costs 50 pts)
  Future<Challenge> sendToFriend(
    String friendEmail, {
    String? description,
  }) async {
    final res = await _api.dio.post(
      '/challenges/send',
      data: {
        'friend_email': friendEmail,
        if (description != null) 'description': description,
      },
    );
    return Challenge.fromJson(res.data);
  }

  /// GET /challenges/active
  Future<Challenge?> getActive() async {
    final res = await _api.dio.get('/challenges/active');
    if (res.data == null) return null;
    return Challenge.fromJson(res.data);
  }

  /// GET /challenges/received — challenges sent to you by friends
  Future<List<Challenge>> getReceived() async {
    final res = await _api.dio.get('/challenges/received');
    return (res.data as List).map((j) => Challenge.fromJson(j)).toList();
  }

  /// POST /challenges/<id>/submit
  Future<Map<String, dynamic>> submitProof(
    String challengeId,
    List<int> bytes,
    String filename,
  ) async {
    final formData = FormData.fromMap({
      'photo': MultipartFile.fromBytes(bytes, filename: filename),
    });
    final res = await _api.dio.post(
      '/challenges/$challengeId/submit',
      data: formData,
      options: Options(contentType: 'multipart/form-data'),
    );
    return res.data;
  }

  /// GET /challenges/
  Future<List<Challenge>> listHistory() async {
    final res = await _api.dio.get('/challenges/');
    return (res.data as List).map((j) => Challenge.fromJson(j)).toList();
  }
}
