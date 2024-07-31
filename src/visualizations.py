"""Helper functions for project visualizations."""

import folium
import folium.plugins
import geopandas as gpd
import numpy as np
import matplotlib as mpl
import pandas as pd
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
from src.constants import NYC_MAP_CENTER


HEATMAP_COLORS = (
    "#e1e1e1",  # gray-white
    "#cbcacc",
    "#bcbabe",
    "#a4a2a8",  # gray
    "#a88284",
    "#b0403c",
    "#b31f17",  # red
)

CYCLE_COLORS = (
    "#4C72B0",  # blue
    "#C44E52",  # red
    "#8172B2",  # purple
    "#55A868",  # green
    "#CF6D17",  # orange
    "#7F7F7F",  # gray
)


def setup_chart(
    figsize=(18, 10),
    title="",
    titlesize=28,
    titlepad=25,
    ylabel="",
    ylabel_size=22,
    ylabel_rotation="horizontal",
    ylabel_pad=30,
    ylogscale=False,
    ylim=None,
    yaxis_format=None,
    yticksize_major=20,
    xlabel="",
    xlabel_size=22,
    xlabel_rotation="horizontal",
    xlabel_pad=10,
    xlim=None,
    xticksize_major=20,
    xaxis_format=None,
    majortick_locator_x=None,
    xticks=None,
    minor_ticks=False,
    colors=CYCLE_COLORS,
    text=None,
    textfontsize=16,
    textfontstyle="normal",  # italic, bold
):
    """Setup common parameters for Matplotlib charts."""
    fig, ax = plt.subplots()
    fig.set_size_inches(figsize)  # width, height
    ax.set_title(title, fontsize=titlesize, pad=titlepad)
    # y axis
    ax.set_ylabel(
        ylabel,
        fontsize=ylabel_size,
        rotation=ylabel_rotation,
        labelpad=ylabel_pad,
    )
    if ylogscale:
        ax.set_yscale("log")
    if ylim:
        ax.set_ylim(ymin=ylim[0], ymax=ylim[1])
    if yaxis_format:
        ax.yaxis.set_major_formatter(yaxis_format)
    ax.tick_params(axis="y", which="major", labelsize=yticksize_major)
    # x axis
    ax.set_xlabel(
        xlabel,
        fontsize=xlabel_size,
        rotation=xlabel_rotation,
        labelpad=xlabel_pad,
    )
    if xlim:
        ax.set_xlim(xmin=xlim[0], xmax=xlim[1])
    ax.tick_params(axis="x", which="major", labelsize=xticksize_major)
    if xaxis_format:
        ax.xaxis.set_major_formatter(xaxis_format)
    if majortick_locator_x:
        ax.xaxis.set_major_locator(majortick_locator_x)
    if xticks is not None:
        ax.set_xticks(**xticks)

    if minor_ticks:
        ax.minorticks_on()
    else:
        ax.minorticks_off()
    if colors:
        ax.set_prop_cycle("color", colors)  # color_cycle
    if text:
        ax.text(
            text[0],
            text[1],
            text[2],
            transform=ax.transAxes,
            fontsize=textfontsize,
            fontstyle=textfontstyle,
        )
    return fig, ax


def annotate_axis(
    ax,
    x_arr,
    y_arr,
    annotate_digits=1,
    vert_offset=15,
    textcoords="offset pixels",
    annotate_fontsize=14,
    ha="center",
    annotate_bbox=None,
):
    """Annotate axes with y value."""
    for x, y in zip(x_arr, y_arr):
        ax.annotate(
            f"{y:,.{annotate_digits}f}",
            xy=(x, y),
            xytext=(0, vert_offset),
            textcoords=textcoords,
            fontsize=annotate_fontsize,
            ha=ha,
            bbox=annotate_bbox,
        )  # xytext represents offset


def fig_legend(
    fig,
    legend_labels,
    legend_fontsize=16,
    legend_framealpha=0.0,
    legend_bbox=(1.0, 0.9),
    legend_labelspacing=0.7,
    legend_handleheight=1.5,
    **kwargs,
):
    """Setup common parameters for legend attached to figure."""
    legend_args = {
        "fontsize": legend_fontsize,
        "framealpha": legend_framealpha,
        "bbox_to_anchor": legend_bbox,
        "labelspacing": legend_labelspacing,
        "handleheight": legend_handleheight,
    }
    fig.legend(labels=legend_labels, **legend_args, **kwargs)


def grouped_bar_chart(
    df,
    legend_labels="",
    style="default",
    save="",
    relative_gap=0.1,
    bar_fontsize=16,
    bar_padding=3,
    bar_label_bbox=None,
    bar_digits=0,
    legend_args=None,
    **setup_args,
):
    """Make a grouped vertical bar chart from a pd.DataFrame where the DataFrame index
    represents the groupings and columns represent the individual bar heights.
    """
    with plt.style.context(style):
        fig, ax = setup_chart(**setup_args)

        # bar and bar group sizes
        bar_group_width = fig.get_size_inches()[0] / len(df.index)
        bars_no_space_width = bar_group_width * (1 - relative_gap)
        bar_width = (bar_group_width / len(df.columns)) * (1 - relative_gap)

        # x labels and location
        x_labels = df.index
        x_label_locs = []
        for x in range(len(x_labels)):
            x_loc = -bar_width + (bars_no_space_width / 2) + (bar_group_width * x)
            x_label_locs.append(x_loc)
        ax.set_xticks(x_label_locs, x_labels)
        ax.set_axisbelow(True)
        ax.grid(which="major", axis="y", linewidth=0.9)

        # bars and bar labels
        bars = []
        for i in range(len(df.columns)):
            col_name = df.columns[i]
            offset = (bar_width * i) - (bar_width / 2)
            x = [offset + (bar_group_width * j) for j in range(len(df.index))]
            y = df[col_name].values
            bars.append(ax.bar(x, height=y, width=bar_width, label=col_name))
        for bar in bars:
            if bar_label_bbox is None:
                bar_label_bbox = {"facecolor": "none", "edgecolor": "none"}
            ax.bar_label(
                bar,
                labels=[f"{val:,.{bar_digits}f}" for val in bar.datavalues],
                fontsize=bar_fontsize,
                padding=bar_padding,
                bbox=bar_label_bbox,
            )
        # legend
        if legend_labels:
            legend_kwargs = {}
            if legend_args is not None:
                legend_kwargs = legend_args
            fig_legend(
                fig, legend_labels, **legend_kwargs
            )  # legend labels are sensitive to order
    if save:
        plt.savefig(save, bbox_inches="tight")
    plt.show()


