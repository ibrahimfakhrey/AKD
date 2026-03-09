import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import 'home_screen.dart';
import 'challenge_screen.dart';
import 'friends_screen.dart';
import 'shop_screen.dart';
import 'profile_screen.dart';

/// Main tab scaffold — bottom nav with 5 tabs.
class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _index = 0;

  static const _screens = [
    HomeScreen(),
    ChallengeScreen(),
    FriendsScreen(),
    ShopScreen(),
    ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _index, children: _screens),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: AppColors.lightSurface,
          border: Border(
            top: BorderSide(
              color: AppColors.inputBg.withValues(alpha: 0.4),
              width: 1,
            ),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: _index,
          onTap: (i) => setState(() => _index = i),
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home_rounded),
              label: 'Home',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.timer_rounded),
              label: 'Challenge',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.people_rounded),
              label: 'Friends',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.store_rounded),
              label: 'Shop',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_rounded),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }
}
