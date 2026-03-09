import '../models/friend.dart';
import 'api_client.dart';

/// Friend service — send/accept requests, list friends.
class FriendService {
  final ApiClient _api;

  FriendService(this._api);

  /// POST /friends/request
  Future<Map<String, dynamic>> sendRequest(String friendEmail) async {
    final res = await _api.dio.post(
      '/friends/request',
      data: {'friend_email': friendEmail},
    );
    return res.data;
  }

  /// POST /friends/<id>/accept
  Future<Map<String, dynamic>> acceptRequest(String requestId) async {
    final res = await _api.dio.post('/friends/$requestId/accept');
    return res.data;
  }

  /// DELETE /friends/<id>
  Future<void> removeFriend(String requestId) async {
    await _api.dio.delete('/friends/$requestId');
  }

  /// GET /friends/list
  Future<List<FriendEntry>> listFriends() async {
    final res = await _api.dio.get('/friends/list');
    return (res.data as List).map((j) => FriendEntry.fromJson(j)).toList();
  }

  /// GET /friends/pending
  Future<List<PendingRequest>> pendingRequests() async {
    final res = await _api.dio.get('/friends/pending');
    return (res.data as List).map((j) => PendingRequest.fromJson(j)).toList();
  }
}
