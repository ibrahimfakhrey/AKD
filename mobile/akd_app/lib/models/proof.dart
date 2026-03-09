/// Proof model — photo evidence for quests and challenges.
class Proof {
  final String id;
  final String userId;
  final String fileUrl;
  final String? thumbnailUrl;
  final String uploadTime;
  final Map<String, dynamic>? aiVerificationResult;
  final bool verified;
  final String? verifier;
  final double? verifierConfidence;

  Proof({
    required this.id,
    required this.userId,
    required this.fileUrl,
    this.thumbnailUrl,
    required this.uploadTime,
    this.aiVerificationResult,
    this.verified = false,
    this.verifier,
    this.verifierConfidence,
  });

  factory Proof.fromJson(Map<String, dynamic> json) {
    return Proof(
      id: json['id'],
      userId: json['user_id'] ?? '',
      fileUrl: json['file_url'] ?? '',
      thumbnailUrl: json['thumbnail_url'],
      uploadTime: json['upload_time'] ?? '',
      aiVerificationResult: json['ai_verification_result'] != null
          ? Map<String, dynamic>.from(json['ai_verification_result'])
          : null,
      verified: json['verified'] ?? false,
      verifier: json['verifier'],
      verifierConfidence: (json['verifier_confidence'] as num?)?.toDouble(),
    );
  }
}
