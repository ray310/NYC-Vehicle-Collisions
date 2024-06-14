"""Helper functions for project visualizations"""

import folium
import folium.plugins
import geopandas as gpd
import numpy as np
import matplotlib as mpl
import pandas as pd
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
from src.constants import NYC_MAP_CENTER


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
    ylabel_pad=30,
    logscale=False,
    major_tick_fontsize=20,
    minor_tick_fontsize=14,
    minor_ticks_off=False,
    colors=None,
    bar_fontsize=16,
    bar_padding=3,
    legend=True,
    legend_fontsize=16,
    legend_bbox=(1.1, 0.9),
    legend_labelspacing=0.7,
    legend_handleheight=1.5,
    bar_label_bbox=None,
    bar_digits=0,
):
    """Makes a grouped vertical bar chart from a pd.DataFrame where the DataFrame index
    represents the groupings and columns represent the individual bar heights"""
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
        if legend:
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


def make_horizontal_bar_chart(
    bar_labels,
    bar_values,
    title="",
    x_label="",
    style="default",
    save="",
    fig_size=(18, 10),
    title_fontsize=32,
    label_fontsize=22,
    major_tick_fontsize=20,
    reverse=False,
):
    """Makes a horizontal bar chart from input bar labels and respective values"""
    with plt.style.context(style):
        # figure, title, and axis labels
        fig, ax = plt.subplots()
        fig.set_size_inches(fig_size)  # width, height
        ax.set_title(title, fontsize=title_fontsize, pad=30)
        ax.set_xlabel(x_label, fontsize=label_fontsize, labelpad=10)

        # horizontal bars
        y = list(range(len(bar_values)))
        if reverse:
            y.reverse()
        bars = ax.barh(y, bar_values)
        ax.set_yticks(y, bar_labels, va="center")

        # tick labels and size
        ax.bar_label(bars, padding=5, fontsize=20)
        ax.tick_params(which="major", labelsize=major_tick_fontsize)

    if save:
        plt.savefig(save, bbox_inches="tight")
    plt.show()


def make_line_chart(
    list_x_y_tuples,
    style="default",
    fig_size=(18, 10),
    title="",
    title_fontsize=32,
    y_label="",
    label_fontsize=22,
    ylabel_rotation="horizontal",
    ylabel_pad=60,
    x_label="",
    logscale=False,
    y_lim=None,
    yaxis_digits=0,
    set_major_tick_x=None,
    tick_fontsize=20,
    colors=None,
    markerstyle="o",
    markersize=10,
    linewidth=5,
    annotate=False,
    annotate_digits=1,
    vert_offset=15,
    annotate_fontsize=14,
    annotate_bbox=None,
    legend_labels=None,
    legend_fontsize=16,
    legend_bbox=(1.1, 0.9),
    legend_labelspacing=0.7,
    legend_handleheight=1.5,
    text=None,
    text_fontsize=16,
    text_fontstyle="normal",
    save="",
):
    """Makes a line chart"""
    with plt.style.context(style):
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

        # axes parameters and colors
        ax.tick_params(which="both", labelsize=tick_fontsize)
        if logscale:
            ax.set_yscale("log")
        if y_lim:
            ax.set_ylim(ymin=y_lim[0], ymax=y_lim[1])
        ax.yaxis.set_major_formatter(f"{{x:,.{yaxis_digits}f}}")
        if set_major_tick_x:
            ax.xaxis.set_major_locator(set_major_tick_x)
        if colors:
            ax.set_prop_cycle("color", colors)  # color_cycle

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
                for x, y in zip(x_arr, y_arr):
                    ax.annotate(
                        f"{y:,.{annotate_digits}f}",
                        xy=(x, y),
                        xytext=(0, vert_offset),
                        textcoords="offset pixels",
                        fontsize=annotate_fontsize,
                        ha="center",
                        bbox=annotate_bbox,
                    )  # xytext represents offset

        # legend
        if legend_labels:
            legend_args = {
                "fontsize": legend_fontsize,
                "framealpha": 0.0,
                "bbox_to_anchor": legend_bbox,
                "labelspacing": legend_labelspacing,
                "handleheight": legend_handleheight,
            }
            fig.legend(
                labels=legend_labels, **legend_args
            )  # manually labeling legend is sensitive to order

        if text:
            ax.text(
                text[0],
                text[1],
                text[2],
                transform=ax.transAxes,
                fontsize=text_fontsize,
                fontstyle=text_fontstyle,
            )

    if save:
        plt.savefig(save, bbox_inches="tight")
    plt.show()


def format_cbar_default(tick):
    """Default string formatting for numerical color bar ticks"""
    return f"{tick:.2f}"


def make_heat_map(
    pd_ct,
    labels,
    colors=None,
    interpolation=None,
    min_max=None,
    save="",
    cbar_format=format_cbar_default,
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
    """Returns a prepared Folium map"""
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
    """Returns a gpd.GeoDataFrame prepared for a Folium Choropleth.
    gpd.GeoDataFrame contains a column for index values, a column for an aggregated value,
    and a column for the associated geometry"""
    groupby_df = df[mask].groupby(by=groupby_col)[agg_col].agg(agg_metrics).to_frame()
    groupby_df[agg_col] /= divisor
    if round_agg_values:
        groupby_df[agg_col] = groupby_df[agg_col].round(decimals=round_decimal)
        if round_decimal == 0:
            groupby_df[agg_col] = groupby_df[agg_col].astype(int)
    groupby_df.index = groupby_df.index.astype(int)
    groupby_df[groupby_df.index.name] = (
        groupby_df.index
    )  # need 2 columns for Folium Choropleth
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
