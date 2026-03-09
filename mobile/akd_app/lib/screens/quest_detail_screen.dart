import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';

import '../providers/quest_provider.dart';
import '../theme/app_colors.dart';

/// Quest detail — description, status, camera/gallery proof submission.
class QuestDetailScreen extends StatefulWidget {
  final String questId;

  const QuestDetailScreen({super.key, required this.questId});

  @override
  State<QuestDetailScreen> createState() => _QuestDetailScreenState();
}

class _QuestDetailScreenState extends State<QuestDetailScreen> {
  final _picker = ImagePicker();
  bool _submitting = false;

  Future<void> _pickAndSubmit(ImageSource source) async {
    final picked = await _picker.pickImage(source: source, imageQuality: 80);
    if (picked == null) return;

    final bytes = await picked.readAsBytes();

    setState(() => _submitting = true);
    final provider = context.read<QuestProvider>();
    final ok = await provider.submitProof(widget.questId, bytes, picked.name);
    setState(() => _submitting = false);

    if (ok && mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Proof submitted! 🎉')));
      Navigator.of(context).pop();
    } else if (mounted && provider.error != null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(provider.error!)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final quests = context.watch<QuestProvider>();
    final dq = quests.dailyQuests
        .where((q) => q.id == widget.questId)
        .firstOrNull;

    return Scaffold(
      appBar: AppBar(title: Text(dq?.quest?.title ?? 'Quest')),
      body: dq == null
          ? const Center(child: Text('Quest not found'))
          : Container(
              decoration: const BoxDecoration(
                gradient: AppColors.lightGradient,
              ),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Status pill
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: dq.isCompleted
                            ? AppColors.success.withValues(alpha: 0.15)
                            : dq.isPendingReview
                            ? AppColors.warning.withValues(alpha: 0.15)
                            : AppColors.coral.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        dq.statusLabel,
                        style: TextStyle(
                          color: dq.isCompleted
                              ? AppColors.success
                              : dq.isPendingReview
                              ? AppColors.warning
                              : AppColors.coral,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                    // Description
                    Text(
                      dq.quest?.description ?? '',
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                    const SizedBox(height: 12),
                    // Reward
                    Row(
                      children: [
                        const Icon(
                          Icons.star_rounded,
                          color: AppColors.pointsGold,
                          size: 20,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          '${dq.quest?.rewardPoints ?? 10} points',
                          style: Theme.of(context).textTheme.titleMedium
                              ?.copyWith(color: AppColors.pointsGold),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Icon(
                          Icons.category_rounded,
                          color: AppColors.purple,
                          size: 20,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          dq.quest?.category ?? 'General',
                          style: Theme.of(context).textTheme.bodyMedium
                              ?.copyWith(color: AppColors.purple),
                        ),
                      ],
                    ),
                    const Spacer(),
                    // Submit buttons
                    if (dq.isAssigned) ...[
                      if (_submitting)
                        const Center(
                          child: CircularProgressIndicator(
                            color: AppColors.coral,
                          ),
                        )
                      else ...[
                        SizedBox(
                          width: double.infinity,
                          height: 54,
                          child: ElevatedButton.icon(
                            onPressed: () => _pickAndSubmit(ImageSource.camera),
                            icon: const Icon(Icons.camera_alt_rounded),
                            label: const Text('Take Photo'),
                          ),
                        ),
                        const SizedBox(height: 12),
                        SizedBox(
                          width: double.infinity,
                          height: 54,
                          child: OutlinedButton.icon(
                            onPressed: () =>
                                _pickAndSubmit(ImageSource.gallery),
                            icon: const Icon(Icons.photo_library_rounded),
                            label: const Text('Choose from Gallery'),
                          ),
                        ),
                      ],
                    ],
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),
    );
  }
}
