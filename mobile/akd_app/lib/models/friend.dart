import 'user.dart';

/// Friend entry model — accepted friendships and pending requests.
class FriendEntry {
  final String friendshipId;
  final String status;
  final User? friend;
  final String createdAt;

  FriendEntry({
    required this.friendshipId,
    required this.status,
    this.friend,
    required this.createdAt,
  });

  factory FriendEntry.fromJson(Map<String, dynamic> json) {
    return FriendEntry(
      friendshipId: json['friendship_id'] ?? '',
      status: json['status'] ?? 'requested',
      friend: json['friend'] != null ? User.fromJson(json['friend']) : null,
      createdAt: json['created_at'] ?? '',
    );
  }
}

class PendingRequest {
  final String friendshipId;
  final User? requester;
  final String createdAt;

  PendingRequest({
    required this.friendshipId,
    this.requester,
    required this.createdAt,
  });

  factory PendingRequest.fromJson(Map<String, dynamic> json) {
    return PendingRequest(
      friendshipId: json['friendship_id'] ?? '',
      requester: json['requester'] != null
          ? User.fromJson(json['requester'])
          : null,
      createdAt: json['created_at'] ?? '',
    );
  }
}
