import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

/// Points/gems stat display with icon.
class StatBar extends StatelessWidget {
  final int points;
  final int gems;

  const StatBar({super.key, required this.points, required this.gems});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _chip(Icons.star_rounded, AppColors.pointsGold, points.toString()),
        const SizedBox(width: 12),
        _chip(Icons.diamond_rounded, AppColors.gemBlue, gems.toString()),
      ],
    );
  }

  Widget _chip(IconData icon, Color color, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: 18),
          const SizedBox(width: 6),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w700,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }
}
