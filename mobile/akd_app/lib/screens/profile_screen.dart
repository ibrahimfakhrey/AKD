import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../theme/app_colors.dart';
import '../utils/color_utils.dart';

/// Profile screen — avatar, stats, bio, edit, logout.
class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _editing = false;
  late TextEditingController _nameCtrl;
  late TextEditingController _bioCtrl;

  @override
  void initState() {
    super.initState();
    final user = context.read<AuthProvider>().user;
    _nameCtrl = TextEditingController(text: user?.displayName ?? '');
    _bioCtrl = TextEditingController(text: user?.bio ?? '');
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _bioCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    final auth = context.read<AuthProvider>();
    await auth.updateProfile({
      'display_name': _nameCtrl.text.trim(),
      'bio': _bioCtrl.text.trim(),
    });
    setState(() => _editing = false);
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final user = auth.user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        actions: [
          if (!_editing)
            IconButton(
              icon: const Icon(Icons.edit_rounded),
              onPressed: () => setState(() => _editing = true),
            )
          else
            TextButton(
              onPressed: _save,
              child: const Text(
                'Save',
                style: TextStyle(color: AppColors.coral),
              ),
            ),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.lightGradient),
        child: user == null
            ? const Center(child: CircularProgressIndicator())
            : SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    // Avatar
                    CircleAvatar(
                      radius: 50,
                      backgroundColor: AppColors.coral.withValues(alpha: 0.2),
                      backgroundImage: user.avatarUrl != null
                          ? NetworkImage(user.avatarUrl!)
                          : null,
                      child: user.avatarUrl == null
                          ? Text(
                              user.displayName.isNotEmpty
                                  ? user.displayName[0].toUpperCase()
                                  : '?',
                              style: const TextStyle(
                                fontSize: 40,
                                color: AppColors.coral,
                                fontWeight: FontWeight.w700,
                              ),
                            )
                          : null,
                    ).animate().scale(
                      begin: const Offset(0.8, 0.8),
                      end: const Offset(1.0, 1.0),
                      duration: 400.ms,
                    ),
                    const SizedBox(height: 16),
                    // Name
                    if (_editing)
                      TextField(
                        controller: _nameCtrl,
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.headlineMedium,
                        decoration: const InputDecoration(
                          hintText: 'Display Name',
                          border: InputBorder.none,
                        ),
                      )
                    else
                      Text(
                        user.displayName,
                        style: Theme.of(context).textTheme.headlineMedium,
                      ),
                    const SizedBox(height: 4),
                    Text(
                      user.email ?? '',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 24),
                    // Stats row
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        _statBox(
                          context,
                          'Points',
                          user.points.toString(),
                          AppColors.pointsGold,
                        ),
                        const SizedBox(width: 16),
                        _statBox(
                          context,
                          'Gems',
                          user.gems.toString(),
                          AppColors.gemBlue,
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    // Bio
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        color: AppColors.lightCard,
                        borderRadius: BorderRadius.circular(18),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Bio',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 8),
                          if (_editing)
                            TextField(
                              controller: _bioCtrl,
                              maxLines: 3,
                              decoration: const InputDecoration(
                                hintText: 'Tell us about yourself...',
                                border: InputBorder.none,
                              ),
                            )
                          else
                            Text(
                              user.bio?.isNotEmpty == true
                                  ? user.bio!
                                  : 'No bio yet. Tap edit to add one!',
                              style: Theme.of(context).textTheme.bodyMedium,
                            ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 32),
                    // Logout
                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: OutlinedButton.icon(
                        onPressed: () async {
                          await auth.logout();
                          if (mounted) context.go('/login');
                        },
                        style: OutlinedButton.styleFrom(
                          foregroundColor: AppColors.error,
                          side: const BorderSide(color: AppColors.error),
                        ),
                        icon: const Icon(Icons.logout_rounded),
                        label: const Text('Logout'),
                      ),
                    ),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _statBox(
    BuildContext context,
    String label,
    String value,
    Color color,
  ) {
    return Container(
      width: 120,
      padding: const EdgeInsets.symmetric(vertical: 18),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: Theme.of(
              context,
            ).textTheme.headlineLarge?.copyWith(color: color),
          ),
          const SizedBox(height: 4),
          Text(label, style: Theme.of(context).textTheme.bodySmall),
        ],
      ),
    );
  }
}
