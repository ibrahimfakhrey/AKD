import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

/// AKD app theme — playful, vibrant, and fun bouncy theme.
class AppTheme {
  AppTheme._();

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      scaffoldBackgroundColor: AppColors.lightBg,
      colorScheme: const ColorScheme.light(
        primary: AppColors.coral,
        secondary: AppColors.teal,
        tertiary: AppColors.purple,
        surface: AppColors.lightSurface,
        error: AppColors.error,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: AppColors.textPrimary,
        onError: Colors.white,
      ),
      textTheme: _textTheme,
      appBarTheme: AppBarTheme(
        backgroundColor: AppColors.lightBg,
        foregroundColor: AppColors.textPrimary,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: GoogleFonts.outfit(
          fontSize: 22,
          fontWeight: FontWeight.w800,
          letterSpacing: -0.5,
          color: AppColors.textPrimary,
        ),
      ),
      cardTheme: CardThemeData(
        color: AppColors.lightCard,
        elevation: 6,
        shadowColor: Colors.black.withOpacity(0.08),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(
            32,
          ), // Extra bouncy rounded corners
        ),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.coral,
          foregroundColor: Colors.white,
          elevation: 4,
          shadowColor: AppColors.coral.withOpacity(0.5),
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 18),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          textStyle: GoogleFonts.outfit(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            letterSpacing: 0.5,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style:
            OutlinedButton.styleFrom(
              foregroundColor: AppColors.teal,
              backgroundColor: AppColors.inputBg,
              side: const BorderSide(color: Colors.transparent, width: 2),
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 18),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(24),
              ),
              textStyle: GoogleFonts.outfit(
                fontSize: 18,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.5,
              ),
            ).copyWith(
              side: MaterialStateProperty.resolveWith<BorderSide>((
                Set<MaterialState> states,
              ) {
                if (states.contains(MaterialState.hovered) ||
                    states.contains(MaterialState.pressed)) {
                  return const BorderSide(color: AppColors.teal, width: 2);
                }
                return const BorderSide(color: Colors.transparent, width: 0);
              }),
            ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.inputBg,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20),
          borderSide: const BorderSide(color: AppColors.teal, width: 3),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20),
          borderSide: const BorderSide(color: AppColors.error, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 24,
          vertical: 20,
        ),
        hintStyle: GoogleFonts.inter(
          color: AppColors.textMuted,
          fontSize: 16,
          fontWeight: FontWeight.w500,
        ),
        labelStyle: GoogleFonts.inter(
          color: AppColors.textSecondary,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: AppColors.lightSurface,
        selectedItemColor: AppColors.coral,
        unselectedItemColor: AppColors.textMuted,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: AppColors.textPrimary,
        contentTextStyle: GoogleFonts.inter(
          color: Colors.white,
          fontWeight: FontWeight.w600,
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        behavior: SnackBarBehavior.floating,
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: AppColors.lightSurface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(32)),
      ),
    );
  }

  static TextTheme get _textTheme {
    return TextTheme(
      displayLarge: GoogleFonts.outfit(
        fontSize: 36,
        fontWeight: FontWeight.w800,
        letterSpacing: -1,
        color: AppColors.textPrimary,
      ),
      displayMedium: GoogleFonts.outfit(
        fontSize: 30,
        fontWeight: FontWeight.w800,
        letterSpacing: -0.5,
        color: AppColors.textPrimary,
      ),
      headlineLarge: GoogleFonts.outfit(
        fontSize: 26,
        fontWeight: FontWeight.w800,
        color: AppColors.textPrimary,
      ),
      headlineMedium: GoogleFonts.outfit(
        fontSize: 22,
        fontWeight: FontWeight.w700,
        color: AppColors.textPrimary,
      ),
      titleLarge: GoogleFonts.outfit(
        fontSize: 20,
        fontWeight: FontWeight.w700,
        color: AppColors.textPrimary,
      ),
      titleMedium: GoogleFonts.outfit(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: AppColors.textPrimary,
      ),
      bodyLarge: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.w500,
        color: AppColors.textPrimary,
      ),
      bodyMedium: GoogleFonts.inter(
        fontSize: 15,
        fontWeight: FontWeight.w500,
        color: AppColors.textSecondary,
      ),
      bodySmall: GoogleFonts.inter(
        fontSize: 13,
        fontWeight: FontWeight.w500,
        color: AppColors.textMuted,
      ),
      labelLarge: GoogleFonts.outfit(
        fontSize: 15,
        fontWeight: FontWeight.w700,
        letterSpacing: 0.5,
        color: AppColors.textPrimary,
      ),
    );
  }
}
