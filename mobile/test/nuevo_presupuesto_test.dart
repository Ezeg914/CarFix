import 'package:carfix/app.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('pide completar los datos antes de analizar', (tester) async {
    await tester.pumpWidget(const CarFixApp());

    await tester.scrollUntilVisible(
      find.text('Analizar daños'),
      200,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(find.text('Analizar daños'));
    await tester.pump();

    expect(find.text('Completá este dato'), findsNWidgets(2));
    expect(find.textContaining('Año entre 1950'), findsOneWidget);
  });

  testWidgets('pide una foto si faltan solo la foto', (tester) async {
    await tester.pumpWidget(const CarFixApp());

    await tester.enterText(find.widgetWithText(TextFormField, 'Marca'), 'Volkswagen');
    await tester.enterText(find.widgetWithText(TextFormField, 'Modelo'), 'Vento');
    await tester.enterText(find.widgetWithText(TextFormField, 'Año'), '2012');
    await tester.scrollUntilVisible(
      find.text('Analizar daños'),
      200,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(find.text('Analizar daños'));
    await tester.pump();

    expect(find.text('Sacá o elegí una foto del vehículo.'), findsOneWidget);
  });
}
