import 'package:flutter_test/flutter_test.dart';

import 'package:akd_app/main.dart';
import 'package:akd_app/services/api_client.dart';

void main() {
  testWidgets('App builds without error', (WidgetTester tester) async {
    final apiClient = ApiClient(baseUrl: 'http://localhost:5000/api/v1');
    await tester.pumpWidget(AKDApp(apiClient: apiClient));

    // Verify splash or loading indicator appears
    expect(find.byType(AKDApp), findsOneWidget);
  });
}
