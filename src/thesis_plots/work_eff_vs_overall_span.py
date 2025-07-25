import matplotlib.cm as cm
import matplotlib.patches as mpatches
import matplotlib.ticker as mtick
import numpy as np
from collections import defaultdict

from header import *


def span_comparison_best_vs_work_efficient(algs):
    """
    Plots a histogram comparing the span of the fastest algorithm vs.
    the most work-efficient algorithm for a set of problems.
    """
    num = len(algs)
    names = list(algs.keys())
    fun = complexity_category_1

    categories_dict = {}
    for aspect in ["bs span", "we span"]:
        aspects_list = [algs[name][aspect] for name in names]
        aspects_list.sort()
        for raw_aspect in aspects_list:
            category = fun(raw_aspect)
            if category not in categories_dict:
                categories_dict[category] = {"bs span": 0, "we span": 0}
            categories_dict[category][aspect] += 1

    plt.style.use('default')
    fig, ax = plt.subplots(1, 1, figsize=(6.5, 4.25), dpi=200, layout='tight')

    for i, aspect in enumerate(["bs span", "we span"]):
        aspect_num = sum(categories_dict[x][aspect] for x in categories_dict)
        assert aspect_num == num

        aspect_values = [categories_dict[x][aspect] / aspect_num * 100 for x in categories_dict]
        ax.bar(
            categories_dict.keys(),
            aspect_values,
            width=0.8 * i - 0.4,
            align='edge',
            color=COLORS[i]
        )

    handles = [
        mpatches.Patch(color=COLORS[0], label="Fastest Algorithm (Best Span)"),
        mpatches.Patch(color=COLORS[1], label="Most Efficient Algorithm")
    ]
    ax.legend(handles=handles)

    ax.set_title("Best Span vs. Best Work-efficient Algorithm Span\nfor all (Parallel) Problems")
    ax.set_xticks(ax.get_xticks(), categories_dict.keys(), rotation=90)
    ax.set_yticks(ax.get_yticks(), [f"{x:.0f}%" for x in ax.get_yticks()])
    ax.set_xlabel("Best Span Complexity Class")
    ax.set_ylabel("Percentage of Algorithm Problems")

    plt.savefig(SAVE_LOC + 'span_comparison.png')
    # plt.show()


def NEW_span_comparison_best_vs_work_efficient(algs):
    """
    Generates a stacked horizontal bar chart comparing the complexity distribution
    for the fastest span vs. the most work-efficient span.
    """
    num = len(algs)
    fun = complexity_category_1

    categories_dict = {}
    for aspect in ["bs span", "we span"]:
        aspects_list = [algs[name][aspect] for name in algs]
        aspects_list.sort()
        for raw_aspect in aspects_list:
            category = fun(raw_aspect)
            if category not in categories_dict:
                categories_dict[category] = {"bs span": 0, "we span": 0}
            categories_dict[category][aspect] += 1

    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(6.5, 2), dpi=200, layout='tight')

    categories = list(categories_dict.keys())
    best_span_values = [categories_dict[x]["bs span"] / num * 100 for x in categories]
    we_span_values = [categories_dict[x]["we span"] / num * 100 for x in categories]

    # Bar properties
    y_positions = [0.6, 0.4]
    bar_height = 0.15

    pre_linear = ["constant", "logarithmic", "polylog", "sublinear"]
    linear_group = ["linear", "quadratic", "cubic"]
    supercubic = ["supracubic/\nexponential"]

    pre_linear_colors = {cat: cm.Blues(i) for cat, i in zip(pre_linear, np.linspace(0.4, 1, len(pre_linear)))}
    linear_colors = {cat: cm.Greens(i) for cat, i in zip(linear_group, np.linspace(0.4, 1, len(linear_group)))}
    supercubic_colors = {cat: cm.Reds(i) for cat, i in zip(supercubic, np.linspace(0.4, 1, len(supercubic)))}
    GRADIENT_COLORS = {**pre_linear_colors, **linear_colors, **supercubic_colors}

    bottom_best = 0
    bottom_we = 0
    patches = []

    for i, cat in enumerate(categories):
        color = GRADIENT_COLORS.get(cat, 'gray')

        ax.barh(y_positions[0], best_span_values[i], height=bar_height, color=color, left=bottom_best)
        bottom_best += best_span_values[i]

        ax.barh(y_positions[1], we_span_values[i], height=bar_height, color=color, left=bottom_we)
        bottom_we += we_span_values[i]

        patches.append(mpatches.Patch(color=color, label=cat))

    ax.set_yticks(y_positions)
    ax.set_yticklabels(["Best Span", "Work-Efficient Span"])

    ax.legend(
        handles=patches,
        title="Complexity Class",
        loc="center left",
        bbox_to_anchor=(1.05, 0.5),
        ncol=2,
        fontsize=8,
        frameon=False
    )

    ax.set_title("Best Span vs. Work-efficient Span for All Problems", fontsize=10)
    ax.set_xlabel("Percentage of Algorithm Problems")
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())

    plt.savefig(SAVE_LOC + 'NEW_span_comparison_stacked.png')
    # plt.show()


