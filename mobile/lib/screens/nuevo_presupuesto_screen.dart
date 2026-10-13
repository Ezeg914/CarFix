import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../services/ajustes.dart';
import '../services/carfix_api.dart';
import 'resultado_screen.dart';

/// Datos del vehículo y foto a analizar.
class NuevoPresupuestoScreen extends StatefulWidget {
  const NuevoPresupuestoScreen({super.key});

  @override
  State<NuevoPresupuestoScreen> createState() => _NuevoPresupuestoScreenState();
}

class _NuevoPresupuestoScreenState extends State<NuevoPresupuestoScreen> {
  final _formKey = GlobalKey<FormState>();
  final _marca = TextEditingController();
  final _modelo = TextEditingController();
  final _anio = TextEditingController();
  final _picker = ImagePicker();

  Uint8List? _foto;
  String _nombreFoto = 'foto.jpg';
  bool _analizando = false;

  @override
  void dispose() {
    _marca.dispose();
    _modelo.dispose();
    _anio.dispose();
    super.dispose();
  }

  Future<void> _elegirFoto(ImageSource source) async {
    // La foto se achica en el teléfono: el modelo trabaja a 1024 px y así se sube más rápido.
    final file = await _picker.pickImage(source: source, maxWidth: 2048, maxHeight: 2048, imageQuality: 90);
    if (file == null) return;
    final bytes = await file.readAsBytes();
    setState(() {
      _foto = bytes;
      _nombreFoto = file.name;
    });
  }

  Future<void> _analizar() async {
    if (!_formKey.currentState!.validate()) return;
    final foto = _foto;
    if (foto == null) {
      _mostrarError('Sacá o elegí una foto del vehículo.');
      return;
    }

    setState(() => _analizando = true);
    try {
      final api = CarFixApi(await Ajustes.servidor());
      final analisis = await api.analizar(
        foto: foto,
        nombreArchivo: _nombreFoto,
        marca: _marca.text.trim(),
        modelo: _modelo.text.trim(),
        anio: _anio.text.trim(),
      );
      if (!mounted) return;
      await Navigator.of(context)
          .push(MaterialPageRoute(builder: (_) => ResultadoScreen(analisis: analisis)));
    } on CarFixApiException catch (e) {
      _mostrarError(e.mensaje);
    } finally {
      if (mounted) setState(() => _analizando = false);
    }
  }

  void _mostrarError(String mensaje) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(mensaje)));
  }

  Future<void> _editarServidor() async {
    final controller = TextEditingController(text: await Ajustes.servidor());
    if (!mounted) return;
    final url = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Dirección de la API'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.url,
          decoration: const InputDecoration(
            hintText: 'http://192.168.0.10:8000',
            helperText: 'La IP de la PC donde corre el backend',
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
          FilledButton(
            onPressed: () => Navigator.pop(context, controller.text),
            child: const Text('Guardar'),
          ),
        ],
      ),
    );
    controller.dispose();
    if (url != null && url.trim().isNotEmpty) await Ajustes.guardarServidor(url);
  }

  String? _requerido(String? value) => (value == null || value.trim().isEmpty) ? 'Completá este dato' : null;

  String? _validarAnio(String? value) {
    final anio = int.tryParse(value?.trim() ?? '');
    final actual = DateTime.now().year + 1;
    if (anio == null || anio < 1950 || anio > actual) return 'Año entre 1950 y $actual';
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('CarFix'),
        actions: [
          IconButton(
            tooltip: 'Ajustes',
            icon: const Icon(Icons.settings_outlined),
            onPressed: _analizando ? null : _editarServidor,
          ),
        ],
      ),
      body: SafeArea(
        child: Form(
          key: _formKey,
          // Column y no ListView: así los campos nunca se descartan y el formulario los valida todos.
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('Vehículo', style: theme.textTheme.titleMedium),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _marca,
                  decoration: const InputDecoration(labelText: 'Marca', border: OutlineInputBorder()),
                  textCapitalization: TextCapitalization.words,
                  textInputAction: TextInputAction.next,
                  validator: _requerido,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _modelo,
                  decoration: const InputDecoration(labelText: 'Modelo', border: OutlineInputBorder()),
                  textCapitalization: TextCapitalization.words,
                  textInputAction: TextInputAction.next,
                  validator: _requerido,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _anio,
                  decoration: const InputDecoration(labelText: 'Año', border: OutlineInputBorder()),
                  keyboardType: TextInputType.number,
                  validator: _validarAnio,
                ),
                const SizedBox(height: 24),
                Text('Foto del daño', style: theme.textTheme.titleMedium),
                const SizedBox(height: 12),
                _VistaPrevia(foto: _foto),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: _analizando ? null : () => _elegirFoto(ImageSource.camera),
                        icon: const Icon(Icons.photo_camera_outlined),
                        label: const Text('Cámara'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: _analizando ? null : () => _elegirFoto(ImageSource.gallery),
                        icon: const Icon(Icons.photo_library_outlined),
                        label: const Text('Galería'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                FilledButton.icon(
                  onPressed: _analizando ? null : _analizar,
                  icon: _analizando
                      ? const SizedBox.square(dimension: 18, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.search),
                  label: Text(_analizando ? 'Analizando…' : 'Analizar daños'),
                  style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(52)),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _VistaPrevia extends StatelessWidget {
  const _VistaPrevia({required this.foto});

  final Uint8List? foto;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return AspectRatio(
      aspectRatio: 4 / 3,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: foto != null
            ? Image.memory(foto!, fit: BoxFit.cover)
            : ColoredBox(
                color: scheme.surfaceContainerHighest,
                child: Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.directions_car_outlined, size: 48, color: scheme.outline),
                      const SizedBox(height: 8),
                      Text('Sin foto todavía', style: TextStyle(color: scheme.outline)),
                    ],
                  ),
                ),
              ),
      ),
    );
  }
}
