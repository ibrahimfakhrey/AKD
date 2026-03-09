import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';

import '../providers/challenge_provider.dart';
import '../models/challenge.dart';
import '../theme/app_colors.dart';
import '../widgets/countdown_timer.dart';

/// Challenge screen — countdown timer, submit proof, received challenges.
class ChallengeScreen extends StatefulWidget {
  const ChallengeScreen({super.key});

  @override
  State<ChallengeScreen> createState() => _ChallengeScreenState();
}

class _ChallengeScreenState extends State<ChallengeScreen> {
  final _picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      if (!mounted) return;
      context.read<ChallengeProvider>().fetchReceived();
    });
  }

  Future<void> _submitPhoto(Challenge receivedChallenge) async {
    final picked = await _picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 80,
    );
    if (picked == null) return;

    final bytes = await picked.readAsBytes();

    final provider = context.read<ChallengeProvider>();
    final ok = await provider.submitReceivedProof(
      receivedChallenge.id,
      bytes,
      picked.name,
    );

    if (ok && mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Challenge completed! 💎')));
    } else if (mounted && provider.error != null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(provider.error!)));
    }
  }

  void _showSendDialog() {
    final ctrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.lightSurface,
        title: const Text('Send Challenge'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Costs 50 points. Your friend has 1 hour to complete it for 5 gems!',
              style: TextStyle(fontSize: 13, color: AppColors.textMuted),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: ctrl,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(
                labelText: 'Friend Email Address',
                prefixIcon: Icon(Icons.email_outlined, color: AppColors.teal),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              final email = ctrl.text.trim();
              if (email.isEmpty) return;
              Navigator.pop(ctx);
              final cp = context.read<ChallengeProvider>();
              final ok = await cp.sendToFriend(email);
              if (ok && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Challenge sent! 💌')),
                );
              } else if (mounted && cp.error != null) {
                ScaffoldMessenger.of(
                  context,
                ).showSnackBar(SnackBar(content: Text(cp.error!)));
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.teal),
            child: const Text('Send (50 pts)'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cp = context.watch<ChallengeProvider>();

    return Scaffold(
      appBar: AppBar(title: const Text('Received Challenges')),
      body: Container(
        width: double.infinity,
        decoration: const BoxDecoration(gradient: AppColors.lightGradient),
        child: SafeArea(
          child: RefreshIndicator(
            onRefresh: () => cp.fetchReceived(),
            child: cp.received.isEmpty
                ? ListView(
                    children: [
                      const SizedBox(height: 100),
                      Center(
                        child: Column(
                          children: [
                            const Icon(
                              Icons.mail_outline_rounded,
                              size: 48,
                              color: AppColors.textMuted,
                            ),
                            const SizedBox(height: 12),
                            Text(
                              'No incoming challenges',
                              style: Theme.of(context).textTheme.bodyMedium,
                            ),
                          ],
                        ),
                      ),
                    ],
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: cp.received.length,
                    itemBuilder: (ctx, i) {
                      final challenge = cp.received[i];
                      if (challenge.status == 'pending_review') {
                        return _receivedCard(
                          challenge,
                          "Pending Review...",
                          null,
                        );
                      }
                      return _receivedCard(
                        challenge,
                        "Prove it within:",
                        CountdownTimer(
                          remaining: challenge.timeRemaining,
                          total: challenge.expiresAtDateTime.difference(
                            challenge.startedAtDateTime,
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.teal,
        onPressed: _showSendDialog,
        icon: const Icon(Icons.send_rounded),
        label: const Text('Send Friend'),
      ),
    );
  }

  Widget _receivedCard(
    Challenge challenge,
    String subtitle,
    Widget? timerWidget,
  ) {
    return Card(
      color: AppColors.lightSurface,
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(
                  Icons.mark_email_unread_rounded,
                  color: AppColors.coral,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Challenge from friend!',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.pointsGold.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.diamond_rounded,
                        size: 14,
                        color: AppColors.pointsGold,
                      ),
                      const SizedBox(width: 4),
                      const Text(
                        '5',
                        style: TextStyle(
                          color: AppColors.pointsGold,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              challenge.description ?? 'A hard kindness challenge',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            if (timerWidget != null) ...[
              Text(
                subtitle,
                style: const TextStyle(
                  fontSize: 12,
                  color: AppColors.textMuted,
                ),
              ),
              const SizedBox(height: 8),
              timerWidget,
            ] else ...[
              Text(subtitle, style: const TextStyle(color: AppColors.warning)),
            ],
            const SizedBox(height: 16),
            if (challenge.status == 'active')
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () => _submitPhoto(challenge),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.teal,
                  ),
                  icon: const Icon(Icons.camera_alt_rounded),
                  label: const Text('Submit Proof'),
                ),
              ),
          ],
        ),
      ).animate().fadeIn(duration: 300.ms).slideY(begin: 0.1, end: 0),
    );
  }
}
