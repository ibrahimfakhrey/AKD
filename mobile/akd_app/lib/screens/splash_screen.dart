import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/app_colors.dart';

/// Animated splash screen with kindness heart logo.
class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.lightGradient),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      gradient: AppColors.coralGradient,
                      borderRadius: BorderRadius.circular(30),
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.coral.withValues(alpha: 0.4),
                          blurRadius: 40,
                          spreadRadius: 5,
                        ),
                      ],
                    ),
                    child: const Icon(
                      Icons.favorite_rounded,
                      color: Colors.white,
                      size: 60,
                    ),
                  )
                  .animate()
                  .scale(
                    begin: const Offset(0.5, 0.5),
                    end: const Offset(1.0, 1.0),
                    duration: 600.ms,
                    curve: Curves.elasticOut,
                  )
                  .fadeIn(duration: 400.ms),
              const SizedBox(height: 24),
              Text(
                    'Acts of Kindness',
                    style: Theme.of(context).textTheme.displayMedium,
                  )
                  .animate()
                  .fadeIn(delay: 300.ms, duration: 500.ms)
                  .slideY(begin: 0.3, end: 0),
              const SizedBox(height: 8),
              Text(
                'Spread love daily ✨',
                style: Theme.of(context).textTheme.bodyMedium,
              ).animate().fadeIn(delay: 600.ms, duration: 500.ms),
              const SizedBox(height: 48),
              const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  valueColor: AlwaysStoppedAnimation(AppColors.coral),
                ),
              ).animate().fadeIn(delay: 800.ms),
            ],
          ),
        ),
      ),
    );
  }
}
