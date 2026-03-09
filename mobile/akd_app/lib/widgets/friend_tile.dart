import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

/// Friend tile with avatar, name, and action button.
class FriendTile extends StatelessWidget {
  final String displayName;
  final String? avatarUrl;
  final String? subtitle;
  final Widget? trailing;
  final Color? nameColor;

  const FriendTile({
    super.key,
    required this.displayName,
    this.avatarUrl,
    this.subtitle,
    this.nameColor,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.lightCard,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 22,
            backgroundColor: AppColors.coral.withValues(alpha: 0.2),
            backgroundImage: avatarUrl != null
                ? NetworkImage(avatarUrl!)
                : null,
            child: avatarUrl == null
                ? Text(
                    displayName.isNotEmpty ? displayName[0].toUpperCase() : '?',
                    style: const TextStyle(
                      color: AppColors.coral,
                      fontWeight: FontWeight.w700,
                    ),
                  )
                : null,
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  displayName,
                  style: Theme.of(
                    context,
                  ).textTheme.titleMedium?.copyWith(color: nameColor),
                ),
                if (subtitle != null)
                  Text(subtitle!, style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}
