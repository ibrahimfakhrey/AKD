/// Quest master record and DailyQuest per-user instance.
class Quest {
  final String id;
  final String title;
  final String description;
  final String? category;
  final String difficultyHint;
  final int rewardPoints;
  final bool active;
  final String createdAt;

  Quest({
    required this.id,
    required this.title,
    required this.description,
    this.category,
    this.difficultyHint = 'easy',
    this.rewardPoints = 10,
    this.active = true,
    required this.createdAt,
  });

  factory Quest.fromJson(Map<String, dynamic> json) {
    return Quest(
      id: json['id'],
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      category: json['category'],
      difficultyHint: json['difficulty_hint'] ?? 'easy',
      rewardPoints: json['reward_points'] ?? 10,
      active: json['active'] ?? true,
      createdAt: json['created_at'] ?? '',
    );
  }
}

class DailyQuest {
  final String id;
  final String userId;
  final String questId;
  final Quest? quest;
  final String date;
  final String status; // assigned | pending_review | completed | rejected
  final String? proofId;
  final bool rewardAwarded;

  DailyQuest({
    required this.id,
    required this.userId,
    required this.questId,
    this.quest,
    required this.date,
    this.status = 'assigned',
    this.proofId,
    this.rewardAwarded = false,
  });

  factory DailyQuest.fromJson(Map<String, dynamic> json) {
    return DailyQuest(
      id: json['id'],
      userId: json['user_id'] ?? '',
      questId: json['quest_id'] ?? '',
      quest: json['quest'] != null ? Quest.fromJson(json['quest']) : null,
      date: json['date'] ?? '',
      status: json['status'] ?? 'assigned',
      proofId: json['proof_id'],
      rewardAwarded: json['reward_awarded'] ?? false,
    );
  }

  bool get isCompleted => status == 'completed';
  bool get isPendingReview => status == 'pending_review';
  bool get isAssigned => status == 'assigned';

  String get statusLabel {
    switch (status) {
      case 'completed':
        return 'Completed ✓';
      case 'pending_review':
        return 'Under Review';
      case 'rejected':
        return 'Rejected';
      default:
        return 'To Do';
    }
  }
}