def NEW_w_seq_span_comparison_best_vs_work_efficient(algs):
    """
    Generates a stacked horizontal bar chart comparing complexity for three
    algorithm types: fastest span, fastest work-efficient, and best sequential.

    Features:
    1.  **Improved Labeling**: Dynamically places labels inside or outside bars
        with targeted adjustments to prevent overlap.
    2.  **Corrected Flow Lines**: Dashed lines correctly track categories
        between bars, even for categories with a zero-percent share.
    """
    num = len(algs)
    fun = complexity_category_1

    categories_dict = defaultdict(lambda: {"bs span": 0, "we span": 0, "best seq": 0})
    category_order = [
        "constant", "logarithmic", "polylog", "sublinear",
        "linear", "quadratic", "cubic", "supracubic/\nexponential"
    ]

    for name in algs:
        for aspect in ["bs span", "we span", "best seq"]:
            raw_aspect = algs[name][aspect]
            category = fun(raw_aspect)
            if category in category_order:
                categories_dict[category][aspect] += 1

    categories = [c for c in category_order if c in categories_dict]

    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)

    best_span_values = [categories_dict[x]["bs span"] / num * 100 for x in categories]
    we_span_values = [categories_dict[x]["we span"] / num * 100 for x in categories]
    best_seq_values = [categories_dict[x]["best seq"] / num * 100 for x in categories]

    y_positions = [0.8, 0.5, 0.2]
    bar_height = 0.2

    pre_linear = ["constant", "logarithmic", "polylog", "sublinear"]
    linear_group = ["linear", "quadratic", "cubic", "supracubic/\nexponential"]

    pre_linear_colors = {cat: cm.Blues(i) for cat, i in zip(pre_linear, np.linspace(0.8, 0.3, len(pre_linear)))}
    linear_colors = {cat: cm.Greens(i) for cat, i in zip(linear_group, np.linspace(0.4, 1, len(linear_group)))}
    GRADIENT_COLORS = {**pre_linear_colors, **linear_colors}

    bottoms = [0, 0, 0]
    all_values = [best_span_values, we_span_values, best_seq_values]
    category_max_bar = {}
    category_right_edges = defaultdict(dict)

    for i, cat in enumerate(categories):
        color = GRADIENT_COLORS.get(cat, 'gray')
        for j, y_pos in enumerate(y_positions):
            val = all_values[j][i]
            left = bottoms[j]
            ax.barh(y_pos, val, height=bar_height, color=color, left=left, zorder=2)

            right_edge = left + val
            category_right_edges[cat][y_pos] = right_edge

            if cat not in category_max_bar or val > category_max_bar[cat][1]:
                category_max_bar[cat] = (j, val, left, y_pos)

            bottoms[j] = right_edge

    for cat in categories:
        x1 = category_right_edges[cat][y_positions[0]]
        x2 = category_right_edges[cat][y_positions[1]]
        x3 = category_right_edges[cat][y_positions[2]]

        ax.plot([x1, x2], [y_positions[0] - bar_height / 2, y_positions[1] + bar_height / 2],
                linestyle='--', color='gray', linewidth=0.8, alpha=0.7, zorder=1)

        ax.plot([x2, x3], [y_positions[1] - bar_height / 2, y_positions[2] + bar_height / 2],
                linestyle='--', color='gray', linewidth=0.8, alpha=0.7, zorder=1)

    sorted_cats = sorted(category_max_bar.items(), key=lambda item: item[1][2] + item[1][1] / 2)
    label_threshold = 7
    custom_offsets = {
        "sublinear": 0.22,
        "cubic": -0.07,
    }
    default_offset = 0.12

    for cat, (bar_idx, val, left, y) in sorted_cats:
        center_x = left + val / 2

        if val > label_threshold:
            # Place label inside wider bars
            ax.text(
                center_x, y, cat,
                ha='center', va='center', fontsize=8, color='white', weight='bold', zorder=3
            )
        else:
            # Place label outside smaller bars with an arrow
            y_offset = custom_offsets.get(cat, default_offset)
            ax.annotate(cat.replace("\n", " "), xy=(center_x, y), xytext=(center_x, y + bar_height / 2 + y_offset), ha='center', va='bottom', arrowprops=dict(arrowstyle='-', color='black', lw=0.8, shrinkB=3), fontsize=8, weight='bold', color='white')

    # --- Final Formatting ---
    ax.set_yticks(y_positions)
    ax.set_yticklabels(
        ["Fastest Algorithm\n(Span)", "Fastest Work-Efficient\nAlgorithm (Span)", "Fastest Sequential\nAlgorithm (Runtime)"],
        fontsize=10, va='center'
    )
    ax.tick_params(axis='y', length=0, pad=10)

    ax.set_title("Span and Runtime Complexity Distribution Across Algorithm Types", fontsize=14, weight='bold', pad=20)
    ax.set_xlabel("Percentage of Problems", fontsize=10)
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())

    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(SAVE_LOC + 'NEW_w_seq_span_comparison_stacked.png', bbox_inches='tight')
    # plt.show()
