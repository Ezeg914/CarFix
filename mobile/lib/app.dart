import 'package:flutter/material.dart';

import 'screens/nuevo_presupuesto_screen.dart';

class CarFixApp extends StatelessWidget {
  const CarFixApp({super.key});

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xFF1565C0);
    return MaterialApp(
      title: 'CarFix',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: seed, useMaterial3: true),
      darkTheme: ThemeData(colorSchemeSeed: seed, brightness: Brightness.dark, useMaterial3: true),
      home: const NuevoPresupuestoScreen(),
    );
  }
}
