from plot.dual_plot import DualPlot


class LogDualPlot(DualPlot):
    def _plot_curves(self, ax, plotter):
        """Override to add logarithmic scale and ratio-specific formatting."""
        super()._plot_curves(ax, plotter)

        # Set logarithmic scale for x-axis
        ax.set_xscale('log')

        # Add vertical line at ratio = 1 for reference
        ax.axvline(x=1, color='black', linestyle='--', alpha=0.5, linewidth=1)

        # Customize x-axis ticks for ratio interpretation
        ax.set_xticks([0.01, 0.1, 1, 10, 100])
        ax.set_xticklabels(['0.01\n(GL >> ISL)', '0.1', '1\n(Equal)', '10', '100\n(ISL >> GL)'])

        # Enhance grid for log scale
        ax.grid(True, alpha=0.3, which='both')