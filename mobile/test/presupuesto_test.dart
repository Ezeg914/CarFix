import 'dart:convert';
import 'dart:io';

import 'package:carfix/models/presupuesto.dart';
import 'package:carfix/widgets/formato.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  // Respuesta real de la API para samples/vento_2012.jpg
  final json = jsonDecode(File('test/fixtures/presupuesto_vento.json').readAsStringSync());

  test('lee el presupuesto que devuelve la API', () {
    final p = Presupuesto.fromJson(json);

    expect(p.vehiculo.descripcion, 'Volkswagen Vento 2012');
    expect(p.piezas.map((x) => (x.nombre, x.accion)), [
      ('Óptica delantera', Accion.cambiar),
      ('Paragolpes delantero', Accion.cambiar),
      ('Capot', Accion.reparar),
    ]);
    expect(p.revisar.single.nombre, 'Parabrisas');
    expect(p.revisar.single.confianzaMaxima, closeTo(0.65, 0.01));
    expect(p.faltanPrecios, isTrue);
    expect(p.vehiculoEncontrado, isTrue);
  });

  test('una acción desconocida se trata como revisar', () {
    final pieza = PiezaPresupuesto.fromJson({'nombre': 'X', 'accion': 'otra'});
    expect(pieza.accion, Accion.revisar);
    expect(pieza.danios, isEmpty);
  });

  test('formato de precios con punto de miles', () {
    expect(formatoPrecio(0), '\$ 0');
    expect(formatoPrecio(950), '\$ 950');
    expect(formatoPrecio(1234567.4), '\$ 1.234.567');
  });
}
