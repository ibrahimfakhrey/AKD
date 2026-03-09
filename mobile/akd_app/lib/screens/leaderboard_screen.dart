import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';

import '../models/leaderboard_entry.dart';
import '../services/api_client.dart';
import '../services/leaderboard_service.dart';
import '../theme/app_colors.dart';
import '../widgets/leaderboard_row.dart';

/// Leaderboard screen — tabs for points and gems rankings.
class LeaderboardScreen extends StatefulWidget {
  const LeaderboardScreen({super.key});

  @override
  State<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabCtrl;
  late LeaderboardService _service;
  List<LeaderboardEntry> _points = [];
  List<LeaderboardEntry> _gems = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabCtrl = TabController(length: 2, vsync: this);
    _service = LeaderboardService(context.read<ApiClient>());
    _load();
  }

  @override
  void dispose() {
    _tabCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      _points = await _service.getPointsBoard();
      _gems = await _service.getGemsBoard();
    } catch (e) {
      setState(
        () => _error = 'Could not load leaderboard. Check your connection.',
      );
    }
    setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Leaderboard'),
        bottom: TabBar(
          controller: _tabCtrl,
          indicatorColor: AppColors.pointsGold,
          labelColor: AppColors.pointsGold,
          unselectedLabelColor: AppColors.textMuted,
          tabs: const [
            Tab(icon: Icon(Icons.star_rounded), text: 'Points'),
            Tab(icon: Icon(Icons.diamond_rounded), text: 'Gems'),
          ],
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.lightGradient),
        child: _loading
            ? const Center(
                child: CircularProgressIndicator(color: AppColors.pointsGold),
              )
            : _error != null
            ? Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.wifi_off_rounded,
                      color: AppColors.error,
                      size: 48,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      _error!,
                      style: const TextStyle(color: AppColors.error),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: _load,
                      icon: const Icon(Icons.refresh_rounded),
                      label: const Text('Retry'),
                    ),
                  ],
                ),
              )
            : TabBarView(
                controller: _tabCtrl,
                children: [_buildList(_points, false), _buildList(_gems, true)],
              ),
      ),
    );
  }

  Widget _buildList(List<LeaderboardEntry> entries, bool isGems) {
    if (entries.isEmpty) {
      return Center(
        child: Text(
          'No rankings yet',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.builder(
        padding: const EdgeInsets.only(top: 12),
        itemCount: entries.length,
        itemBuilder: (_, i) => LeaderboardRow(entry: entries[i], isGems: isGems)
            .animate()
            .fadeIn(delay: (60 * i).ms, duration: 300.ms)
            .slideX(begin: 0.1, end: 0),
      ),
    );
  }
}
