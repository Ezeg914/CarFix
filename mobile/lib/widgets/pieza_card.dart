import 'package:flutter/material.dart';

import '../models/presupuesto.dart';
import 'formato.dart';

/// Una pieza del presupuesto: qué hacer, por qué y cuánto sale.
class PiezaCard extends StatelessWidget {
  const PiezaCard({super.key, required this.pieza});

  final PiezaPresupuesto pieza;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = pieza.accion.color(theme.colorScheme);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text(pieza.nombre, style: theme.textTheme.titleMedium)),
                Chip(
                  avatar: Icon(pieza.accion.icono, size: 18, color: color),
                  label: Text(pieza.accion.etiqueta),
                  labelStyle: TextStyle(color: color, fontWeight: FontWeight.w600),
                  side: BorderSide(color: color),
                  visualDensity: VisualDensity.compact,
                ),
              ],
            ),
            Text(pieza.motivo, style: theme.textTheme.bodySmall),
            if (pieza.items.isNotEmpty) ...[
              const Divider(height: 24),
              for (final item in pieza.items)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2),
                  child: Row(
                    children: [
                      Expanded(child: Text(item.concepto)),
                      Text(
                        item.precio > 0 ? formatoPrecio(item.precio) : 'sin precio',
                        style: item.precio > 0 ? null : TextStyle(color: theme.colorScheme.outline),
                      ),
                    ],
                  ),
                ),
            ],
          ],
        ),
      ),
    );
  }
}
