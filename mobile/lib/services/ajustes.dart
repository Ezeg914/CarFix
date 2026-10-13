import 'package:shared_preferences/shared_preferences.dart';

/// Guarda en el teléfono la dirección de la API.
class Ajustes {
  static const _claveServidor = 'servidor';

  /// En el emulador de Android, 10.0.2.2 es la PC. En un celular real hay que
  /// poner la IP de la PC en la red local, por ej. http://192.168.0.10:8000
  static const servidorPorDefecto = 'http://10.0.2.2:8000';

  static Future<String> servidor() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_claveServidor) ?? servidorPorDefecto;
  }

  static Future<void> guardarServidor(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_claveServidor, url.trim());
  }
}
