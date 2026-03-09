import '../models/shop_item.dart';
import 'api_client.dart';

/// Shop service — browse items, buy, view inventory.
class ShopService {
  final ApiClient _api;

  ShopService(this._api);

  /// GET /shop/items
  Future<List<ShopItem>> listItems() async {
    final res = await _api.dio.get('/shop/items');
    return (res.data as List).map((j) => ShopItem.fromJson(j)).toList();
  }

  /// POST /shop/buy/<itemId>
  Future<Map<String, dynamic>> buyItem(String itemId) async {
    final res = await _api.dio.post('/shop/buy/$itemId');
    return res.data;
  }

  /// GET /shop/inventory
  Future<List<Purchase>> getInventory() async {
    final res = await _api.dio.get('/shop/inventory');
    return (res.data as List).map((j) => Purchase.fromJson(j)).toList();
  }

  Future<void> equipItem(String itemId) async {
    final response = await _api.dio.post('/shop/equip/$itemId');
    if (response.statusCode != 200) {
      throw Exception('Failed to equip item');
    }
  }
}
