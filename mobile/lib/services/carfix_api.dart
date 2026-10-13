import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

import '../models/presupuesto.dart';

class Analisis {
  const Analisis({required this.presupuesto, required this.imagen});

  final Presupuesto presupuesto;

  /// Foto con las piezas y los daños marcados (JPEG).
  final Uint8List imagen;
}

class CarFixApiException implements Exception {
  const CarFixApiException(this.mensaje);

  final String mensaje;

  @override
  String toString() => mensaje;
}

/// Cliente de la API del backend (`backend/carfix/api.py`).
class CarFixApi {
  CarFixApi(this.baseUrl, {http.Client? client}) : _client = client ?? http.Client();

  final String baseUrl;
  final http.Client _client;

  // Analizar una foto en CPU puede tardar varios segundos.
  static const _timeout = Duration(seconds: 90);

  Uri _uri(String path) => Uri.parse(baseUrl.replaceAll(RegExp(r'/+$'), '') + path);

  Future<Analisis> analizar({
    required Uint8List foto,
    required String nombreArchivo,
    required String marca,
    required String modelo,
    required String anio,
  }) async {
    final request = http.MultipartRequest('POST', _uri('/analizar'))
      ..fields.addAll({'marca': marca, 'modelo': modelo, 'anio': anio})
      ..files.add(http.MultipartFile.fromBytes('foto', foto, filename: nombreArchivo));

    final http.Response response;
    try {
      response = await http.Response.fromStream(await _client.send(request).timeout(_timeout));
    } catch (_) {
      throw CarFixApiException(
        'No se pudo conectar con el servidor ($baseUrl). Revisá que la API esté corriendo y la dirección en Ajustes.',
      );
    }

    final body = _decode(response);
    if (response.statusCode != 200) {
      throw CarFixApiException(body['detail']?.toString() ?? 'Error del servidor (${response.statusCode})');
    }
    return Analisis(
      presupuesto: Presupuesto.fromJson(body['presupuesto'] as Map<String, dynamic>),
      imagen: base64Decode(body['imagen'] as String),
    );
  }

  Map<String, dynamic> _decode(http.Response response) {
    try {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } catch (_) {
      throw CarFixApiException('Respuesta inválida del servidor (${response.statusCode})');
    }
  }
}
