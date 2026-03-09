import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';

import '../models/shop_item.dart';
import '../services/api_client.dart';
import '../services/shop_service.dart';
import '../theme/app_colors.dart';
import '../widgets/shop_item_card.dart';

/// Shop screen — grid of items, buy with gems.
class ShopScreen extends StatefulWidget {
  const ShopScreen({super.key});

  @override
  State<ShopScreen> createState() => _ShopScreenState();
}

class _ShopScreenState extends State<ShopScreen> {
  late ShopService _service;
  List<ShopItem> _items = [];
  List<Purchase> _inventory = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _service = ShopService(context.read<ApiClient>());
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      _items = await _service.listItems();
      _inventory = await _service.getInventory();
    } catch (_) {}
    setState(() => _loading = false);
  }

  Set<String> get _ownedIds => _inventory.map((p) => p.shopItemId).toSet();

  Future<void> _buy(ShopItem item) async {
    try {
      await _service.buyItem(item.id);
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Purchased ${item.name}! 🎉')));
      }
      _load();
    } on DioException catch (e) {
      if (mounted) {
        final api = context.read<ApiClient>();
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(api.errorMessage(e))));
      }
    }
  }

  Future<void> _equip(ShopItem item) async {
    try {
      await _service.equipItem(item.id);
      if (mounted) {
        // Also refresh user profile here ideally, but for now just show success
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Equipped ${item.name}! ✨')));
      }
      _load();
    } on DioException catch (e) {
      if (mounted) {
        final api = context.read<ApiClient>();
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(api.errorMessage(e))));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Shop')),
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.lightGradient),
        child: _loading
            ? const Center(
                child: CircularProgressIndicator(color: AppColors.purple),
              )
            : _items.isEmpty
            ? Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.store_rounded,
                      size: 48,
                      color: AppColors.textMuted,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Shop is empty',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              )
            : RefreshIndicator(
                onRefresh: _load,
                child: GridView.builder(
                  padding: const EdgeInsets.all(16),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    mainAxisSpacing: 14,
                    crossAxisSpacing: 14,
                    childAspectRatio: 0.75,
                  ),
                  itemCount: _items.length,
                  itemBuilder: (_, i) {
                    final item = _items[i];
                    return ShopItemCard(
                          item: item,
                          owned: _ownedIds.contains(item.id),
                          onBuy: () => _buy(item),
                          onEquip: () => _equip(item),
                        )
                        .animate()
                        .fadeIn(delay: (80 * i).ms, duration: 300.ms)
                        .scale(
                          begin: const Offset(0.9, 0.9),
                          end: const Offset(1.0, 1.0),
                        );
                  },
                ),
              ),
      ),
    );
  }
}
