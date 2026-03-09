import '../models/leaderboard_entry.dart';
import 'api_client.dart';

/// Leaderboard service — points and gems rankings.
class LeaderboardService {
  final ApiClient _api;

  LeaderboardService(this._api);

  /// GET /leaderboard/points
  Future<List<LeaderboardEntry>> getPointsBoard({
    int limit = 50,
    int offset = 0,
  }) async {
    final res = await _api.dio.get(
      '/leaderboard/points',
      queryParameters: {'limit': limit, 'offset': offset},
    );
    return (res.data as List).map((j) => LeaderboardEntry.fromJson(j)).toList();
  }

  /// GET /leaderboard/gems
  Future<List<LeaderboardEntry>> getGemsBoard({
    int limit = 50,
    int offset = 0,
  }) async {
    final res = await _api.dio.get(
      '/leaderboard/gems',
      queryParameters: {'limit': limit, 'offset': offset},
    );
    return (res.data as List).map((j) => LeaderboardEntry.fromJson(j)).toList();
  }
}