def horizontal_bar_chart(
    bar_labels,
    bar_values,
    bar_fontsize=20,
    style="default",
    save="",
    reverse=False,
    **setup_args,
):
    """Make a horizontal bar chart from input bar labels and respective values."""
    with plt.style.context(style):
        fig, ax = setup_chart(**setup_args)
        # horizontal bars
        y = list(range(len(bar_values)))
        if reverse:
            y.reverse()
        bars = ax.barh(y, bar_values)
        ax.set_yticks(y, bar_labels, va="center")
        ax.bar_label(bars, padding=5, fontsize=bar_fontsize)
    if save:
        plt.savefig(save, bbox_inches="tight")
    plt.show()


def line_chart(
    list_x_y_tuples,
    style="default",
    markerstyle="o",
    markersize=10,
    linewidth=5,
    annotate=False,
    annotate_args=None,
    legend_labels=None,
    legend_args=None,
    save="",
    **setup_args,
):
    """Make a line chart."""
    with plt.style.context(style):
        fig, ax = setup_chart(**setup_args)
        # plot lines
        for tup in list_x_y_tuples:
            x_arr, y_arr = tup
            ax.plot(
                x_arr,
                y_arr,
                marker=markerstyle,
                markersize=markersize,
                linewidth=linewidth,
            )
            if annotate:
                annotate_axis(ax, x_arr, y_arr, **annotate_args)

        # legend
        if legend_labels:
            legend_kwargs = {}
            if legend_args is not None:
                legend_kwargs = legend_args
            fig_legend(
                fig, legend_labels, **legend_kwargs
            )  # legend labels are sensitive to order
    if save:
        plt.savefig(save, bbox_inches="tight")
    plt.show()


def format_cbar_default(tick):
    """Default string formatting for numerical color bar ticks."""
    return f"{tick:.2f}"


def heat_map(
    pd_ct,
    labels,
    fig_size=(18, 10),
    colors=HEATMAP_COLORS,
    interpolation=None,
    min_max=None,
    save="",
    cbar_format=format_cbar_default,
):
    """Make a 2D heatmap from a pd.crosstab.

    - labels are a dictionary with the following keys:
        "title", "x_label", "y_label", "cbar_label"
    - interpolation is the interpolation technique to smooth the heatmap boxes
    - min_max is a tuple of the min/max values for the color graduations
    """
    # figure and title
    fig, ax = plt.subplots()
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
        pd_ct,
        cmap=color_map,
        interpolation=interpolation,
        vmin=min_val,
        vmax=max_val,
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
    cbar.ax.set_xticklabels([cbar_format(tick) for tick in cbar.get_ticks()])
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


def make_marker_map(map_data: pd.DataFrame, text_fmt: str, map_center=NYC_MAP_CENTER):
    """Return a prepared Folium map."""
    fmap = folium.Map(location=map_center, zoom_start=10, tiles="OpenStreetMap")
    js_callback = (
        "function (row) {"
        "var marker = L.marker(new L.LatLng(row[0], row[1]));"
        "var icon = L.AwesomeMarkers.icon({"
        "icon: 'fa-exclamation',"
        "iconColor: 'white',"
        "markerColor: 'red',"
        "prefix: 'fa',"
        "});"
        "marker.setIcon(icon);"
        "var popup = L.popup({maxWidth: '300'});"
        "const display_text = {text:"
        + text_fmt
        + "var poptext = $(`<div id='mytext' style='width: 100.0%; height: 100.0%;'> ${display_text.text}</div>`)[0];"
        "popup.setContent(poptext);"
        "marker.bindPopup(popup);"
        "return marker};"
    )
    folium.plugins.FastMarkerCluster(data=map_data, callback=js_callback).add_to(fmap)
    return fmap


def prep_choropleth_df(
    df,
    mask,
    groupby_col,
    agg_col,
    geoseries,
    divisor=1,
    agg_metrics="count",
    round_agg_values=False,
    round_decimal=2,
):
    """Return a gpd.GeoDataFrame prepared for a Folium Choropleth.

    gpd.GeoDataFrame contains a column for index values, a column for an
    aggregated value, and a column for the associated geometry.
    """
    groupby_df = df[mask].groupby(by=groupby_col)[agg_col].agg(agg_metrics).to_frame()
    groupby_df[agg_col] /= divisor
    if round_agg_values:
        groupby_df[agg_col] = groupby_df[agg_col].round(decimals=round_decimal)
        if round_decimal == 0:
            groupby_df[agg_col] = groupby_df[agg_col].astype(int)
    groupby_df.index = groupby_df.index.astype(int)
    groupby_df[groupby_df.index.name] = groupby_df.index
    return gpd.GeoDataFrame(groupby_df, geometry=geoseries)


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
    """Add a choropleth to a folium.Map from a gpd.GeoDataFrame."""
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
