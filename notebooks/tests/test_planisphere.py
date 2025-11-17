import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageTk
import requests
from io import BytesIO


class EarthPlanisphere:
    def __init__(self, root):
        self.root = root
        self.root.title("Earth Planisphere")
        self.root.geometry("900x700")

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Coordinates", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        # Latitude input
        ttk.Label(input_frame, text="Latitude:").grid(row=0, column=0, padx=5)
        self.lat_entry = ttk.Entry(input_frame, width=15)
        self.lat_entry.grid(row=0, column=1, padx=5)
        ttk.Label(input_frame, text="(-90 to 90)").grid(row=0, column=2, padx=5)

        # Longitude input
        ttk.Label(input_frame, text="Longitude:").grid(row=1, column=0, padx=5)
        self.lon_entry = ttk.Entry(input_frame, width=15)
        self.lon_entry.grid(row=1, column=1, padx=5)
        ttk.Label(input_frame, text="(-180 to 180)").grid(row=1, column=2, padx=5)

        # Mark button
        mark_button = ttk.Button(input_frame, text="Mark Location", command=self.mark_location)
        mark_button.grid(row=2, column=0, columnspan=3, pady=10)

        # Canvas for the map
        self.canvas = tk.Canvas(main_frame, width=800, height=500, bg="white")
        self.canvas.grid(row=1, column=0, columnspan=2, pady=10)

        # Load and display the planisphere
        self.load_planisphere()

        # List to store markers
        self.markers = []

    def load_planisphere(self):
        """Load a simple world map planisphere"""
        try:
            # Download a simple equirectangular projection world map
            url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Equirectangular_projection_SW.jpg/1280px-Equirectangular_projection_SW.jpg"
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))

            # Resize to fit canvas
            img = img.resize((800, 500), Image.Resampling.LANCZOS)
            self.map_image = img.copy()

            # Convert to PhotoImage and display
            self.photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load map: {e}")
            # Create a simple grid as fallback
            self.create_simple_grid()

    def create_simple_grid(self):
        """Create a simple grid if map download fails"""
        # Draw grid lines
        for i in range(0, 801, 100):
            self.canvas.create_line(i, 0, i, 500, fill="lightgray")
        for i in range(0, 501, 50):
            self.canvas.create_line(0, i, 800, i, fill="lightgray")

        # Add equator and prime meridian
        self.canvas.create_line(0, 250, 800, 250, fill="blue", width=2)
        self.canvas.create_line(400, 0, 400, 500, fill="blue", width=2)

        # Labels
        self.canvas.create_text(400, 10, text="Prime Meridian", fill="blue")
        self.canvas.create_text(10, 250, text="Equator", fill="blue", anchor=tk.W)

    def lat_lon_to_pixel(self, lat, lon):
        """Convert latitude/longitude to pixel coordinates on the canvas"""
        # Canvas dimensions
        width = 800
        height = 500

        # Convert longitude (-180 to 180) to x (0 to 800)
        x = ((lon + 180) / 360) * width

        # Convert latitude (90 to -90) to y (0 to 500)
        y = ((90 - lat) / 180) * height

        return x, y

    def mark_location(self):
        """Mark a location on the planisphere based on user input"""
        try:
            lat = float(self.lat_entry.get())
            lon = float(self.lon_entry.get())

            # Validate coordinates
            if not (-90 <= lat <= 90):
                messagebox.showerror("Error", "Latitude must be between -90 and 90")
                return
            if not (-180 <= lon <= 180):
                messagebox.showerror("Error", "Longitude must be between -180 and 180")
                return

            # Convert to pixel coordinates
            x, y = self.lat_lon_to_pixel(lat, lon)

            # Reload the base map to clear previous drawings
            if hasattr(self, 'map_image'):
                img = self.map_image.copy()
                draw = ImageDraw.Draw(img)

                # Draw all markers
                for marker_lat, marker_lon in self.markers:
                    mx, my = self.lat_lon_to_pixel(marker_lat, marker_lon)
                    self.draw_marker(draw, mx, my)

                # Draw new marker
                self.draw_marker(draw, x, y)

                # Update canvas
                self.photo = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            else:
                # Fallback if using simple grid
                self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="red", outline="darkred", width=2)
                self.canvas.create_text(x, y - 15, text=f"({lat:.2f}, {lon:.2f})", fill="red")

            # Store marker
            self.markers.append((lat, lon))

            messagebox.showinfo("Success", f"Location marked at:\nLatitude: {lat}°\nLongitude: {lon}°")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric coordinates")

    def draw_marker(self, draw, x, y):
        """Draw a marker on the image"""
        # Draw a red pin-like marker
        radius = 8
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill="red", outline="darkred", width=2)
        draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill="white")


def main():
    root = tk.Tk()
    app = EarthPlanisphere(root)
    root.mainloop()


if __name__ == "__main__":
    main()