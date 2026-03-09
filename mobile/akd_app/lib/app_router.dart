import 'package:go_router/go_router.dart';

import 'providers/auth_provider.dart';
import 'screens/splash_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/signup_screen.dart';
import 'screens/main_shell.dart';
import 'screens/quest_detail_screen.dart';
import 'screens/leaderboard_screen.dart';

/// GoRouter configuration with auth-based redirects.
GoRouter appRouter(AuthProvider auth) {
  return GoRouter(
    initialLocation: '/',
    refreshListenable: auth,
    redirect: (context, state) {
      final loggedIn = auth.isLoggedIn;
      final loggingIn =
          state.matchedLocation == '/login' ||
          state.matchedLocation == '/signup';
      final splashing = state.matchedLocation == '/';

      if (auth.loading) return null; // still checking
      if (!loggedIn && !loggingIn) return '/login';
      if (loggedIn && (loggingIn || splashing)) return '/home';
      return null;
    },
    routes: [
      GoRoute(path: '/', builder: (context, state) => const SplashScreen()),
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(
        path: '/signup',
        builder: (context, state) => const SignupScreen(),
      ),
      GoRoute(path: '/home', builder: (context, state) => const MainShell()),
      GoRoute(
        path: '/quest/:id',
        builder: (_, state) =>
            QuestDetailScreen(questId: state.pathParameters['id']!),
      ),
      GoRoute(
        path: '/leaderboard',
        builder: (context, state) => const LeaderboardScreen(),
      ),
    ],
  );
}
