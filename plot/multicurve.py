import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Union, List, Dict, Tuple, Optional

# Optional backend import with error handling
try:
    from matplotlib.backends.backend_pgf import PdfPages

    HAS_PGF = True
except ImportError:
    HAS_PGF = False


class MultiCurvePlotter:
    def __init__(self, title="Multi-Curve Plot", xlabel="X", ylabel="Y"):
        """
        Initialize the MultiCurvePlotter for plotting multiple curves.

        Args:
            title (str): Plot title
            xlabel (str): X-axis label
            ylabel (str): Y-axis label
        """
        self.curves = []  # List to store curve data
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

        # Plot styling options
        self.figsize = (10, 6)
        self.grid = True
        self.dpi = 300
        self.legend = True

        # Default colors for multiple curves
        self.default_colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']

    def add_curve(self, df: pd.DataFrame, x_col: str, y_col: str,
                  label: str = None, color: str = None, line_style: str = '-',
                  line_width: float = 2, marker: str = None):
        """
        Add a curve to the plot.

        Args:
            df (pd.DataFrame): DataFrame containing the data
            x_col (str): Name of the x-axis column
            y_col (str): Name of the y-axis column
            label (str): Legend label for this curve
            color (str): Line color (auto-assigned if None)
            line_style (str): Line style ('-', '--', '-.', ':')
            line_width (float): Line width
            marker (str): Marker style ('o', 's', '^', etc.)
        """
        curve_data = {
            'df': df.copy(),
            'x_col': x_col,
            'y_col': y_col,
            'label': label or f"Curve {len(self.curves) + 1}",
            'color': color or self.default_colors[len(self.curves) % len(self.default_colors)],
            'line_style': line_style,
            'line_width': line_width,
            'marker': marker
        }
        self.curves.append(curve_data)

    def add_curve_from_arrays(self, x_data: Union[List, np.ndarray], y_data: Union[List, np.ndarray],
                              label: str = None, color: str = None, line_style: str = '-',
                              line_width: float = 2, marker: str = None):
        """
        Add a curve from x and y arrays/lists.

        Args:
            x_data: X-axis data
            y_data: Y-axis data
            label (str): Legend label for this curve
            color (str): Line color (auto-assigned if None)
            line_style (str): Line style ('-', '--', '-.', ':')
            line_width (float): Line width
            marker (str): Marker style ('o', 's', '^', etc.)
        """
        df = pd.DataFrame({'x': x_data, 'y': y_data})
        self.add_curve(df, 'x', 'y', label, color, line_style, line_width, marker)

    def clear_curves(self):
        """Remove all curves from the plot."""
        self.curves = []

    def set_style(self, figsize=(10, 6), grid=True, legend=True):
        """Set plot styling options."""
        self.figsize = figsize
        self.grid = grid
        self.legend = legend

    def set_labels(self, title=None, xlabel=None, ylabel=None):
        """Update plot labels."""
        if title is not None:
            self.title = title
        if xlabel is not None:
            self.xlabel = xlabel
        if ylabel is not None:
            self.ylabel = ylabel

    def plot(self, show=True):
        """
        Create and display the plot with all curves.

        Args:
            show (bool): Whether to display the plot

        Returns:
            tuple: (fig, ax) matplotlib figure and axis objects
        """
        if not self.curves:
            raise ValueError("No curves added. Use add_curve() or add_curve_from_arrays() first.")

        fig, ax = plt.subplots(figsize=self.figsize)

        # Plot each curve
        for curve in self.curves:
            # Sort data by x values for proper curve plotting
            sorted_df = curve['df'].sort_values(by=curve['x_col'])

            ax.plot(sorted_df[curve['x_col']], sorted_df[curve['y_col']],
                    linestyle=curve['line_style'],
                    linewidth=curve['line_width'],
                    color=curve['color'],
                    marker=curve['marker'],
                    label=curve['label'])

        ax.set_title(self.title, fontsize=14, fontweight='bold')
        ax.set_xlabel(self.xlabel, fontsize=12)
        ax.set_ylabel(self.ylabel, fontsize=12)

        if self.grid:
            ax.grid(True, alpha=0.3)

        if self.legend and len(self.curves) > 1:
            ax.legend()

        plt.tight_layout()

        if show:
            plt.show()

        return fig, ax

    def export_png(self, filename, dpi=None, bbox_inches='tight', transparent=False):
        """
        Export the plot as a PNG file.

        Args:
            filename (str): Output filename (with or without .png extension)
            dpi (int): Resolution in dots per inch (defaults to class dpi setting)
            bbox_inches (str): Bbox in inches. 'tight' fits the plot tightly
            transparent (bool): Whether to save with transparent background
        """
        # Ensure .png extension
        filename = str(filename)
        if not filename.endswith('.png'):
            filename += '.png'

        fig, ax = self.plot(show=False)

        fig.savefig(filename,
                    dpi=dpi or self.dpi,
                    bbox_inches=bbox_inches,
                    transparent=transparent,
                    format='png')

        plt.close(fig)
        print(f"Plot saved as PNG: {filename}")

    def export_latex(self, filename, backend='pgf', usetex=True, preamble=None):
        """
        Export the plot as LaTeX figure using matplotlib's native backends.

        Args:
            filename (str): Output filename (extension determines format)
            backend (str): 'pgf' for PGF/TikZ or 'ps' for PSTricks
            usetex (bool): Whether to use LaTeX for text rendering
            preamble (list): Custom LaTeX preamble commands
        """
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
            # For other backends (PDF, EPS with LaTeX)
            if usetex:
                matplotlib.rcParams.update({
                    "text.usetex": True,
                    "font.family": "serif",
                })

        try:
            # Create the plot
            fig, ax = self.plot(show=False)

            # Save the figure (just the plot, not a full document)
            fig.savefig(filename, bbox_inches='tight')
            plt.close(fig)

            print(f"Plot saved as LaTeX figure ({backend}): {filename}")

        finally:
            # Restore original backend
            matplotlib.use(original_backend)
            # Reset rcParams
            matplotlib.rcParams.update(matplotlib.rcParamsDefault)

    def get_stats(self):
        """Return basic statistics about all curves."""
        if not self.curves:
            return {"message": "No curves added"}

        stats = {}
        all_x_values = []
        all_y_values = []

        for i, curve in enumerate(self.curves):
            df = curve['df']
            x_col = curve['x_col']
            y_col = curve['y_col']
            label = curve['label']

            curve_stats = {
                'data_points': len(df),
                'x_range': (df[x_col].min(), df[x_col].max()),
                'y_range': (df[y_col].min(), df[y_col].max()),
                'x_mean': df[x_col].mean(),
                'y_mean': df[y_col].mean()
            }
            stats[f"Curve_{i + 1}_{label}"] = curve_stats

            all_x_values.extend(df[x_col].tolist())
            all_y_values.extend(df[y_col].tolist())

        # Overall statistics
        stats['Overall'] = {
            'total_curves': len(self.curves),
            'total_data_points': sum(len(curve['df']) for curve in self.curves),
            'overall_x_range': (min(all_x_values), max(all_x_values)),
            'overall_y_range': (min(all_y_values), max(all_y_values)),
        }

        return stats


