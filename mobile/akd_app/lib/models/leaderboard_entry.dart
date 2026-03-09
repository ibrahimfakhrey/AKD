/// Leaderboard entry — points or gems ranking row.
class LeaderboardEntry {
  final int rank;
  final String userId;
  final String displayName;
  final String? avatarUrl;
  final int value; // points or gems depending on board

  LeaderboardEntry({
    required this.rank,
    required this.userId,
    required this.displayName,
    this.avatarUrl,
    required this.value,
  });

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json) {
    return LeaderboardEntry(
      rank: json['rank'] ?? 0,
      userId: json['user_id'] ?? json['id'] ?? '',
      displayName: json['display_name'] ?? '',
      avatarUrl: json['avatar_url'],
      value: json['points'] ?? json['gems'] ?? 0,
    );
  }
}
