import 'package:flutter/material.dart';
import '../models/leaderboard_entry.dart';
import '../theme/app_colors.dart';

/// Leaderboard row — rank medal, avatar, name, value.
class LeaderboardRow extends StatelessWidget {
  final LeaderboardEntry entry;
  final bool isGems; // false = points

  const LeaderboardRow({super.key, required this.entry, this.isGems = false});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 3),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: entry.rank <= 3
            ? _topColors[entry.rank]!.withValues(alpha: 0.08)
            : AppColors.lightCard,
        borderRadius: BorderRadius.circular(14),
        border: entry.rank <= 3
            ? Border.all(
                color: _topColors[entry.rank]!.withValues(alpha: 0.25),
                width: 1,
              )
            : null,
      ),
      child: Row(
        children: [
          // Rank
          SizedBox(
            width: 32,
            child: entry.rank <= 3
                ? Icon(
                    _medals[entry.rank],
                    color: _topColors[entry.rank],
                    size: 24,
                  )
                : Text(
                    '${entry.rank}',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
          ),
          const SizedBox(width: 12),
          // Avatar
          CircleAvatar(
            radius: 18,
            backgroundColor: AppColors.coral.withValues(alpha: 0.2),
            backgroundImage: entry.avatarUrl != null
                ? NetworkImage(entry.avatarUrl!)
                : null,
            child: entry.avatarUrl == null
                ? Text(
                    entry.displayName.isNotEmpty
                        ? entry.displayName[0].toUpperCase()
                        : '?',
                    style: const TextStyle(
                      color: AppColors.coral,
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  )
                : null,
          ),
          const SizedBox(width: 12),
          // Name
          Expanded(
            child: Text(
              entry.displayName,
              style: Theme.of(context).textTheme.titleMedium,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          // Value
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                isGems ? Icons.diamond_rounded : Icons.star_rounded,
                color: isGems ? AppColors.gemBlue : AppColors.pointsGold,
                size: 16,
              ),
              const SizedBox(width: 4),
              Text(
                '${entry.value}',
                style: TextStyle(
                  color: isGems ? AppColors.gemBlue : AppColors.pointsGold,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  static const _medals = {
    1: Icons.emoji_events_rounded,
    2: Icons.emoji_events_rounded,
    3: Icons.emoji_events_rounded,
  };

  static const _topColors = {
    1: Color(0xFFFFD700),
    2: Color(0xFFC0C0C0),
    3: Color(0xFFCD7F32),
  };
}
