# string-simulation
This is a string simulation using multiple springs. It uses Hooke's law to 
simulate the springs. I originally tried to use pendulums (see commit history)
but learned that springs are better and how to simulate them from 
[this video by Let's Code Physics](https://www.youtube.com/watch?v=0WaDxYuD9S8).
For the obstruction (circle that can push spring), I just calculated the normal
force using vector projection. To apply the forces, I used Euler integration. I
tried using the Velocity Verlet algorithm but that wasn't working, so I settled
for Euler's methods. To keep the movement consistent (even if inaccurate) I 
followed
[Glenn Fiedler's well-known article on timestepping](https://www.gafferongames.com/post/fix_your_timestep/).

## Usage
To change how the string behaves, edit the constants in the main Game class. At
the top of the class, you can edit the timestep (`_TIMESTEP`). Making it 
smaller makes the physics more accurate. In __init__, you can edit the physics 
constants, such as gravity (`self._GRAVITY`), the spring constant (`self._K`), 
the amount of springs (`self._AMOUNT`), the length of each spring 
(`self._LENGTH`), the mass of each bob (`self._MASS`), and the radius of the 
obstruction (`self._OBSTRUCTION_RADIUS`).

