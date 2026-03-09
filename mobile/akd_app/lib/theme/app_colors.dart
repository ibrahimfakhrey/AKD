import 'package:flutter/material.dart';

/// AKD design system colors — fun, bouncy, catchy playful palette.
class AppColors {
  AppColors._();

  // Playful Primary palette
  static const coral = Color(0xFFFF6B6B);
  static const coralLight = Color(0xFFFF8E8E);
  static const coralDark = Color(0xFFE84545);

  // Playful Secondary palette
  static const teal = Color(0xFF4ECDC4);
  static const tealLight = Color(0xFF7EDDD6);
  static const tealDark = Color(0xFF36B5AC);

  // Accent & Fun Colors
  static const purple = Color(0xFF9B59B6);
  static const blueLight = Color(0xFF48DBFB);
  static const yellow = Color(0xFFFDCB6E);

  // Gems & Points
  static const gemBlue = Color(0xFF60A5FA);
  static const pointsGold = Color(0xFFFBBF24);

  // Status
  static const success = Color(0xFF2ECC71);
  static const warning = Color(0xFFFDCB6E);
  static const error = Color(0xFFFF6B6B);

  // Light theme surfaces (Bouncy Theme)
  static const lightBg = Color(0xFFF0F4F8);
  static const lightSurface = Color(0xFFFFFFFF);
  static const lightCard = Color(0xFFFFFFFF);
  static const lightCardHover = Color(0xFFF8FAFC);
  static const inputBg = Color(0xFFF1F5F9);

  // Text
  static const textPrimary = Color(0xFF1E293B);
  static const textSecondary = Color(0xFF475569);
  static const textMuted = Color(0xFF94A3B8);

  // Gradients
  static const coralGradient = LinearGradient(
    colors: [coral, Color(0xFFFF9A76)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const tealGradient = LinearGradient(
    colors: [teal, Color(0xFF55E6C1)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const purpleGradient = LinearGradient(
    colors: [purple, Color(0xFFD980FA)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const lightGradient = LinearGradient(
    colors: [lightBg, Color(0xFFE2E8F0)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
}
