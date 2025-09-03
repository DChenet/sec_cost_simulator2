import matplotlib.pyplot as plt
import matplotlib
from typing import Tuple, Optional


class DualPlot:
    def __init__(self, left_plotter, right_plotter, figsize=(15, 6),
                 main_title=None, spacing=0.3):
        """
        Create side-by-side plots from two plotter objects.

        Args:
            left_plotter: Any plotter object with curves attribute (MultiCurvePlotter or CurvePlotter)
            right_plotter: Any plotter object with curves attribute
            figsize (tuple): Figure size (width, height) in inches
            main_title (str): Overall title for the combined figure
            spacing (float): Horizontal spacing between subplots
        """
        self.left_plotter = left_plotter
        self.right_plotter = right_plotter
        self.figsize = figsize
        self.main_title = main_title
        self.spacing = spacing

    def plot(self, show=True):
        """
        Create and display the side-by-side plots.

        Args:
            show (bool): Whether to display the plot

        Returns:
            tuple: (fig, (ax1, ax2)) matplotlib figure and axis objects
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)

        # Adjust spacing between subplots
        plt.subplots_adjust(wspace=self.spacing)

        # Plot left subplot
        self._plot_curves(ax1, self.left_plotter)

        # Plot right subplot
        self._plot_curves(ax2, self.right_plotter)

        # Add main title if provided
        if self.main_title:
            fig.suptitle(self.main_title, fontsize=16, fontweight='bold', y=0.98)

        plt.tight_layout()

        if show:
            plt.show()

        return fig, (ax1, ax2)

    def _plot_curves(self, ax, plotter):
        """
        Plot all curves from a plotter object onto the given axis.

        Args:
            ax: Matplotlib axis object
            plotter: Plotter object with curves attribute
        """
        if not hasattr(plotter, 'curves') or not plotter.curves:
            raise ValueError("Plotter must have a 'curves' attribute with curve data")

        # Plot each curve
        for curve in plotter.curves:
            sorted_df = curve['df'].sort_values(by=curve['x_col'])

            plot_kwargs = {
                'label': curve['label'],
                'color': curve['color'],
                'linewidth': curve['line_width'],
                'linestyle': curve['line_style']
            }

            # Add marker if specified
            if curve.get('marker'):
                plot_kwargs['marker'] = curve['marker']

            ax.plot(sorted_df[curve['x_col']], sorted_df[curve['y_col']], **plot_kwargs)

        # Set labels and styling
        ax.set_title(plotter.title, fontsize=14, fontweight='bold')
        ax.set_xlabel(plotter.xlabel, fontsize=12)
        ax.set_ylabel(plotter.ylabel, fontsize=12)

        # Add grid if enabled in the plotter
        if hasattr(plotter, 'grid') and plotter.grid:
            ax.grid(True, alpha=0.3)

        # Add legend if there are multiple curves or legend is enabled
        if len(plotter.curves) > 1 or (hasattr(plotter, 'legend') and plotter.legend):
            ax.legend()

    def export_png(self, filename, dpi=300, bbox_inches='tight', transparent=False):
        """
        Export the dual plot as a PNG file.

        Args:
            filename (str): Output filename (with or without .png extension)
            dpi (int): Resolution in dots per inch
            bbox_inches (str): Bbox in inches. 'tight' fits the plot tightly
            transparent (bool): Whether to save with transparent background
        """
        # Ensure .png extension
        filename = str(filename)
        if not filename.endswith('.png'):
            filename += '.png'

        fig, axes = self.plot(show=False)

        fig.savefig(filename,
                    dpi=dpi,
                    bbox_inches=bbox_inches,
                    transparent=transparent,
                    format='png')

        plt.close(fig)
        print(f"Dual plot saved as PNG: {filename}")

    def export_latex(self, filename, backend='pgf', usetex=True, preamble=None):
        """
        Export the dual plot as LaTeX figure using matplotlib's native backends.

        Args:
            filename (str): Output filename (extension determines format)
            backend (str): 'pgf' for PGF/TikZ or 'pdf' for PDF
            usetex (bool): Whether to use LaTeX for text rendering
            preamble (list): Custom LaTeX preamble commands
        """
        # Import here to avoid issues if not available
        try:
            from matplotlib.backends.backend_pgf import PdfPages
            HAS_PGF = True
        except ImportError:
            HAS_PGF = False

        if backend.lower() == 'pgf' and not HAS_PGF:
            raise ImportError("PGF backend not available. Install matplotlib with PGF support.")

        # Set up LaTeX backend
        original_backend = matplotlib.get_backend()

        if backend.lower() == 'pgf':
            matplotlib.use('pgf')

            # Configure PGF backend
            default_preamble = [
                r"\usepackage[utf8x]{inputenc}",
                r"\usepackage[T1]{fontenc}",
                r"\usepackage{amsmath}",
            ]
            preamble_str = '\n'.join(preamble or default_preamble)

            pgf_config = {
                "pgf.texsystem": "pdflatex",
                "pgf.rcfonts": False,
                "pgf.preamble": preamble_str
            }

            if usetex:
                pgf_config.update({
                    "text.usetex": True,
                    "font.family": "serif",
                    "font.serif": [],
                    "font.sans-serif": [],
                    "font.monospace": [],
                })

            matplotlib.rcParams.update(pgf_config)

            # Ensure correct extension
            if not filename.endswith(('.pgf', '.tex')):
                filename += '.pgf'

        else:
            # For other backends
            if usetex:
                matplotlib.rcParams.update({
                    "text.usetex": True,
                    "font.family": "serif",
                })

        try:
            # Create the plot
            fig, axes = self.plot(show=False)

            # Save the figure
            fig.savefig(filename, bbox_inches='tight')
            plt.close(fig)

            print(f"Dual plot saved as LaTeX figure ({backend}): {filename}")

        finally:
            # Restore original backend
            matplotlib.use(original_backend)
            # Reset rcParams
            matplotlib.rcParams.update(matplotlib.rcParamsDefault)

    def set_style(self, figsize=None, main_title=None, spacing=None):
        """
        Update styling options for the dual plot.

        Args:
            figsize (tuple): Figure size (width, height) in inches
            main_title (str): Overall title for the combined figure
            spacing (float): Horizontal spacing between subplots
        """
        if figsize is not None:
            self.figsize = figsize
        if main_title is not None:
            self.main_title = main_title
        if spacing is not None:
            self.spacing = spacing


# Example usage
# if __name__ == "__main__":
#     import numpy as np
#     import pandas as pd
#
#     # Import your plotter classes (adjust path as needed)
#     # from plot.simple_curve import MultiCurvePlotter
#
#     # Create sample data for demonstration
#     x = np.linspace(0, 2 * np.pi, 100)
#
#     # Create first plotter (time costs)
#     time_plotter = MultiCurvePlotter(
#         title="Time Cost Analysis",
#         xlabel="ISL Speed (Mb/s)",
#         ylabel="Time (s)"
#     )
#
#     # Add some sample curves
#     for i, phi in enumerate([0.1, 0.5, 0.9]):
#         y = np.sin(x + i) * (1 + phi)
#         time_plotter.add_curve_from_arrays(x, y, label=f"φ = {phi}")
#
#     # Create second plotter (energy costs)
#     energy_plotter = MultiCurvePlotter(
#         title="Energy Cost Analysis",
#         xlabel="ISL Speed (Mb/s)",
#         ylabel="Energy (J)"
#     )
#
#     # Add some sample curves
#     for i, phi in enumerate([0.1, 0.5, 0.9]):
#         y = np.cos(x + i) * (2 + phi)
#         energy_plotter.add_curve_from_arrays(x, y, label=f"φ = {phi}")
#
#     # Create dual plot
#     dual_plot = DualPlot(
#         left_plotter=time_plotter,
#         right_plotter=energy_plotter,
#         figsize=(15, 6),
#         main_title="Performance Analysis: Time vs Energy Costs"
#     )
#
#     # Display the dual plot
#     dual_plot.plot()
#
#     # Export options
#     # dual_plot.export_png("dual_analysis.png", dpi=300)
#     # dual_plot.export_latex("dual_analysis.pgf")