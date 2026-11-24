// Campus and eaves walk, metres. GLB assets own the fixed, baked surfaces.
world_map_bounds = [22, 28];
world_seed = 1123;

module volume(c, size) {
  translate([c[0]-size[0]/2, c[1]-size[1]/2, c[2]]) cube(size);
}
module subject(id, size, at) {
  translate(at)
    map_asset(instance_id=id, slot=id, proxy_size=size)
      volume([0,0,0], size);
}
// The water is specular and must continue responding to the runtime sky.
world_material([0.032,0.089,0.11], roughness=0.18, metalness=0.36)
  volume([0,-4,-0.82],[21,25,0.12]);

world_surface(id="walk",tags=["walkable"])
  world_collider(id="walk-floor",tags=["walkable","gameplay"],visual=false)
    volume([0,-4,-0.28],[5.8,14,0.28]);
world_collider(id="campus-wall",tags=["gameplay"],visual=false)
  volume([2.51,-1.02,0],[0.2,6.1,3.1]);
world_collider(id="old-wall",tags=["gameplay"],visual=false)
  volume([2.52,-7.52,0],[0.25,6.9,3.0]);
world_collider(id="hinge-post",tags=["gameplay"],visual=false)
  volume([-0.88,-4,0],[0.19,0.21,2.92]);
world_collider(id="table-body",tags=["gameplay"],visual=false)
  volume([1.20,-8,0],[1.17,0.76,0.80]);
world_collider(id="washbasin",tags=["gameplay"],visual=false)
  volume([-1.42,-5.5,0],[0.65,0.65,0.30]);
world_traversal_route(id="under-eaves",role="primary",points=[[0,1,0],[0,-2.3,0],[0,-4,0],[0,-5.5,0],[0,-8,0]],capsule=[0.32,1.72],sample_spacing=0.3,max_slope_degrees=34,max_step_height=0.22);

subject("walkway",[5.8,14,0.28],[0,-4,-0.28]);
subject("campus",[4.0,6.0,3.6],[0.79,-1.0,0]);
subject("old-eaves",[4.0,7.0,3.7],[0.79,-7.5,0]);
subject("basin",[0.76,0.76,0.34],[-1.42,-5.5,0]);
subject("desk",[1.95,1.65,1.05],[1.20,-8,0]);
