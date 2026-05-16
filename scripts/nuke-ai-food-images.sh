#!/usr/bin/env bash
# nuke-ai-food-images.sh
# Deletes the 110 AI-generated food image files (Gemini renders) that the
# 2026-05-16 cleanup pass orphaned. The matching <figure> blocks were already
# stripped from HTML in the same pass. Most renders were wrong (Venezuelan
# arepas, Thai-looking sancocho, flat arepas de huevo).
#
# Pattern: /img/<page-slug>-food-<entity>.{jpg,webp}
#
# Usage:  bash scripts/nuke-ai-food-images.sh

set -e
cd "$(dirname "$0")/.."

deleted=0
freed=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  if [ -f "img/$f" ]; then
    sz=$(stat -f%z "img/$f" 2>/dev/null || stat -c%s "img/$f" 2>/dev/null || echo 0)
    git rm -q --cached -- "img/$f" 2>/dev/null || true
    rm -f -- "img/$f"
    deleted=$((deleted + 1))
    freed=$((freed + sz))
  fi
done <<'FILES'
barranquilla-carnival-complete-guide-food-arepas-de-huevo.jpg
barranquilla-carnival-complete-guide-food-arepas-de-huevo.webp
barranquilla-carnival-complete-guide-food-butifarra-with-bollo.jpg
barranquilla-carnival-complete-guide-food-butifarra-with-bollo.webp
barranquilla-food-tour-downtown-food-arepas-de-huevo.jpg
barranquilla-food-tour-downtown-food-arepas-de-huevo.webp
barranquilla-food-tour-downtown-food-ceviche-costeno.jpg
barranquilla-food-tour-downtown-food-ceviche-costeno.webp
barranquilla-food-tour-downtown-food-chicharron.jpg
barranquilla-food-tour-downtown-food-chicharron.webp
barranquilla-food-tour-downtown-food-mote-de-queso.jpg
barranquilla-food-tour-downtown-food-mote-de-queso.webp
barranquilla-food-tour-downtown-food-patacones.jpg
barranquilla-food-tour-downtown-food-patacones.webp
barranquilla-food-tour-downtown-food-pescado-frito.jpg
barranquilla-food-tour-downtown-food-pescado-frito.webp
barranquilla-food-tour-downtown-food-sancocho-de-pescado.jpg
barranquilla-food-tour-downtown-food-sancocho-de-pescado.webp
barranquilla-nightlife-bars-clubs-food-cocteles.jpg
barranquilla-nightlife-bars-clubs-food-cocteles.webp
barranquilla-nightlife-bars-clubs-food-fritos.jpg
barranquilla-nightlife-bars-clubs-food-fritos.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-ajiaco.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-ajiaco.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-arepas-de-huevo.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-arepas-de-huevo.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-bandeja-paisa.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-bandeja-paisa.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-buñuelos.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-buñuelos.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-fritos.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-fritos.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-mondongo.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-mondongo.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-pescado-frito.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-pescado-frito.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-sancocho.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-sancocho.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-tamales-tolimenses.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-tamales-tolimenses.webp
barranquilla-wedding-guide-2026-food-arepas.jpg
barranquilla-wedding-guide-2026-food-arepas.webp
barranquilla-wedding-guide-2026-food-bocas.jpg
barranquilla-wedding-guide-2026-food-bocas.webp
barranquilla-wedding-guide-2026-food-cocteles.jpg
barranquilla-wedding-guide-2026-food-cocteles.webp
barranquilla-wedding-guide-2026-food-flores.jpg
barranquilla-wedding-guide-2026-food-flores.webp
barranquilla-wedding-guide-2026-food-frutas-tropicales.jpg
barranquilla-wedding-guide-2026-food-frutas-tropicales.webp
barranquilla-wedding-guide-2026-food-pescado.jpg
barranquilla-wedding-guide-2026-food-pescado.webp
barranquilla-wedding-guide-2026-food-postres.jpg
barranquilla-wedding-guide-2026-food-postres.webp
barranquilla-wedding-guide-2026-food-sancocho.jpg
barranquilla-wedding-guide-2026-food-sancocho.webp
barranquilla-with-kids-family-guide-2026-food-postres.jpg
barranquilla-with-kids-family-guide-2026-food-postres.webp
best-bars-craft-drinks-barranquilla-food-cervezas-artesanales.jpg
best-bars-craft-drinks-barranquilla-food-cervezas-artesanales.webp
best-bars-craft-drinks-barranquilla-food-cocteles.jpg
best-bars-craft-drinks-barranquilla-food-cocteles.webp
best-desserts-barranquilla-food-postres.jpg
best-desserts-barranquilla-food-postres.webp
best-family-restaurants-barranquilla-food-arepas.jpg
best-family-restaurants-barranquilla-food-arepas.webp
best-family-restaurants-barranquilla-food-bandeja-paisa.jpg
best-family-restaurants-barranquilla-food-bandeja-paisa.webp
best-family-restaurants-barranquilla-food-hamburguesas.jpg
best-family-restaurants-barranquilla-food-hamburguesas.webp
best-family-restaurants-barranquilla-food-helados.jpg
best-family-restaurants-barranquilla-food-helados.webp
best-family-restaurants-barranquilla-food-pasta.jpg
best-family-restaurants-barranquilla-food-pasta.webp
best-family-restaurants-barranquilla-food-patacones.jpg
best-family-restaurants-barranquilla-food-patacones.webp
best-family-restaurants-barranquilla-food-pescado.jpg
best-family-restaurants-barranquilla-food-pescado.webp
best-family-restaurants-barranquilla-food-pizza.jpg
best-family-restaurants-barranquilla-food-pizza.webp
best-family-restaurants-barranquilla-food-pollo.jpg
best-family-restaurants-barranquilla-food-pollo.webp
best-night-out-barranquilla-food-cervezas-artesanales.jpg
best-night-out-barranquilla-food-cervezas-artesanales.webp
best-night-out-barranquilla-food-cocteles.jpg
best-night-out-barranquilla-food-cocteles.webp
best-night-out-barranquilla-food-tequila.jpg
best-night-out-barranquilla-food-tequila.webp
best-restaurants-with-children-barranquilla-food-arepas.jpg
best-restaurants-with-children-barranquilla-food-arepas.webp
best-restaurants-with-children-barranquilla-food-bandeja-paisa.jpg
best-restaurants-with-children-barranquilla-food-bandeja-paisa.webp
best-restaurants-with-children-barranquilla-food-hamburguesas.jpg
best-restaurants-with-children-barranquilla-food-hamburguesas.webp
best-restaurants-with-children-barranquilla-food-helados.jpg
best-restaurants-with-children-barranquilla-food-helados.webp
best-restaurants-with-children-barranquilla-food-pasta.jpg
best-restaurants-with-children-barranquilla-food-pasta.webp
best-restaurants-with-children-barranquilla-food-pizza.jpg
best-restaurants-with-children-barranquilla-food-pizza.webp
best-restaurants-with-children-barranquilla-food-pollo-asado.jpg
best-restaurants-with-children-barranquilla-food-pollo-asado.webp
best-tours-experiences-barranquilla-food-arepas-de-huevo.jpg
best-tours-experiences-barranquilla-food-arepas-de-huevo.webp
best-tours-experiences-barranquilla-food-patacones.jpg
best-tours-experiences-barranquilla-food-patacones.webp
fun-things-to-do-in-barranquilla-as-a-group-food-postres.jpg
fun-things-to-do-in-barranquilla-as-a-group-food-postres.webp
miramar-food-pandebono.jpg
miramar-food-pandebono.webp
puerto-colombia-food-arroz-de-mariscos.jpg
puerto-colombia-food-arroz-de-mariscos.webp
puerto-mocho-food-patacones.jpg
puerto-mocho-food-patacones.webp
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-arepas-de-huevo.jpg
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-arepas-de-huevo.webp
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-frutas-tropicales.jpg
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-frutas-tropicales.webp
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-mango-biche.jpg
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-mango-biche.webp
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-mariscos.jpg
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-mariscos.webp
FILES

freed_mb=$((freed / 1024 / 1024))
echo "Deleted $deleted AI food image files, freed $freed_mb MB."
