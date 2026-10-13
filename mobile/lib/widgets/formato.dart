import 'package:flutter/material.dart';

import '../models/presupuesto.dart';

/// "$ 12.345" con punto de miles, como se escribe en Argentina.
String formatoPrecio(double valor) {
  final entero = valor.round().toString();
  final conPuntos = entero.replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (_) => '.');
  return '\$ $conPuntos';
}

String formatoPorcentaje(double valor) => '${(valor * 100).round()}%';

extension AccionUi on Accion {
  String get etiqueta => switch (this) {
    Accion.cambiar => 'Cambiar',
    Accion.reparar => 'Reparar',
    Accion.pintar => 'Pintar',
    Accion.revisar => 'Revisar',
  };

  IconData get icono => switch (this) {
    Accion.cambiar => Icons.swap_horiz,
    Accion.reparar => Icons.build,
    Accion.pintar => Icons.format_paint,
    Accion.revisar => Icons.help_outline,
  };

  Color color(ColorScheme scheme) => switch (this) {
    Accion.cambiar => scheme.error,
    Accion.reparar => Colors.orange.shade700,
    Accion.pintar => scheme.primary,
    Accion.revisar => scheme.outline,
  };
}
