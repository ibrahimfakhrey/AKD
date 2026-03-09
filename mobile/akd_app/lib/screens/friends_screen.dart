import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/friend.dart';
import '../services/api_client.dart';
import '../services/friend_service.dart';
import '../theme/app_colors.dart';
import '../utils/color_utils.dart';
import '../widgets/friend_tile.dart';

/// Friends screen — tabs for friends list and pending requests.
class FriendsScreen extends StatefulWidget {
  const FriendsScreen({super.key});

  @override
  State<FriendsScreen> createState() => _FriendsScreenState();
}

class _FriendsScreenState extends State<FriendsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabCtrl;
  late FriendService _service;
  List<FriendEntry> _friends = [];
  List<PendingRequest> _pending = [];
  bool _loading = true;
  final _addCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tabCtrl = TabController(length: 2, vsync: this);
    _service = FriendService(context.read<ApiClient>());
    _loadAll();
  }

  @override
  void dispose() {
    _tabCtrl.dispose();
    _addCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadAll() async {
    setState(() => _loading = true);
    try {
      _friends = await _service.listFriends();
      _pending = await _service.pendingRequests();
    } catch (_) {}
    setState(() => _loading = false);
  }

  Future<void> _accept(String id) async {
    await _service.acceptRequest(id);
    _loadAll();
  }

  Future<void> _remove(String id) async {
    await _service.removeFriend(id);
    _loadAll();
  }

  Future<void> _sendRequest() async {
    final email = _addCtrl.text.trim();
    if (email.isEmpty) return;
    try {
      await _service.sendRequest(email);
      _addCtrl.clear();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Friend request sent! 💌')),
        );
      }
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
      appBar: AppBar(
        title: const Text('Friends'),
        bottom: TabBar(
          controller: _tabCtrl,
          indicatorColor: AppColors.coral,
          labelColor: AppColors.coral,
          unselectedLabelColor: AppColors.textMuted,
          tabs: [
            Tab(text: 'Friends (${_friends.length})'),
            Tab(text: 'Pending (${_pending.length})'),
          ],
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.lightGradient),
        child: _loading
            ? const Center(
                child: CircularProgressIndicator(color: AppColors.coral),
              )
            : TabBarView(
                controller: _tabCtrl,
                children: [
                  // Friends tab
                  RefreshIndicator(
                    onRefresh: _loadAll,
                    child: _friends.isEmpty
                        ? ListView(
                            children: [
                              const SizedBox(height: 100),
                              Center(
                                child: Column(
                                  children: [
                                    const Icon(
                                      Icons.people_outline_rounded,
                                      size: 48,
                                      color: AppColors.textMuted,
                                    ),
                                    const SizedBox(height: 12),
                                    Text(
                                      'No friends yet',
                                      style: Theme.of(
                                        context,
                                      ).textTheme.bodyMedium,
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.only(top: 8),
                            itemCount: _friends.length,
                            itemBuilder: (_, i) {
                              final f = _friends[i];
                              return FriendTile(
                                displayName: f.friend?.displayName ?? 'Unknown',
                                avatarUrl: f.friend?.avatarUrl,
                                nameColor:
                                    f.friend?.equippedCosmetics?['name_color'] !=
                                        null
                                    ? HexColor.fromHex(
                                        f
                                            .friend!
                                            .equippedCosmetics!['name_color'],
                                      )
                                    : null,
                                trailing: IconButton(
                                  icon: const Icon(
                                    Icons.person_remove_rounded,
                                    color: AppColors.error,
                                    size: 20,
                                  ),
                                  onPressed: () => _remove(f.friendshipId),
                                ),
                              );
                            },
                          ),
                  ),
                  // Pending tab
                  RefreshIndicator(
                    onRefresh: _loadAll,
                    child: _pending.isEmpty
                        ? ListView(
                            children: [
                              const SizedBox(height: 100),
                              Center(
                                child: Text(
                                  'No pending requests',
                                  style: Theme.of(context).textTheme.bodyMedium,
                                ),
                              ),
                            ],
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.only(top: 8),
                            itemCount: _pending.length,
                            itemBuilder: (_, i) {
                              final p = _pending[i];
                              return FriendTile(
                                displayName:
                                    p.requester?.displayName ?? 'Unknown',
                                avatarUrl: p.requester?.avatarUrl,
                                subtitle: 'Wants to be your friend',
                                trailing: ElevatedButton(
                                  onPressed: () => _accept(p.friendshipId),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: AppColors.teal,
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 14,
                                      vertical: 8,
                                    ),
                                    minimumSize: Size.zero,
                                  ),
                                  child: const Text(
                                    'Accept',
                                    style: TextStyle(fontSize: 12),
                                  ),
                                ),
                              );
                            },
                          ),
                  ),
                ],
              ),
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppColors.coral,
        onPressed: () {
          showModalBottomSheet(
            context: context,
            backgroundColor: AppColors.lightSurface,
            shape: const RoundedRectangleBorder(
              borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
            ),
            builder: (_) => Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Add Friend',
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _addCtrl,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(
                      labelText: 'Friend Email Address',
                      prefixIcon: Icon(
                        Icons.email_outlined,
                        color: AppColors.coral,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        _sendRequest();
                        Navigator.pop(context);
                      },
                      child: const Text('Send Request'),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
              ),
            ),
          );
        },
        child: const Icon(Icons.person_add_rounded),
      ),
    );
  }
}
