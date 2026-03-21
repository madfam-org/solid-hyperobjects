// Yantra4D wrapper — PolyDiceGenerator
// render_mode: 0=d4, 1=d6, 2=d8, 3=d12, 4=d20

die_size = 20;
font_depth = 0.6;
font_size = 6;
rounding_corner = 0;
rounding_edge = 0;
render_mode = 0;
fn = 0;

// Override library toggles — only the selected die is enabled
d2 = false;
d3 = false;
d4 = (render_mode == 0);
d4p = false;
d6 = (render_mode == 1);
d8 = (render_mode == 2);
d10 = false;
d00 = false;
d12 = (render_mode == 3);
d12r = false;
d16 = false;
d20 = (render_mode == 4);

// Size overrides — uniform across all die types
d4_size = die_size;
d6_size = die_size;
d8_size = die_size;
d12_size = die_size;
d20_size = die_size;

// Text overrides
text_depth = font_depth;
d4_text_size = font_size;
d6_text_size = font_size;
d8_text_size = font_size;
d12_text_size = font_size;
d20_text_size = font_size;

// Rounding overrides
corner_rounding = rounding_corner;
edge_rounding = rounding_edge;

// Quality override
$fn = fn > 0 ? fn : 32;

include <PolyDiceGenerator.scad>
