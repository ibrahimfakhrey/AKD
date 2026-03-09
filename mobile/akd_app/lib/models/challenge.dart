/// Challenge model — timed kindness challenges.
class Challenge {
  final String id;
  final String userId;
  final String? description;
  final String startedAt;
  final String expiresAt;
  String status; // active | completed | failed | expired | pending_review
  final int costPoints;
  final String? proofId;
  final bool rewardGiven;
  final String challengeType; // 'self' | 'received'
  final String? senderId;
  final String? recipientId;

  Challenge({
    required this.id,
    required this.userId,
    this.description,
    required this.startedAt,
    required this.expiresAt,
    this.status = 'active',
    this.costPoints = 10,
    this.proofId,
    this.rewardGiven = false,
    this.challengeType = 'self',
    this.senderId,
    this.recipientId,
  });

  factory Challenge.fromJson(Map<String, dynamic> json) {
    return Challenge(
      id: json['id'],
      userId: json['user_id'] ?? '',
      description: json['description'],
      startedAt: json['started_at'] ?? '',
      expiresAt: json['expires_at'] ?? '',
      status: json['status'] ?? 'active',
      costPoints: json['cost_points'] ?? 10,
      proofId: json['proof_id'],
      rewardGiven: json['reward_given'] ?? false,
      challengeType: json['challenge_type'] ?? 'self',
      senderId: json['sender_id'],
      recipientId: json['recipient_id'],
    );
  }

  bool get isActive => status == 'active';
  bool get isCompleted => status == 'completed';
  bool get isReceived => challengeType == 'received';

  DateTime _parseUtc(String dtStr) {
    if (!dtStr.endsWith('Z')) return DateTime.parse('${dtStr}Z');
    return DateTime.parse(dtStr);
  }

  DateTime get expiresAtDateTime => _parseUtc(expiresAt);
  DateTime get startedAtDateTime => _parseUtc(startedAt);

  Duration get timeRemaining {
    final expires = expiresAtDateTime;
    final now = DateTime.now().toUtc();
    final diff = expires.difference(now);
    return diff.isNegative ? Duration.zero : diff;
  }
}
