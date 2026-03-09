import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

/// Countdown timer widget for challenges — circular progress + time text.
class CountdownTimer extends StatelessWidget {
  final Duration remaining;
  final Duration total;

  const CountdownTimer({
    super.key,
    required this.remaining,
    required this.total,
  });

  @override
  Widget build(BuildContext context) {
    final progress = total.inSeconds > 0
        ? remaining.inSeconds / total.inSeconds
        : 0.0;
    final minutes = remaining.inMinutes
        .remainder(60)
        .toString()
        .padLeft(2, '0');
    final seconds = remaining.inSeconds
        .remainder(60)
        .toString()
        .padLeft(2, '0');
    final hours = remaining.inHours;

    return SizedBox(
      width: 160,
      height: 160,
      child: Stack(
        alignment: Alignment.center,
        children: [
          SizedBox(
            width: 140,
            height: 140,
            child: CircularProgressIndicator(
              value: progress,
              strokeWidth: 8,
              strokeCap: StrokeCap.round,
              backgroundColor: AppColors.inputBg,
              valueColor: AlwaysStoppedAnimation(
                progress > 0.3 ? AppColors.teal : AppColors.error,
              ),
            ),
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                hours > 0 ? '$hours:$minutes:$seconds' : '$minutes:$seconds',
                style: Theme.of(context).textTheme.displayMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: progress > 0.3
                      ? AppColors.textPrimary
                      : AppColors.error,
                ),
              ),
              Text('remaining', style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        ],
      ),
    );
  }
}
