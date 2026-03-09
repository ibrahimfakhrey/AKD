import 'package:flutter/material.dart';
import '../models/quest.dart';
import '../theme/app_colors.dart';

/// Animated quest card with status indicator and gradient border.
class QuestCard extends StatelessWidget {
  final DailyQuest dailyQuest;
  final VoidCallback? onTap;

  const QuestCard({super.key, required this.dailyQuest, this.onTap});

  @override
  Widget build(BuildContext context) {
    final quest = dailyQuest.quest;
    final isCompleted = dailyQuest.isCompleted;
    final isPending = dailyQuest.isPendingReview;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: isCompleted
                ? [
                    AppColors.success.withValues(alpha: 0.15),
                    AppColors.lightCard,
                  ]
                : isPending
                ? [
                    AppColors.warning.withValues(alpha: 0.15),
                    AppColors.lightCard,
                  ]
                : [
                    AppColors.coral.withValues(alpha: 0.08),
                    AppColors.lightCard,
                  ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isCompleted
                ? AppColors.success.withValues(alpha: 0.3)
                : isPending
                ? AppColors.warning.withValues(alpha: 0.3)
                : AppColors.inputBg,
            width: 1,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Row(
            children: [
              // Status icon
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: isCompleted
                      ? AppColors.success.withValues(alpha: 0.2)
                      : isPending
                      ? AppColors.warning.withValues(alpha: 0.2)
                      : AppColors.coral.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(
                  isCompleted
                      ? Icons.check_circle_rounded
                      : isPending
                      ? Icons.hourglass_top_rounded
                      : Icons.volunteer_activism_rounded,
                  color: isCompleted
                      ? AppColors.success
                      : isPending
                      ? AppColors.warning
                      : AppColors.coral,
                  size: 26,
                ),
              ),
              const SizedBox(width: 14),
              // Text content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      quest?.title ?? 'Quest',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        decoration: isCompleted
                            ? TextDecoration.lineThrough
                            : null,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      quest?.description ?? '',
                      style: Theme.of(context).textTheme.bodySmall,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              // Reward badge
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: AppColors.pointsGold.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.star_rounded,
                      color: AppColors.pointsGold,
                      size: 16,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${quest?.rewardPoints ?? 10}',
                      style: Theme.of(context).textTheme.labelLarge?.copyWith(
                        color: AppColors.pointsGold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
