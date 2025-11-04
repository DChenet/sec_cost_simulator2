import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class SatelliteOrbitSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Satellite Orbit Simulation")

        # Create figure with world map
        self.fig = Figure(figsize=(12, 6))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim([-180, 180])
        self.ax.set_ylim([-90, 90])
        self.ax.set_xlabel('Longitude (degrees)')
        self.ax.set_ylabel('Latitude (degrees)')
        self.ax.set_title('Satellite Ground Track on Planisphere')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')

        # Draw simple world map outline
        self.draw_world_map()

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Control frame
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Orbit type selection
        tk.Label(control_frame, text="Orbit Type:").pack(side=tk.LEFT, padx=5)

        self.orbit_type = tk.StringVar(value="polar")
        tk.Radiobutton(control_frame, text="Polar Orbit (Sinusoid)",
                       variable=self.orbit_type, value="polar",
                       command=self.reset_simulation).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="Equatorial Orbit (Straight Line)",
                       variable=self.orbit_type, value="equatorial",
                       command=self.reset_simulation).pack(side=tk.LEFT)

        # Speed control
        tk.Label(control_frame, text="Speed:").pack(side=tk.LEFT, padx=(20, 5))
        self.speed_slider = tk.Scale(control_frame, from_=0.5, to=5.0,
                                     resolution=0.1, orient=tk.HORIZONTAL,
                                     length=200)
        self.speed_slider.set(2.0)
        self.speed_slider.pack(side=tk.LEFT)

        # Reset button
        tk.Button(control_frame, text="Reset",
                  command=self.reset_simulation).pack(side=tk.LEFT, padx=10)

        # Simulation parameters
        self.time = 0
        self.trail_lon = []
        self.trail_lat = []

        # Plot elements
        self.trail_line, = self.ax.plot([], [], 'r-', linewidth=1.5, alpha=0.6, label='Ground Track')
        self.satellite, = self.ax.plot([], [], 'ro', markersize=10, label='Satellite')
        self.ax.legend(loc='upper right')

        # Start animation
        self.animate()

    def draw_world_map(self):
        """Draw simplified continents outline"""
        # Draw equator
        self.ax.axhline(y=0, color='blue', linestyle='--', alpha=0.3, linewidth=1)

        # Draw prime meridian
        self.ax.axvline(x=0, color='blue', linestyle='--', alpha=0.3, linewidth=1)

        # Draw tropics
        self.ax.axhline(y=23.5, color='orange', linestyle=':', alpha=0.2)
        self.ax.axhline(y=-23.5, color='orange', linestyle=':', alpha=0.2)

        # Draw polar circles
        self.ax.axhline(y=66.5, color='cyan', linestyle=':', alpha=0.2)
        self.ax.axhline(y=-66.5, color='cyan', linestyle=':', alpha=0.2)

        # Simple continent outlines (approximate rectangles)
        # Africa
        africa = plt.Rectangle((-20, -35), 60, 70, fill=False, edgecolor='green', linewidth=1.5)
        self.ax.add_patch(africa)

        # South America
        s_america = plt.Rectangle((-80, -55), 40, 80, fill=False, edgecolor='green', linewidth=1.5)
        self.ax.add_patch(s_america)

        # North America
        n_america = plt.Rectangle((-170, 15), 100, 60, fill=False, edgecolor='green', linewidth=1.5)
        self.ax.add_patch(n_america)

        # Eurasia
        eurasia = plt.Rectangle((-10, 35), 150, 40, fill=False, edgecolor='green', linewidth=1.5)
        self.ax.add_patch(eurasia)

        # Australia
        australia = plt.Rectangle((110, -45), 45, 35, fill=False, edgecolor='green', linewidth=1.5)
        self.ax.add_patch(australia)

    def calculate_position(self):
        """Calculate satellite position based on orbit type"""
        speed = self.speed_slider.get()

        if self.orbit_type.get() == "polar":
            # Polar orbit: sinusoidal pattern
            # Longitude increases linearly (Earth rotates beneath satellite)
            lon = (self.time * speed * 5) % 360 - 180  # Wrap around

            # Latitude oscillates between -90 and +90 (polar orbit)
            lat = 80 * np.sin(self.time * speed * 0.05)  # Max latitude ~80°

        else:  # equatorial
            # Equatorial orbit: straight line at latitude 0
            lon = (self.time * speed * 5) % 360 - 180  # Wrap around
            lat = 0  # Always at equator

        return lon, lat

    def reset_simulation(self):
        """Reset the simulation"""
        self.time = 0
        self.trail_lon = []
        self.trail_lat = []
        self.trail_line.set_data([], [])
        self.satellite.set_data([], [])
        self.canvas.draw()

    def animate(self):
        # Update time
        self.time += 1

        # Calculate satellite position
        lon, lat = self.calculate_position()

        # Add to trail
        self.trail_lon.append(lon)
        self.trail_lat.append(lat)

        # Keep trail length manageable (last 500 points)
        if len(self.trail_lon) > 500:
            self.trail_lon.pop(0)
            self.trail_lat.pop(0)

        # Handle longitude wrapping for continuous trail drawing
        trail_lon_wrapped = []
        trail_lat_wrapped = []

        for i in range(len(self.trail_lon)):
            if i > 0:
                # Check for wrap-around
                if abs(self.trail_lon[i] - self.trail_lon[i - 1]) > 180:
                    # Insert NaN to break the line
                    trail_lon_wrapped.append(np.nan)
                    trail_lat_wrapped.append(np.nan)

            trail_lon_wrapped.append(self.trail_lon[i])
            trail_lat_wrapped.append(self.trail_lat[i])

        # Update plots
        self.trail_line.set_data(trail_lon_wrapped, trail_lat_wrapped)
        self.satellite.set_data([lon], [lat])

        # Redraw
        self.canvas.draw()

        # Schedule next frame
        self.root.after(50, self.animate)  # ~20 FPS


# Import matplotlib for Rectangle
import matplotlib.pyplot as plt

# Create Tkinter window
root = tk.Tk()
app = SatelliteOrbitSimulation(root)
root.mainloop()