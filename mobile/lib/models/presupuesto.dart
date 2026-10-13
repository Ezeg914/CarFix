/// Modelos del JSON que devuelve `POST /analizar`.
library;

enum Accion { cambiar, reparar, pintar, revisar }

Accion _parseAccion(String value) =>
    Accion.values.firstWhere((a) => a.name == value, orElse: () => Accion.revisar);

double _toDouble(Object? value) => (value as num?)?.toDouble() ?? 0;

class Vehiculo {
  const Vehiculo({required this.marca, required this.modelo, required this.anio});

  final String marca;
  final String modelo;
  final String anio;

  factory Vehiculo.fromJson(Map<String, dynamic> json) => Vehiculo(
    marca: json['marca']?.toString() ?? '',
    modelo: json['modelo']?.toString() ?? '',
    anio: json['anio']?.toString() ?? '',
  );

  String get descripcion => [marca, modelo, anio].where((s) => s.isNotEmpty).join(' ');
}

class Danio {
  const Danio({required this.categoria, required this.confianza, required this.cobertura});

  final String categoria;

  /// Confianza del modelo, de 0 a 1.
  final double confianza;

  /// Parte de la pieza que cubre el daño, de 0 a 1.
  final double cobertura;

  factory Danio.fromJson(Map<String, dynamic> json) => Danio(
    categoria: json['categoria']?.toString() ?? '',
    confianza: _toDouble(json['conf']),
    cobertura: _toDouble(json['cobertura']),
  );
}

class Item {
  const Item({required this.concepto, required this.precio});

  final String concepto;
  final double precio;

  factory Item.fromJson(Map<String, dynamic> json) =>
      Item(concepto: json['concepto']?.toString() ?? '', precio: _toDouble(json['precio']));
}

class PiezaPresupuesto {
  const PiezaPresupuesto({
    required this.nombre,
    required this.accion,
    required this.motivo,
    required this.danios,
    required this.items,
    required this.subtotal,
  });

  final String nombre;
  final Accion accion;
  final String motivo;
  final List<Danio> danios;
  final List<Item> items;
  final double subtotal;

  factory PiezaPresupuesto.fromJson(Map<String, dynamic> json) => PiezaPresupuesto(
    nombre: json['nombre']?.toString() ?? '',
    accion: _parseAccion(json['accion']?.toString() ?? ''),
    motivo: json['motivo']?.toString() ?? '',
    danios: [for (final d in json['danios'] as List? ?? []) Danio.fromJson(d)],
    items: [for (final i in json['items'] as List? ?? []) Item.fromJson(i)],
    subtotal: _toDouble(json['subtotal']),
  );

  double get confianzaMaxima => danios.fold(0, (max, d) => d.confianza > max ? d.confianza : max);
}

class Presupuesto {
  const Presupuesto({
    required this.vehiculo,
    required this.piezas,
    required this.revisar,
    required this.total,
    required this.faltanPrecios,
    required this.vehiculoEncontrado,
  });

  final Vehiculo vehiculo;

  /// Piezas que suman al total.
  final List<PiezaPresupuesto> piezas;

  /// Posibles daños dudosos (por ej. reflejos): no suman al total.
  final List<PiezaPresupuesto> revisar;
  final double total;
  final bool faltanPrecios;
  final bool vehiculoEncontrado;

  factory Presupuesto.fromJson(Map<String, dynamic> json) => Presupuesto(
    vehiculo: Vehiculo.fromJson(json['vehiculo'] as Map<String, dynamic>? ?? {}),
    piezas: [for (final p in json['piezas'] as List? ?? []) PiezaPresupuesto.fromJson(p)],
    revisar: [for (final p in json['revisar'] as List? ?? []) PiezaPresupuesto.fromJson(p)],
    total: _toDouble(json['total']),
    faltanPrecios: json['faltan_precios'] as bool? ?? false,
    vehiculoEncontrado: json['vehiculo_encontrado'] as bool? ?? true,
  );
}
