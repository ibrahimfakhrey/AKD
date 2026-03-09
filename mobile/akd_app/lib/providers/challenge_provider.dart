import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import '../models/challenge.dart';
import '../services/api_client.dart';
import '../services/challenge_service.dart';

/// Challenge state provider — with live countdown timer.
class ChallengeProvider extends ChangeNotifier {
  final ApiClient api;
  late final ChallengeService _service;

  Challenge? _active;
  List<Challenge> _history = [];
  List<Challenge> _received = [];
  bool _loading = false;
  String? _error;
  Timer? _timer;
  Duration _remaining = Duration.zero;

  ChallengeProvider({required this.api}) {
    _service = ChallengeService(api);
  }

  Challenge? get active => _active;
  List<Challenge> get history => _history;
  List<Challenge> get received => _received;
  bool get loading => _loading;
  String? get error => _error;
  Duration get remaining => _remaining;

  String get formattedRemaining {
    final m = _remaining.inMinutes.remainder(60).toString().padLeft(2, '0');
    final s = _remaining.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '${_remaining.inHours > 0 ? '${_remaining.inHours}:' : ''}$m:$s';
  }

  Future<void> fetchActive() async {
    _loading = true;
    notifyListeners();
    try {
      _active = await _service.getActive();
      _startTimer();
    } catch (_) {}
    _loading = false;
    notifyListeners();
  }

  Future<void> fetchReceived() async {
    try {
      _received = await _service.getReceived();
      if (_received.isNotEmpty) _startTimer();
      notifyListeners();
    } catch (_) {}
  }

  Future<bool> startChallenge({String? description}) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _active = await _service.start(description: description);
      _startTimer();
      _loading = false;
      notifyListeners();
      return true;
    } on DioException catch (e) {
      _error = api.errorMessage(e);
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  /// Send a challenge to a friend — costs the sender 50 points.
  Future<bool> sendToFriend(String friendUserId, {String? description}) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      await _service.sendToFriend(friendUserId, description: description);
      _loading = false;
      notifyListeners();
      return true;
    } on DioException catch (e) {
      _error = api.errorMessage(e);
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> submitProof(List<int> bytes, String filename) async {
    if (_active == null) return false;
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      await _service.submitProof(_active!.id, bytes, filename);
      _stopTimer();
      _active = null;
      _loading = false;
      notifyListeners();
      return true;
    } on DioException catch (e) {
      _error = api.errorMessage(e);
      _loading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _error = 'Could not submit proof: $e';
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  /// Submit proof for a received (friend-sent) challenge by its id.
  Future<bool> submitReceivedProof(
    String challengeId,
    List<int> bytes,
    String filename,
  ) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      await _service.submitProof(challengeId, bytes, filename);
      await fetchReceived();
      _loading = false;
      notifyListeners();
      return true;
    } on DioException catch (e) {
      _error = api.errorMessage(e);
      _loading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _error = 'Could not submit proof: $e';
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> fetchHistory() async {
    try {
      _history = await _service.listHistory();
      notifyListeners();
    } catch (_) {}
  }

  void _startTimer() {
    _stopTimer();
    if ((_active == null || !_active!.isActive) && _received.isEmpty) return;

    if (_active != null && _active!.isActive) {
      _remaining = _active!.timeRemaining;
    }

    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      bool changed = false;

      if (_active != null && _active!.isActive) {
        _remaining = _active!.timeRemaining;
        if (_remaining <= Duration.zero) {
          _stopTimer();
          _active = null;
          changed = true;
        } else {
          changed = true;
        }
      }

      if (_received.isNotEmpty) {
        changed = true; // Always notify to tick received UI timers
        // Update local status of expired received challenges
        for (var c in _received) {
          if (c.timeRemaining <= Duration.zero && c.status == 'active') {
            c.status = 'expired';
          }
        }
      }

      if (changed) notifyListeners();
    });
  }

  void _stopTimer() {
    _timer?.cancel();
    _timer = null;
  }

  @override
  void dispose() {
    _stopTimer();
    super.dispose();
  }
}
