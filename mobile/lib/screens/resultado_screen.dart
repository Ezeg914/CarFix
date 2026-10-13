import 'package:flutter/material.dart';

import '../models/presupuesto.dart';
import '../services/carfix_api.dart';
import '../widgets/formato.dart';
import '../widgets/pieza_card.dart';

/// Foto con los daños marcados y el presupuesto.
class ResultadoScreen extends StatelessWidget {
  const ResultadoScreen({super.key, required this.analisis});

  final Analisis analisis;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final p = analisis.presupuesto;

    return Scaffold(
      appBar: AppBar(title: const Text('Presupuesto')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: InteractiveViewer(maxScale: 5, child: Image.memory(analisis.imagen)),
            ),
            const SizedBox(height: 8),
            Text('Celeste: piezas detectadas. Rojo: daños.', style: theme.textTheme.bodySmall),
            if (!p.vehiculoEncontrado)
              const _Aviso('No se encontró el vehículo en la foto; se analizó la imagen completa.'),
            const SizedBox(height: 16),
            _Resumen(presupuesto: p),
            const SizedBox(height: 16),
            if (p.piezas.isEmpty)
              const _Aviso('No se detectaron daños sobre piezas.')
            else
              for (final pieza in p.piezas) PiezaCard(pieza: pieza),
            if (p.revisar.isNotEmpty) ...[
              const SizedBox(height: 24),
              Text('Para revisar a mano', style: theme.textTheme.titleMedium),
              Text(
                'Posibles daños con poca confianza (por ejemplo reflejos). No suman al total.',
                style: theme.textTheme.bodySmall,
              ),
              const SizedBox(height: 8),
              for (final pieza in p.revisar)
                ListTile(
                  leading: Icon(Accion.revisar.icono),
                  title: Text(pieza.nombre),
                  subtitle: Text('${formatoPorcentaje(pieza.confianzaMaxima)} de confianza'),
                ),
            ],
          ],
        ),
      ),
    );
  }
}

class _Resumen extends StatelessWidget {
  const _Resumen({required this.presupuesto});

  final Presupuesto presupuesto;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final p = presupuesto;
    return Card(
      color: theme.colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(p.vehiculo.descripcion, style: theme.textTheme.titleLarge),
            const SizedBox(height: 4),
            Text('${p.piezas.length} pieza(s) con daño'),
            const SizedBox(height: 12),
            Row(
              children: [
                Text('Total', style: theme.textTheme.titleMedium),
                const Spacer(),
                Text(formatoPrecio(p.total), style: theme.textTheme.headlineSmall),
              ],
            ),
            if (p.faltanPrecios) Text('Hay ítems sin precio todavía', style: theme.textTheme.bodySmall),
          ],
        ),
      ),
    );
  }
}

class _Aviso extends StatelessWidget {
  const _Aviso(this.texto);

  final String texto;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Row(
        children: [
          Icon(Icons.info_outline, color: Theme.of(context).colorScheme.outline),
          const SizedBox(width: 8),
          Expanded(child: Text(texto)),
        ],
      ),
    );
  }
}
