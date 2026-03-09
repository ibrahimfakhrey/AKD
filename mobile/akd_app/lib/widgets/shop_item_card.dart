import 'package:flutter/material.dart';
import '../models/shop_item.dart';
import '../theme/app_colors.dart';

/// Shop item card with image, name, price badge, and buy action.
class ShopItemCard extends StatelessWidget {
  final ShopItem item;
  final bool owned;
  final VoidCallback? onBuy;
  final VoidCallback? onEquip;

  const ShopItemCard({
    super.key,
    required this.item,
    this.owned = false,
    this.onBuy,
    this.onEquip,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.lightCard,
        borderRadius: BorderRadius.circular(20),
        border: owned
            ? Border.all(
                color: AppColors.success.withValues(alpha: 0.5),
                width: 1.5,
              )
            : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Image area
          Expanded(
            flex: 3,
            child: Container(
              decoration: BoxDecoration(
                color: AppColors.inputBg,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(20),
                ),
              ),
              child: Center(
                child: item.imageUrl != null
                    ? ClipRRect(
                        borderRadius: const BorderRadius.vertical(
                          top: Radius.circular(20),
                        ),
                        child: Image.network(item.imageUrl!, fit: BoxFit.cover),
                      )
                    : Icon(
                        _categoryIcon(item.category),
                        size: 40,
                        color: AppColors.purple,
                      ),
              ),
            ),
          ),
          // Info
          Expanded(
            flex: 2,
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.name,
                    style: Theme.of(context).textTheme.titleMedium,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const Spacer(),
                  owned
                      ? GestureDetector(
                          onTap: onEquip,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color: AppColors.success.withValues(alpha: 0.15),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: const Text(
                              'Equip',
                              style: TextStyle(
                                color: AppColors.success,
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        )
                      : GestureDetector(
                          onTap: onBuy,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              gradient: AppColors.purpleGradient,
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(
                                  Icons.diamond_rounded,
                                  color: Colors.white,
                                  size: 14,
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  '${item.priceGems}',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  IconData _categoryIcon(String category) {
    switch (category) {
      case 'avatar_frame':
        return Icons.face_rounded;
      case 'badge':
        return Icons.military_tech_rounded;
      case 'theme':
        return Icons.palette_rounded;
      case 'emoji':
        return Icons.emoji_emotions_rounded;
      default:
        return Icons.card_giftcard_rounded;
    }
  }
}
