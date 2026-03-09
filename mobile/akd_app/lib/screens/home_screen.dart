import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../providers/quest_provider.dart';
import '../providers/challenge_provider.dart';
import '../theme/app_colors.dart';
import '../widgets/quest_card.dart';
import '../widgets/stat_bar.dart';

/// Home screen — greeting, stats bar, and tabs for quests & challenges.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Timer? _pollingTimer;

  @override
  void initState() {
    super.initState();

    Future.microtask(() {
      if (!mounted) return;
      context.read<QuestProvider>().fetchDailyQuests();
      context.read<ChallengeProvider>().fetchReceived();
    });

    // Auto-refresh polling every 10 seconds
    _pollingTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      if (!mounted) return;
      context.read<QuestProvider>().fetchDailyQuests();
      context.read<ChallengeProvider>().fetchReceived();
      context.read<AuthProvider>().refreshProfile();
    });
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }

  Future<void> _refresh() async {
    await context.read<QuestProvider>().fetchDailyQuests();
    await context.read<ChallengeProvider>().fetchReceived();
    await context.read<AuthProvider>().refreshProfile();
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final quests = context.watch<QuestProvider>();
    final cp = context.watch<ChallengeProvider>();

    return Scaffold(
      backgroundColor: AppColors.lightBg,
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.lightGradient),
        child: SafeArea(
          child: RefreshIndicator(
            color: AppColors.coral,
            onRefresh: _refresh,
            child: CustomScrollView(
              slivers: [
                // Header
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                      'Hello, ${auth.user?.displayName ?? 'Kind Soul'} 👋',
                                      style: Theme.of(
                                        context,
                                      ).textTheme.headlineLarge,
                                    )
                                    .animate()
                                    .fadeIn(duration: 400.ms)
                                    .slideX(begin: -0.1, end: 0),
                                const SizedBox(height: 4),
                                Text(
                                  "Today's kindness awaits!",
                                  style: Theme.of(context).textTheme.bodyMedium,
                                ),
                              ],
                            ),
                            Row(
                              children: [
                                Stack(
                                  children: [
                                    IconButton(
                                      onPressed: () =>
                                          context.push('/challenges'),
                                      icon: Container(
                                        padding: const EdgeInsets.all(10),
                                        decoration: BoxDecoration(
                                          color: AppColors.lightCard,
                                          borderRadius: BorderRadius.circular(
                                            14,
                                          ),
                                        ),
                                        child: const Icon(
                                          Icons.mail_rounded,
                                          color: AppColors.teal,
                                        ),
                                      ),
                                    ),
                                    if (cp.received.isNotEmpty)
                                      Positioned(
                                        right: 8,
                                        top: 8,
                                        child: Container(
                                          padding: const EdgeInsets.all(4),
                                          decoration: const BoxDecoration(
                                            color: AppColors.coral,
                                            shape: BoxShape.circle,
                                          ),
                                          child: Text(
                                            '${cp.received.length}',
                                            style: const TextStyle(
                                              fontSize: 10,
                                              color: Colors.white,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                        ),
                                      ),
                                  ],
                                ),
                                IconButton(
                                  onPressed: () => context.push('/leaderboard'),
                                  icon: Container(
                                    padding: const EdgeInsets.all(10),
                                    decoration: BoxDecoration(
                                      color: AppColors.lightCard,
                                      borderRadius: BorderRadius.circular(14),
                                    ),
                                    child: const Icon(
                                      Icons.leaderboard_rounded,
                                      color: AppColors.pointsGold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        StatBar(
                          points: auth.user?.points ?? 0,
                          gems: auth.user?.gems ?? 0,
                        ).animate().fadeIn(delay: 200.ms, duration: 400.ms),
                      ],
                    ),
                  ),
                ),

                // Quests Label
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(20, 20, 20, 8),
                    child: Text(
                      'Daily Quests',
                      style: Theme.of(context).textTheme.headlineMedium,
                    ),
                  ),
                ),

                // Quests List
                if (quests.loading && quests.dailyQuests.isEmpty)
                  const SliverFillRemaining(
                    child: Center(
                      child: CircularProgressIndicator(color: AppColors.coral),
                    ),
                  )
                else if (quests.error != null && quests.dailyQuests.isEmpty)
                  SliverFillRemaining(
                    child: Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(
                            Icons.cloud_off_rounded,
                            size: 48,
                            color: AppColors.textMuted,
                          ),
                          const SizedBox(height: 12),
                          Text(
                            quests.error!,
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: quests.fetchDailyQuests,
                            child: const Text('Retry'),
                          ),
                        ],
                      ),
                    ),
                  )
                else
                  SliverPadding(
                    padding: const EdgeInsets.only(top: 8, bottom: 20),
                    sliver: SliverList(
                      delegate: SliverChildBuilderDelegate(
                        (_, i) =>
                            QuestCard(
                                  dailyQuest: quests.dailyQuests[i],
                                  onTap: () => context.push(
                                    '/quest/${quests.dailyQuests[i].id}',
                                  ),
                                )
                                .animate()
                                .fadeIn(delay: (100 * i).ms, duration: 400.ms)
                                .slideY(begin: 0.15, end: 0),
                        childCount: quests.dailyQuests.length,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
