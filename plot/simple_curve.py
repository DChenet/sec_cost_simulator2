import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Optional backend import with error handling
try:
    from matplotlib.backends.backend_pgf import PdfPages

    HAS_PGF = True
except ImportError:
    HAS_PGF = False


class CurvePlotter:
    def __init__(self, df, x_col, y_col, title="Curve Plot", xlabel=None, ylabel=None):
        """
        Initialize the CurvePlotter with a DataFrame and column specifications.

        Args:
            df (pd.DataFrame): DataFrame containing the data
            x_col (str): Name of the x-axis column
            y_col (str): Name of the y-axis column
            title (str): Plot title
            xlabel (str): X-axis label (defaults to x_col name)
            ylabel (str): Y-axis label (defaults to y_col name)
        """
        self.df = df.copy()
        self.x_col = x_col
        self.y_col = y_col
        self.title = title
        self.xlabel = xlabel or x_col
        self.ylabel = ylabel or y_col

        # Plot styling options
        self.figsize = (10, 6)
        self.line_style = '-'
        self.line_width = 2
        self.color = 'blue'
        self.grid = True
        self.dpi = 300

    def set_style(self, figsize=(10, 6), line_style='-', line_width=2, color='blue', grid=True):
        """Set plot styling options."""
        self.figsize = figsize
        self.line_style = line_style
        self.line_width = line_width
        self.color = color
        self.grid = grid

    def plot(self, show=True):
        """
        Create and display the plot.

        Args:
            show (bool): Whether to display the plot

        Returns:
            tuple: (fig, ax) matplotlib figure and axis objects
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Sort data by x values for proper curve plotting
        sorted_df = self.df.sort_values(by=self.x_col)

        ax.plot(sorted_df[self.x_col], sorted_df[self.y_col],
                linestyle=self.line_style, linewidth=self.line_width, color=self.color)

        ax.set_title(self.title, fontsize=14, fontweight='bold')
        ax.set_xlabel(self.xlabel, fontsize=12)
        ax.set_ylabel(self.ylabel, fontsize=12)

        if self.grid:
            ax.grid(True, alpha=0.3)

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

    def export_latex(self, filename, backend='pgf', usetex=True,
                     preamble=None):
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
        """Return basic statistics about the data."""
        return {
            'data_points': len(self.df),
            'x_range': (self.df[self.x_col].min(), self.df[self.x_col].max()),
            'y_range': (self.df[self.y_col].min(), self.df[self.y_col].max()),
            'x_mean': self.df[self.x_col].mean(),
            'y_mean': self.df[self.y_col].mean()
        }


# Example usage:
# if __name__ == "__main__":
#     # Create sample data
#     x = np.linspace(0, 4 * np.pi, 100)
#     y = np.sin(x) * np.exp(-x / 8)
#     df = pd.DataFrame({'x': x, 'y': y})
#
#     # Create plotter instance
#     plotter = CurvePlotter(df, 'x', 'y',
#                            title="Damped Sine Wave",
#                            xlabel="Time (s)",
#                            ylabel="Amplitude")
#
#     # Customize styling
#     plotter.set_style(figsize=(12, 7), color='red', line_width=2.5)
#
#     # Display plot
#     plotter.plot()
#
#     # Export as PNG
#     plotter.export_png("curve_plot.png", dpi=300)
#
#     # Export as LaTeX figure using matplotlib's PGF backend
#     plotter.export_latex("curve_plot.pgf", backend='pgf')
#
#     # Alternative: Export as PDF with LaTeX text rendering
#     # plotter.export_latex("curve_plot.pdf", backend='pdf', usetex=True)
#
#     # Print statistics
#     print("\nData Statistics:")
#     stats = plotter.get_stats()
#     for key, value in stats.items():
#         print(f"{key}: {value}")