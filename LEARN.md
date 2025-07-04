# Boids

## What are Boids?

Boids ("bird-oid objects") is an artificial life algorithm developed by Craig Reynolds in 1986, which simulates the flocking behavior of birds. The "boids" follow simple rules, but together they produce complex, lifelike group movement - such as flocks of birds, schools of fish, or herds of animals.

## Core concepts

Each boid in the simulation moves according to three fundamental rules:

1. **Separation:** Avoid crowding neighbors (steer to avoid collisions with local flockmates).
2. **Alignment:** Align velocity with nearby flockmates (steer towards the average heading of local flockmates).
3. **Cohesion:** Move toward the average position of local flockmates.

In this implementation, several additional factors can influence boid movement, such as boundaries, wind, locality, and goals.

---

## Configuration parameters

You can tune the simulation by setting the following parameters in the settings panel:

- **Boundary**  
  Whether boids are confined within a limited space. If enabled, boids will turn when they approach the simulation area's edge, and the boundary size can be controlled by updating the top-left and bottom-right edge positions.

- **Count**  
  The number of boids in the simulation.

- **Simulation speed**  
  Controls how fast the simulation updates (time step).

- **Max speed**  
  Limits how fast any boid can move.

- **Cohesion**  
  Strength of the tendency for boids to move toward the average position of neighbors.

- **Alignment**  
  Strength of the tendency for boids to align their direction with neighbors.

- **Separation distance**  
  The minimum distance boids try to maintain from each other.

- **Separation strength**  
  How strongly boids steer to avoid crowding.

- **Turn factor**  
  How sharply boids can turn when adjusting their direction.

- **Locality radius**  
  The distance within which other boids are considered "neighbors" for alignment and cohesion.

- **Wind**  
  If enabled, applies a global wind effect to all boids.

- **Wind direction**  
  The direction of the wind.

- **Goal**  
  An optional target location that boids can be attracted toward, and controls whether and for how long boids pursue the goal.

- **Colorization by velocity**  
  Boid color changes depending on their speed, which can help visualize velocity differences in the flock.

---

## How the algorithm works

On each frame (simulation tick), every boid:

1. Looks at nearby boids (within the locality radius).
2. Computes separation, alignment, and cohesion vectors.
3. Applies wind (if enabled) and goal-seeking (if enabled).
4. Combines all steering influences, limited by turn factor and max speed.
5. Updates its position and velocity.
6. If the boundary is enabled, it turns away from edges.

Through repeated application of these simple rules, complex flocking emerges.

---

## Tips for experimentation

- Increase **separation strength** to make the flock more "loose."
- Increase **cohesion** for a tighter group.
- Adjust **alignment** to make boids travel in similar directions.
- Enable **wind** or **goal chasing** to see environmental influences.
- Play with **colorization by velocity** to visualize activity within the flock.

---

## Further reading

- [Craig Reynolds' Boids](https://www.red3d.com/cwr/boids/)
- [Wikipedia: Boids](https://en.wikipedia.org/wiki/Boids)
- [Nature of Code - Flocking](https://natureofcode.com/book/chapter-6-autonomous-agents/#chapter06_section4)
