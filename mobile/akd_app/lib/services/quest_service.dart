import 'package:dio/dio.dart';
import '../models/quest.dart';
import 'api_client.dart';

/// Quest service — daily quests and proof submission.
class QuestService {
  final ApiClient _api;

  QuestService(this._api);

  /// GET /quests/daily
  Future<List<DailyQuest>> getDailyQuests() async {
    final res = await _api.dio.get('/quests/daily');
    return (res.data as List).map((j) => DailyQuest.fromJson(j)).toList();
  }

  /// POST /quests/<questId>/submit — multipart photo upload
  Future<Map<String, dynamic>> submitProof(
    String questId,
    List<int> bytes,
    String filename,
  ) async {
    final formData = FormData.fromMap({
      'photo': MultipartFile.fromBytes(bytes, filename: filename),
    });
    final res = await _api.dio.post(
      '/quests/$questId/submit',
      data: formData,
      options: Options(contentType: 'multipart/form-data'),
    );
    return res.data;
  }
}
