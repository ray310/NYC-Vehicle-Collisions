"""Helper functions for project visualizations"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import folium
import folium.plugins


HEATMAP_COLORS = [
    "#e1e1e1",  # gray-white
    "#cbcacc",
    "#bcbabe",
    "#a4a2a8",  # gray
    "#a88284",
    "#b0403c",
    "#b31f17",  # red
]

CYCLE_COLORS = [
    "#4C72B0",  # blue
    "#C44E52",  # red
    "#8172B2",  # purple
    "#55A868",  # green
    "#CF6D17",  # orange
    "#7F7F7F",  # gray
]


def make_grouped_bar_chart(
    df,
    title="",
    x_label="",
    y_label="",
    legend_labels="",
    style="default",
    save="",
    fig_size=(18, 10),
    relative_gap=0.1,
    title_fontsize=32,
    label_fontsize=22,
    ylabel_rotation="horizontal",
    ylabel_pad=60,
    logscale=False,
    major_tick_fontsize=20,
    minor_tick_fontsize=14,
    minor_ticks_off=False,
    colors=None,
    bar_fontsize=16,
    legend_fontsize=16,
    legend_bbox=(1.1, 0.9),
    legend_labelspacing=0.7,
    legend_handleheight=1.5,
    bar_label_bbox={"facecolor": "none", "edgecolor": "none"},
):
    """Makes a grouped bar chart from a pd.DataFrame where the DataFrame index represents
    the groupings and columns represent the individual bar heights"""
    with plt.style.context(style):
        # bar and bar group sizes
        bar_group_width = fig_size[0] / len(df.index)
        bars_no_space_width = bar_group_width * (1 - relative_gap)
        bar_width = (bar_group_width / len(df.columns)) * (1 - relative_gap)

        # x labels and location
        x_labels = df.index
        x_label_locs = []
        for x in range(len(x_labels)):
            x_loc = -bar_width + (bars_no_space_width / 2) + (bar_group_width * x)
            x_label_locs.append(x_loc)

        # figure, title, and axis labels
        fig, ax = plt.subplots()
        fig.set_size_inches(fig_size)  # width, height
        ax.set_title(title, fontsize=title_fontsize, pad=30)
        ax.set_ylabel(
            y_label,
            fontsize=label_fontsize,
            rotation=ylabel_rotation,
            labelpad=ylabel_pad,
        )
        ax.set_xlabel(x_label, fontsize=label_fontsize, labelpad=10)

        # tick labels, size, and gridlines
        if logscale:
            ax.set_yscale("log")
        ax.yaxis.set_major_formatter("{x:,.0f}")
        ax.yaxis.set_minor_formatter("{x:,.0f}")
        ax.tick_params(which="major", labelsize=major_tick_fontsize)
        ax.tick_params(which="minor", labelsize=minor_tick_fontsize)
        ax.set_xticks(x_label_locs, x_labels)
        ax.set_axisbelow(True)
        ax.grid(which="major", axis="y", linewidth=0.9)

        if minor_ticks_off:
            ax.minorticks_off()

        # bars and bar labels
        if colors:
            ax.set_prop_cycle("color", colors)  # color_cycle
        bar_labels = []
        for i in range(len(df.columns)):
            col_name = df.columns[i]
            offset = (bar_width * i) - (bar_width / 2)
            x = [offset + (bar_group_width * j) for j in range(len(df.index))]
            y = df[col_name].values
            bar_labels.append(ax.bar(x, height=y, width=bar_width, label=col_name))

        for bl in bar_labels:
            ax.bar_label(
                bl,
                labels=[f"{val:,.0f}" for val in bl.datavalues],
                fontsize=bar_fontsize,
                padding=3,
                bbox=bar_label_bbox,
            )

        # legend
        legend_args = {
            "fontsize": legend_fontsize,
            "framealpha": 0.0,
            "bbox_to_anchor": legend_bbox,
            "labelspacing": legend_labelspacing,
            "handleheight": legend_handleheight,
        }
        if legend_labels:  # manually labeling legend is sensitive to order
            fig.legend(labels=legend_labels, **legend_args)
        else:
            fig.legend(**legend_args)
    if save:
        plt.savefig(save, bbox_inches="tight")
    plt.show()


def make_heat_map(
    pd_ct, labels, colors=None, interpolation=None, min_max=None, save=""
):
    """Makes a 2D heatmap from a pd.crosstab.
    - labels are a dictionary with the following keys:
        "title", "x_label", "y_label", "cbar_label"
    - colors are the list of color graduations to use for the heatmap
    - interpolation is the interpolation technique to smooth the heatmap boxes
    - min_max is a tuple of the min/max values for the color graduations"""

    # figure and title
    fig, ax = plt.subplots()
    fig_size = (18, 10)
    fig.set_size_inches(fig_size)  # width, height
    ax.set_title(labels["title"], fontsize=22, pad=50)

    # x axis
    ax.set_xlabel(labels["x_label"], fontsize=16)
    ax.set_xticks(np.arange(len(pd_ct.columns)) - 0.5)  # -0.5 for left alignment
    ax.set_xticklabels(pd_ct.columns, fontsize=14)

    # y axis
    ax.set_ylabel(labels["y_label"], fontsize=18)
    ax.set_yticks(np.arange(len(pd_ct.index)))
    ax.set_yticklabels(pd_ct.index, fontsize=14)

    # x and y ticks
    ax.tick_params(labeltop=True, labelright=True)

    # heatmap and heatmap colors
    if min_max:
        min_val = min_max[0]
        max_val = min_max[1]
    else:
        min_val = min(pd_ct.min())
        max_val = max(pd_ct.max())

    if colors:
        color_map = ListedColormap(colors)
        step = (max_val - min_val) / len(color_map.colors)
    else:
        default_graduations = 7
        color_map = mpl.cm.get_cmap("viridis")  # matplotlib default
        step = (max_val - min_val) / default_graduations

    im = ax.imshow(
        pd_ct, cmap=color_map, interpolation=interpolation, vmin=min_val, vmax=max_val,
    )

    # colorbar
    cbar = fig.colorbar(
        im,
        ticks=np.arange(min_val, max_val + step, step),
        orientation="horizontal",
        aspect=50,
        pad=0.1,
    )  # aspect is ratio of x to y
    cbar.ax.set_xlabel(labels["cbar_label"], rotation=0, fontsize=16)
    cbar.ax.set_xticklabels([f"{tick:.2f}" for tick in cbar.get_ticks()])
    cbar.ax.tick_params(labelsize=14)

    # gridlines
    offset = 0.5
    col_len = len(pd_ct.columns)
    row_len = len(pd_ct.index)

    ax.vlines(
        x=(np.arange(col_len) + offset),
        ymin=(-offset),
        ymax=row_len - offset,
        colors="gray",
        linewidth=0.3,
    )
    ax.hlines(
        y=(np.arange(row_len) + offset),
        xmin=(-offset),
        xmax=col_len - offset,
        colors="gray",
        linewidth=0.3,
    )
    if save:
        plt.savefig(save, bbox_inches="tight")
    plt.show()


def add_choropleth(
    choro_map,
    gdf,
    key_col,
    val_col,
    tooltip_cols=None,
    tooltip_aliases=None,
    popup_cols=None,
    popup_aliases=None,
    bins=9,
    fill_color="YlOrRd",
    fill_opacity=0.6,
    line_color="gray",
    line_opacity=1.0,
    legend_name="",
):
    """Adds a choropleth to a folium.Map from a gpd.GeoDataFrame"""
    choropleth = folium.Choropleth(
        geo_data=gdf,
        data=gdf,
        columns=[key_col, val_col],  # key_column, value_column
        key_on="feature.properties." + key_col,  # for both DataFrame and geojson
        bins=bins,
        fill_color=fill_color,
        fill_opacity=fill_opacity,
        line_color=line_color,
        line_opacity=line_opacity,
        legend_name=legend_name,
        highlight=True,
    )
    choropleth.add_to(choro_map)

    if tooltip_cols or popup_cols:
        style = lambda x: {"opacity": 0, "fillOpacity": 0}
        info_layer = folium.GeoJson(data=gdf, style_function=style)
        info_layer.add_to(choro_map)

    if tooltip_cols:
        tooltip = folium.features.GeoJsonTooltip(
            fields=tooltip_cols, aliases=tooltip_aliases, localize=True
        )
        tooltip.add_to(info_layer)

    if popup_cols:
        popup = folium.features.GeoJsonPopup(
            fields=popup_cols, aliases=popup_aliases, localize=True
        )
        popup.add_to(info_layer)
    folium.plugins.Fullscreen().add_to(choro_map)
