import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import '../models/quest.dart';
import '../services/api_client.dart';
import '../services/quest_service.dart';

/// Quest state provider — daily quests fetching and proof submission.
class QuestProvider extends ChangeNotifier {
  final ApiClient api;
  late final QuestService _service;

  List<DailyQuest> _dailyQuests = [];
  bool _loading = false;
  String? _error;

  QuestProvider({required this.api}) {
    _service = QuestService(api);
  }

  List<DailyQuest> get dailyQuests => _dailyQuests;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> fetchDailyQuests() async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _dailyQuests = await _service.getDailyQuests();
    } on DioException catch (e) {
      _error = api.errorMessage(e);
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<bool> submitProof(
    String questId,
    List<int> bytes,
    String filename,
  ) async {
    _error = null;
    _loading = true;
    notifyListeners();
    try {
      await _service.submitProof(questId, bytes, filename);
      // Refresh quest list (this manages _loading internally)
      _dailyQuests = await _service.getDailyQuests();
      return true;
    } on DioException catch (e) {
      _error = api.errorMessage(e);
      return false;
    } catch (e) {
      _error = 'Could not submit proof: $e';
      return false;
    } finally {
      _loading = false;
      notifyListeners();
    }
  }
}