# Backward compatibility: Keep the original single-curve class
class CurvePlotter(MultiCurvePlotter):
    def __init__(self, df, x_col, y_col, title="Curve Plot", xlabel=None, ylabel=None):
        """
        Initialize the CurvePlotter with a DataFrame and column specifications.
        This is a single-curve version that maintains backward compatibility.

        Args:
            df (pd.DataFrame): DataFrame containing the data
            x_col (str): Name of the x-axis column
            y_col (str): Name of the y-axis column
            title (str): Plot title
            xlabel (str): X-axis label (defaults to x_col name)
            ylabel (str): Y-axis label (defaults to y_col name)
        """
        super().__init__(title=title,
                         xlabel=xlabel or x_col,
                         ylabel=ylabel or y_col)

        # Add the single curve
        self.add_curve(df, x_col, y_col, label="Data")

        # Single curve styling (for backward compatibility)
        self.line_style = '-'
        self.line_width = 2
        self.color = 'blue'
        self.legend = False  # Don't show legend for single curve

    def set_style(self, figsize=(10, 6), line_style='-', line_width=2, color='blue', grid=True):
        """Set plot styling options for single curve."""
        super().set_style(figsize=figsize, grid=grid, legend=False)

        # Update the single curve's style
        if self.curves:
            self.curves[0]['line_style'] = line_style
            self.curves[0]['line_width'] = line_width
            self.curves[0]['color'] = color

    def get_stats(self):
        """Return basic statistics about the single curve data."""
        if not self.curves:
            return {"message": "No data"}

        curve = self.curves[0]
        df = curve['df']
        x_col = curve['x_col']
        y_col = curve['y_col']

        return {
            'data_points': len(df),
            'x_range': (df[x_col].min(), df[x_col].max()),
            'y_range': (df[y_col].min(), df[y_col].max()),
            'x_mean': df[x_col].mean(),
            'y_mean': df[y_col].mean()
        }


# Example usage:
# if __name__ == "__main__":
#     # Example 1: Single curve (backward compatible)
#     x = np.linspace(0, 4 * np.pi, 100)
#     y = np.sin(x) * np.exp(-x / 8)
#     df = pd.DataFrame({'x': x, 'y': y})
#
#     single_plotter = CurvePlotter(df, 'x', 'y',
#                                   title="Damped Sine Wave",
#                                   xlabel="Time (s)",
#                                   ylabel="Amplitude")
#     single_plotter.set_style(figsize=(10, 6), color='red', line_width=2.5)
#     single_plotter.plot()
#
#     # Example 2: Multiple curves
#     multi_plotter = MultiCurvePlotter(title="Multiple Functions Comparison",
#                                       xlabel="X", ylabel="Y")
#
#     # Add multiple curves
#     x = np.linspace(0, 2 * np.pi, 100)
#
#     # Sine wave
#     y1 = np.sin(x)
#     multi_plotter.add_curve_from_arrays(x, y1, label="sin(x)", color='blue', line_width=2)
#
#     # Cosine wave
#     y2 = np.cos(x)
#     multi_plotter.add_curve_from_arrays(x, y2, label="cos(x)", color='red', line_style='--', line_width=2)
#
#     # Tangent wave (limited range)
#     x_tan = np.linspace(0, np.pi / 2 - 0.1, 50)
#     y3 = np.tan(x_tan)
#     multi_plotter.add_curve_from_arrays(x_tan, y3, label="tan(x)", color='green', marker='o', line_width=1.5)
#
#     multi_plotter.set_style(figsize=(12, 8), grid=True, legend=True)
#     multi_plotter.plot()
#
#     # Export examples
#     # multi_plotter.export_png("multi_curve_plot.png", dpi=300)
#     # multi_plotter.export_latex("multi_curve_plot.pgf", backend='pgf')
#
#     # Print statistics
#     print("\nMulti-curve Statistics:")
#     stats = multi_plotter.get_stats()
#     for key, value in stats.items():
#         print(f"{key}: {value}")