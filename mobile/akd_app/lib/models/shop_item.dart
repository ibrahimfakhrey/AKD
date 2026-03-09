/// Shop item and purchase models.
class ShopItem {
  final String id;
  final String name;
  final String? description;
  final String category; // avatar_frame, badge, theme, emoji
  final int priceGems;
  final String? imageUrl;
  final bool active;

  ShopItem({
    required this.id,
    required this.name,
    this.description,
    this.category = 'badge',
    this.priceGems = 10,
    this.imageUrl,
    this.active = true,
  });

  factory ShopItem.fromJson(Map<String, dynamic> json) {
    return ShopItem(
      id: json['id'],
      name: json['name'] ?? '',
      description: json['description'],
      category: json['category'] ?? 'badge',
      priceGems: json['price_gems'] ?? 10,
      imageUrl: json['image_url'],
      active: json['active'] ?? true,
    );
  }
}

class Purchase {
  final String id;
  final String userId;
  final String shopItemId;
  final ShopItem? item;
  final String purchasedAt;

  Purchase({
    required this.id,
    required this.userId,
    required this.shopItemId,
    this.item,
    required this.purchasedAt,
  });

  factory Purchase.fromJson(Map<String, dynamic> json) {
    return Purchase(
      id: json['id'],
      userId: json['user_id'] ?? '',
      shopItemId: json['shop_item_id'] ?? '',
      item: json['item'] != null ? ShopItem.fromJson(json['item']) : null,
      purchasedAt: json['purchased_at'] ?? '',
    );
  }
}
