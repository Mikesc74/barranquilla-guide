#!/usr/bin/env bash
# archive-ai-food-images-v2.sh
# Second pass: archives the remaining AI -food- renders that v1 missed
# (different entity slug spellings like arepa-de-huevo vs arepas-de-huevo,
# plus fruits and drink variants).
#
# Destination: ~/code/_image-gen/archive/barranquilla/food/
#
# Usage:  bash scripts/archive-ai-food-images-v2.sh

set -e
cd "$(dirname "$0")/.."

DEST="$HOME/code/_image-gen/archive/barranquilla/food"
mkdir -p "$DEST"

moved=0
size_bytes=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  if [ -f "img/$f" ]; then
    sz=$(stat -f%z "img/$f" 2>/dev/null || stat -c%s "img/$f" 2>/dev/null || echo 0)
    git rm -q --cached -- "img/$f" 2>/dev/null || true
    mv -- "img/$f" "$DEST/$f"
    moved=$((moved + 1))
    size_bytes=$((size_bytes + sz))
  fi
done <<'FILES'
barranquilla-food-tour-downtown-food-corozo.jpg
barranquilla-food-tour-downtown-food-corozo.webp
barranquilla-food-tour-downtown-food-guanabana.jpg
barranquilla-food-tour-downtown-food-guanabana.webp
barranquilla-food-tour-downtown-food-maracuya.jpg
barranquilla-food-tour-downtown-food-maracuya.webp
barranquilla-nightlife-bars-clubs-food-aguardiente.jpg
barranquilla-nightlife-bars-clubs-food-aguardiente.webp
barranquilla-nightlife-bars-clubs-food-arepa-de-huevo.jpg
barranquilla-nightlife-bars-clubs-food-arepa-de-huevo.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-arepa-de-huevo.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-arepa-de-huevo.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-arepa-paisa.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-arepa-paisa.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-bollo.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-bollo.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-butifarra.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-butifarra.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-changua.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-changua.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-mojarra-frita.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-mojarra-frita.webp
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-sancocho-de-pescado.jpg
barranquilla-vs-medellin-vs-bogota-which-colombian-city-is-right-for-you-food-sancocho-de-pescado.webp
barranquilla-wedding-guide-2026-food-aguardiente.jpg
barranquilla-wedding-guide-2026-food-aguardiente.webp
barranquilla-wedding-guide-2026-food-bandeja-paisa.jpg
barranquilla-wedding-guide-2026-food-bandeja-paisa.webp
barranquilla-wedding-guide-2026-food-patacones.jpg
barranquilla-wedding-guide-2026-food-patacones.webp
barranquilla-wedding-guide-2026-food-ron-medellin.jpg
barranquilla-wedding-guide-2026-food-ron-medellin.webp
barranquilla-wedding-guide-2026-food-ron-viejo-de-caldas.jpg
barranquilla-wedding-guide-2026-food-ron-viejo-de-caldas.webp
barranquilla-wedding-guide-2026-food-rum-and-coke.jpg
barranquilla-wedding-guide-2026-food-rum-and-coke.webp
best-bars-craft-drinks-barranquilla-food-dulcinea-brown-ale.jpg
best-bars-craft-drinks-barranquilla-food-dulcinea-brown-ale.webp
best-bars-craft-drinks-barranquilla-food-the-boka-legend.jpg
best-bars-craft-drinks-barranquilla-food-the-boka-legend.webp
best-family-restaurants-barranquilla-food-arroz-rozzo-de-mariscos.jpg
best-family-restaurants-barranquilla-food-arroz-rozzo-de-mariscos.webp
best-family-restaurants-barranquilla-food-camarones-al-ajo.jpg
best-family-restaurants-barranquilla-food-camarones-al-ajo.webp
best-family-restaurants-barranquilla-food-coconut-rice.jpg
best-family-restaurants-barranquilla-food-coconut-rice.webp
best-family-restaurants-barranquilla-food-comida-corriente.jpg
best-family-restaurants-barranquilla-food-comida-corriente.webp
best-family-restaurants-barranquilla-food-margherita.jpg
best-family-restaurants-barranquilla-food-margherita.webp
best-family-restaurants-barranquilla-food-mojarra-frita.jpg
best-family-restaurants-barranquilla-food-mojarra-frita.webp
best-night-out-barranquilla-food-boka-legend-cocktail.jpg
best-night-out-barranquilla-food-boka-legend-cocktail.webp
best-night-out-barranquilla-food-dulcinea.jpg
best-night-out-barranquilla-food-dulcinea.webp
best-restaurants-with-children-barranquilla-food-costena-burger.jpg
best-restaurants-with-children-barranquilla-food-costena-burger.webp
best-restaurants-with-children-barranquilla-food-frozo-malt-shake.jpg
best-restaurants-with-children-barranquilla-food-frozo-malt-shake.webp
best-restaurants-with-children-barranquilla-food-passion-fruit.jpg
best-restaurants-with-children-barranquilla-food-passion-fruit.webp
best-restaurants-with-children-barranquilla-food-zapote.jpg
best-restaurants-with-children-barranquilla-food-zapote.webp
fun-things-to-do-in-barranquilla-as-a-group-food-arepas-de-huevo.jpg
fun-things-to-do-in-barranquilla-as-a-group-food-arepas-de-huevo.webp
puerto-colombia-food-arroz-con-coco.jpg
puerto-colombia-food-arroz-con-coco.webp
san-basilio-de-palenque-food-fried-red-snapper-with-coconut-rice-and-mango-sauce.jpg
san-basilio-de-palenque-food-fried-red-snapper-with-coconut-rice-and-mango-sauce.webp
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-arepas.jpg
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-arepas.webp
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-bunuelo.jpg
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-bunuelo.webp
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-pan-de-yuca.jpg
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-pan-de-yuca.webp
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-pandebono.jpg
supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026-food-pandebono.webp
FILES

mb=$((size_bytes / 1024 / 1024))
echo "Moved $moved AI food image files (~${mb} MB) to: $DEST"
