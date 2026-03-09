import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'app_router.dart';
import 'providers/auth_provider.dart';
import 'providers/quest_provider.dart';
import 'providers/challenge_provider.dart';
import 'services/api_client.dart';
import 'theme/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final apiClient = ApiClient();
  runApp(AKDApp(apiClient: apiClient));
}

class AKDApp extends StatefulWidget {
  final ApiClient apiClient;

  const AKDApp({super.key, required this.apiClient});

  @override
  State<AKDApp> createState() => _AKDAppState();
}

class _AKDAppState extends State<AKDApp> {
  late final AuthProvider _authProvider;
  late final GoRouter _router;

  @override
  void initState() {
    super.initState();
    _authProvider = AuthProvider(api: widget.apiClient);
    _router = appRouter(_authProvider);
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // Expose the raw API client for services that need it
        Provider<ApiClient>.value(value: widget.apiClient),
        // Auth must come first — router listens to it
        ChangeNotifierProvider.value(value: _authProvider),
        ChangeNotifierProvider(
          create: (_) => QuestProvider(api: widget.apiClient),
        ),
        ChangeNotifierProvider(
          create: (_) => ChallengeProvider(api: widget.apiClient),
        ),
      ],
      child: MaterialApp.router(
        title: 'Acts of Kindness Daily',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        routerConfig: _router,
      ),
    );
  }
}
