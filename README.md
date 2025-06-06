# Boids

A Python implementation of the boids ("bird-oid objects") flocking algorithm, simulating the collective motion of animals like birds or fish.

## Features
* Real-time simulation of boids movement.
* Configurable parameters (number of boids, visual range, speed, etc.).
* Uses [Pygame](https://www.pygame.org/news) for visualization and [pyimgui](https://github.com/pyimgui/pyimgui) for GUI.

## Preview
<img src="public/preview_color.gif" width="auto" height="700%" style="object-fit: contain; max-height: 700px;" />

## Prerequisites

* **Python:** 3.8+.
* Corresponding [python3-devel](https://pkgs.org/download/python3-devel) package for your distribution.

## Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Eoic/Boids
    cd Boids
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Linux/macOS
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**

    * **For running the simulation:**
        ```bash
        pip install .
        ```

    * **For development (including testing, linting, etc.):**
        ```bash
        pip install -e '.[dev]'
        ```
        * The `-e` flag installs the project in "editable" mode. Changes you make to the source code will be immediately effective without needing to reinstall.
        * `.[dev]` installs the main package dependencies and the extra dependencies specified under the `[dev]` section in `pyproject.toml`. These include tools for testing, linting, formatting, etc.

## Usage

Once installed, you can run the Boids simulation directly from your command line:

```bash
boids
```

## References
1. [Boids Pseudocode](http://www.kfish.org/boids/pseudocode.html).
2. [Boids (Flocks, Herds, and Schools: a Distributed Behavioral Model)](https://www.red3d.com/cwr/boids/).
