// Author origin: RainStudy/ShoreRoute, at RainStudy z=10.8 m.
// The saved rain map covers |x| <= 10.5 and RainStudy z=-8.5..16.5.
world_map_bounds = [90, 100];
world_seed = 1124;

// The old surface is y=-0.70. Butt the three new pieces up to its
// exact perimeter; overlapping coplanar water flickers from the boat.
module water_strip(x0,x1,z0,z1) {
  translate([-x1, -(z1-10.8), -0.82]) cube([x1-x0, z1-z0, 0.12]);
}
world_material([0.032,0.089,0.11], roughness=0.18, metalness=0.36) {
  water_strip(-44,44,16.5,60);
  water_strip(-44,-10.5,-8.5,16.5);
  water_strip(10.5,44,-8.5,16.5);
}
