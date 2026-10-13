import 'dart:convert';
import 'dart:typed_data';

import 'package:carfix/services/carfix_api.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  final foto = Uint8List.fromList([1, 2, 3]);

  Future<Analisis> analizar(CarFixApi api) =>
      api.analizar(foto: foto, nombreArchivo: 'auto.jpg', marca: 'VW', modelo: 'Vento', anio: '2012');

  test('manda la foto y los datos, y lee la respuesta', () async {
    late http.BaseRequest enviado;
    final client = MockClient((request) async {
      enviado = request;
      return http.Response(
        jsonEncode({
          'presupuesto': {
            'vehiculo': {'marca': 'VW'},
            'piezas': [],
            'revisar': [],
            'total': 0,
          },
          'imagen': base64Encode([9, 9]),
        }),
        200,
      );
    });

    final analisis = await analizar(CarFixApi('http://pc:8000/', client: client));

    expect(enviado.url.toString(), 'http://pc:8000/analizar');
    expect(enviado.method, 'POST');
    expect(analisis.presupuesto.vehiculo.marca, 'VW');
    expect(analisis.imagen, [9, 9]);
  });

  test('muestra el mensaje de error de la API', () async {
    final client = MockClient(
      (_) async =>
          http.Response.bytes(utf8.encode(jsonEncode({'detail': 'El archivo no es una imagen válida'})), 400),
    );

    await expectLater(
      analizar(CarFixApi('http://pc:8000', client: client)),
      throwsA(
        isA<CarFixApiException>().having((e) => e.mensaje, 'mensaje', 'El archivo no es una imagen válida'),
      ),
    );
  });

  test('avisa si no puede conectarse', () async {
    final client = MockClient((_) async => throw http.ClientException('sin red'));

    expect(analizar(CarFixApi('http://pc:8000', client: client)), throwsA(isA<CarFixApiException>()));
  });
}
