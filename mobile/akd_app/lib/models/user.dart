/// User model matching backend User.to_dict() JSON response.
class User {
  final String id;
  final String displayName;
  final String? email;
  final String? avatarUrl;
  final String? bio;
  final int points;
  final int gems;
  final Map<String, dynamic>? equippedCosmetics;
  final Map<String, dynamic>? privacySettings;
  final bool? isAdmin;
  final bool? isBanned;
  final bool? isVerifiedEmail;
  final String createdAt;
  final String? lastActiveAt;

  User({
    required this.id,
    required this.displayName,
    this.email,
    this.avatarUrl,
    this.bio,
    this.points = 0,
    this.gems = 0,
    this.equippedCosmetics,
    this.privacySettings,
    this.isAdmin,
    this.isBanned,
    this.isVerifiedEmail,
    required this.createdAt,
    this.lastActiveAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      displayName: json['display_name'] ?? '',
      email: json['email'],
      avatarUrl: json['avatar_url'],
      bio: json['bio'],
      points: json['points'] ?? 0,
      gems: json['gems'] ?? 0,
      equippedCosmetics: json['equipped_cosmetics'] != null
          ? Map<String, dynamic>.from(json['equipped_cosmetics'])
          : null,
      privacySettings: json['privacy_settings'] != null
          ? Map<String, dynamic>.from(json['privacy_settings'])
          : null,
      isAdmin: json['is_admin'],
      isBanned: json['is_banned'],
      isVerifiedEmail: json['is_verified_email'],
      createdAt: json['created_at'] ?? '',
      lastActiveAt: json['last_active_at'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'display_name': displayName,
      'email': email,
      'avatar_url': avatarUrl,
      'bio': bio,
      'points': points,
      'gems': gems,
      'equipped_cosmetics': equippedCosmetics,
    };
  }
}
