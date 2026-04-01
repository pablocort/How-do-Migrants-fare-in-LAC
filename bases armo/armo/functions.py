import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



from scipy.stats import norm

def make_weighted_stats_multi(
    df,
    group_cols,
    status_cols,
    weight_col="factor_ci",
    ddof=0,
    flatten_cols=True,
    sep=" ",
    add_dummy_counts=True,
    dummy_values=(0, 1),
    include_n_unweighted=False,
    include_sum_weights=False,
    include_se=False,          # <--- NEW
    include_ci=False,          # <--- NEW
    ci_level=0.95,             # <--- NEW
    include_neff=False,        # <--- NEW
    output_format="wide",
):
    """
    Weighted mean and weighted std for multiple numeric variables by group.

    Optional:
      - add_dummy_counts: for dummy-like vars (0/1), add ones_unweighted and ones_weights
      - include_n_unweighted: include number of valid (x,w) obs per variable
      - include_sum_weights: include sum of weights used per variable
      - include_se: add standard error of the weighted mean
      - include_ci: add confidence interval for the weighted mean (normal approx)
      - include_neff: add Kish effective sample size
      - output_format: "wide" (default) or "long"
    """

    if isinstance(status_cols, str):
        status_cols = [status_cols]

    z = norm.ppf(0.5 + ci_level / 2) if include_ci else None

    def _wstats(g):
        out = {}
        w_all = g[weight_col].astype(float)

        for v in status_cols:
            x_all = g[v].astype(float)

            mask = x_all.notna() & w_all.notna() & (w_all > 0)
            n = int(mask.sum())
            sw = float(w_all[mask].sum()) if n > 0 else 0.0

            if n == 0 or sw == 0:
                out[(v, "mean")] = np.nan
                out[(v, "std")] = np.nan

                if include_se:
                    out[(v, "se")] = np.nan
                if include_ci:
                    out[(v, "ci_lo")] = np.nan
                    out[(v, "ci_hi")] = np.nan
                if include_neff:
                    out[(v, "n_eff")] = 0.0

                if include_n_unweighted:
                    out[(v, "n_unweighted")] = 0
                if include_sum_weights:
                    out[(v, "sum_weights")] = 0.0

                if add_dummy_counts:
                    out[(v, "ones_unweighted")] = 0
                    out[(v, "ones_weights")] = 0.0
                continue

            xx = x_all[mask].to_numpy(dtype=float)
            ww = w_all[mask].to_numpy(dtype=float)

            wsum = ww.sum()
            mu = (ww * xx).sum() / wsum

            # weighted population variance (your original)
            var = (ww * (xx - mu) ** 2).sum() / wsum

            # optional ddof correction via neff (your original logic)
            neff = (wsum ** 2) / (ww ** 2).sum()
            if ddof == 1 and n > 1 and neff > 1:
                var = var * (neff / (neff - 1))

            std = float(np.sqrt(var))

            out[(v, "mean")] = float(mu)
            out[(v, "std")] = std

            if include_neff:
                out[(v, "n_eff")] = float(neff)

            # ---- NEW: SE of weighted mean (general formula) ----
            if include_se or include_ci:
                # SE^2 = sum(w^2*(x-mu)^2) / (sum w)^2
                se2 = np.sum((ww ** 2) * (xx - mu) ** 2) / (wsum ** 2)
                se = float(np.sqrt(se2))
                if include_se:
                    out[(v, "se")] = se
                if include_ci:
                    ci_lo = float(mu - z * se)
                    ci_hi = float(mu + z * se)

                    out[(v, "ci_lo")] = ci_lo
                    out[(v, "ci_hi")] = ci_hi

                    # NEW: distances from mean (for Excel custom error bars)
                    out[(v, "err_lo")] = float(mu - ci_lo)
                    out[(v, "err_hi")] = float(ci_hi - mu)
                
            if include_n_unweighted:
                out[(v, "n_unweighted")] = n
            if include_sum_weights:
                out[(v, "sum_weights")] = sw

            if add_dummy_counts:
                uniq = pd.unique(pd.Series(xx).dropna())
                uniq_set = set(np.round(uniq, 12).tolist())
                is_dummy = uniq_set.issubset(set(dummy_values))

                if is_dummy:
                    out[(v, "ones_unweighted")] = int(np.nansum(xx))
                    out[(v, "ones_weights")] = float(np.nansum(ww * xx))
                else:
                    out[(v, "ones_unweighted")] = np.nan
                    out[(v, "ones_weights")] = np.nan

        return pd.Series(out)

    out = (
        df
        .groupby(group_cols, dropna=False)
        .apply(_wstats)
    )

    out.columns = pd.MultiIndex.from_tuples(out.columns, names=["variable", "stat"])

    if output_format == "long":
        out = (
            out
            .stack(level="variable", future_stack=True)
            .rename_axis(index=list(group_cols) + ["variable"])
            .reset_index()
        )
        return out
    if output_format != "wide":
        raise ValueError("output_format must be 'wide' or 'long'")

    if flatten_cols:
        out.columns = [f"{a}{sep}{b}" for a, b in out.columns]

    return out

# plot point function
def plot_scatter_stats(
    df: pd.DataFrame,
    x_var: str,
    y_var: str,
    hue_var: str,
    palette: str = "Blues",
    figsize: tuple = (12, 7),
    title: str | None = None,
    point_size: float = 220,
    ylabel: str | None = None,
    xlabel: str | None = None,
    y_lim: tuple | None = None,
) -> plt.Figure:

    hue_levels = df[hue_var].unique()
    n_hue = len(hue_levels)

    markers = ["o", "^", "s", "D", "*", "P", "X", "v", "<", ">"]

    # use a richer colour range — skip the very light end of Blues
    palette_colors = sns.color_palette(palette, n_colors=n_hue + 3)[3:]
    color_map  = dict(zip(hue_levels, palette_colors))
    marker_map = {lv: markers[i % len(markers)] for i, lv in enumerate(hue_levels)}

    x_levels = list(df[x_var].unique())
    x_idx    = {lv: i for i, lv in enumerate(x_levels)}

    fig, ax = plt.subplots(figsize=figsize)

    for hue_val in hue_levels:
        sub   = df[df[hue_var] == hue_val]
        x_pos = [x_idx[xv] for xv in sub[x_var]]

        ax.scatter(
            x          = x_pos,
            y          = sub[y_var],
            color      = [(*color_map[hue_val][:3], 0.15)],  # light fill
            edgecolors = color_map[hue_val],
            linewidths = 2.0,
            s          = point_size,
            zorder     = 3,
            marker     = marker_map[hue_val],
            label      = str(hue_val),
        )

        # value labels to the right of each point
        for xp, yp in zip(x_pos, sub[y_var]):
            ax.text(
                xp + 0.05, yp,
                f"{yp:.2f}",
                ha        = "left",
                va        = "center",
                fontsize  = 9,
                color     = color_map[hue_val],
                fontweight= "semibold",
            )

    # ── aesthetics ------------------------------------------------------------
    ax.set_xticks(range(len(x_levels)))
    ax.set_xticklabels(x_levels, rotation=0, ha="center", fontsize=13)
    ax.set_ylabel(ylabel or y_var, fontsize=13, labelpad=10)
    ax.set_xlabel("", fontsize=12)

    if title:
        ax.set_title(title, fontsize=15, pad=14, fontweight="bold")

    ax.tick_params(axis="y", labelsize=12)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, color="lightgrey")
    ax.xaxis.grid(True, linestyle="--", alpha=0.4, color="lightgrey")
    ax.set_axisbelow(True)
    sns.despine(ax=ax)

    # tighter y,x limits
    ax.set_ylim(y_lim)
    ax.set_xlim(-0.4, len(x_levels) - 0.6)

    # ── legend below ---------------------------------------------------------
    hue_handles, hue_labels = ax.get_legend_handles_labels()
    if ax.get_legend():
        ax.get_legend().remove()

    fig.legend(
        handles        = hue_handles,
        labels         = hue_labels,
        loc            = "lower center",
        bbox_to_anchor = (0.5, 0.01),
        ncol           = n_hue,
        frameon        = False,
        fontsize       = 12,
        title          = "",
        markerscale    = 1.3,
    )

    fig.tight_layout(rect=[0, 0.10, 1, 1])
    return fig



# plot function

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_labor_stats(
    df: pd.DataFrame,
    x_var: str,
    hue_var: str,
    filter_variable: str | None = None,
    point_variable: str | None = None,
    palette: str = "Set2",
    figsize: tuple = (10, 6),
    title: str | None = None,
    dodge: float = 0.4,
    capsize: float = 4,
    bar_width: float = 0.15,
    point_size: float = 80,
) -> plt.Figure:

    # ── subset bar data -------------------------------------------------------
    bar_df = df.copy()
    if filter_variable is not None:
        bar_df = bar_df[bar_df["variable"] == filter_variable]
    if bar_df.empty:
        raise ValueError(f"No rows remain after filtering variable='{filter_variable}'.")

    # ── subset point data -----------------------------------------------------
    point_df = None
    if point_variable is not None:
        point_df = df[df["variable"] == point_variable].copy()

    # ── colour map ------------------------------------------------------------
    hue_levels = bar_df[hue_var].unique()
    palette_colors = sns.color_palette(palette, n_colors=len(hue_levels))
    color_map = dict(zip(hue_levels, palette_colors))

    # ── x-axis positions with dodging ----------------------------------------
    x_levels = list(bar_df[x_var].unique())
    x_idx = {lv: i for i, lv in enumerate(x_levels)}
    n_hue = len(hue_levels)
    offsets = np.linspace(-dodge / 2, dodge / 2, n_hue)
    offset_map = dict(zip(hue_levels, offsets))

    # ── draw ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=figsize)

    for hue_val in hue_levels:
        sub = bar_df[bar_df[hue_var] == hue_val]
        x_pos = [x_idx[xv] + offset_map[hue_val] for xv in sub[x_var]]

        ax.bar(
            x=x_pos,
            height=sub["mean"],
            width=bar_width,
            color=color_map[hue_val],
            label=str(hue_val),
            zorder=3,
        )

        yerr = np.array([
            np.abs(sub["err_lo"].values),
            np.abs(sub["err_hi"].values),
        ])
        ax.errorbar(
            x=x_pos,
            y=sub["mean"],
            yerr=yerr,
            fmt="none",
            color="black",
            capsize=capsize,
            linewidth=1.2,
            elinewidth=1.0,
            zorder=4,
        )

        if point_df is not None:
            psub = point_df[point_df[hue_var] == hue_val]
            px_pos = [x_idx[xv] + offset_map[hue_val] for xv in psub[x_var]]

            ax.scatter(
                x=px_pos,
                y=psub["mean"],
                color=color_map[hue_val],
                edgecolors="black",
                linewidths=0.7,
                s=point_size,
                zorder=5,
                marker="D",
            )

            p_yerr = np.array([
                np.abs(psub["err_lo"].values),
                np.abs(psub["err_hi"].values),
            ])
            ax.errorbar(
                x=px_pos,
                y=psub["mean"],
                yerr=p_yerr,
                fmt="none",
                color=color_map[hue_val],
                capsize=capsize,
                linewidth=1.0,
                elinewidth=0.8,
                alpha=0.7,
                zorder=4,
            )

    # ── aesthetics ------------------------------------------------------------
    ax.set_xticks(range(len(x_levels)))
    ax.set_xticklabels(x_levels, rotation=0, ha="center", fontsize=11)
    ax.set_ylabel("Promedio del grupo", fontsize=12)
    ax.set_xlabel("")
    var_label = filter_variable if filter_variable else "all variables"
    ax.set_title(title or f"{var_label}  |  x={x_var}  ·  hue={hue_var}", fontsize=13, pad=12)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    sns.despine(ax=ax)

    # ── legends (figure-level, no duplicates) ---------------------------------
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    # collect hue handles from ax and clear ax legends
    hue_handles, hue_labels = ax.get_legend_handles_labels()
    if ax.get_legend():
        ax.get_legend().remove()

    # hue legend (top row)
    fig.legend(
        handles=hue_handles,
        labels=hue_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.08),
        ncol=len(hue_levels),
        frameon=False,
        fontsize=10,
        title="",
    )

    # geometry legend (bottom row) — only if point_variable is set
    if point_variable is not None:
        geom_handles = [
            Patch(facecolor="grey", edgecolor="none", label=f"Barras: {filter_variable}"),
            Line2D([0], [0], marker="D", color="w", markerfacecolor="grey",
                   markeredgecolor="black", markersize=8, label=f"Puntos: {point_variable}"),
        ]
        fig.legend(
            handles=geom_handles,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.01),
            ncol=2,
            frameon=False,
            fontsize=10,
        )

    fig.tight_layout(rect=[0, 0.18, 1, 1])
    return fig

def check_update():
    print("This is a placeholder for a future function that checks for updates to the codebase or data.")
    print("Yes, updates are available, now1")

import re
import unicodedata

def fix_orthography(text):
    if pd.isna(text):
        return text

    s = str(text).strip()

    # 1) fix common mojibake (e.g., "educaciÃ³n" -> "educación")
    try:
        s = s.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    # 2) normalize unicode composition
    s = unicodedata.normalize("NFC", s)

    # 3) clean spacing
    s = re.sub(r"\s+", " ", s).strip()

    # 4) optional manual corrections for true spelling variants
    corrections = {
        "educacion basica": "educación básica",
        "secundaria incompleta": "secundaria incompleta",
        # add your own here
    }
    s_lower = s.lower()
    s = corrections.get(s_lower, s)

    return s



def make_weighted_stats_multi_old(
    df,
    group_cols,                 # e.g. ['pais_c', 'foreign_born']
    status_cols,                # numeric vars
    weight_col='factor_ci',
    ddof=0,
    flatten_cols=True,
    sep=' '
):
    """
    Weighted mean and weighted standard deviation for multiple numeric variables,
    grouped by group_cols, using weight_col.

    Additionally returns:
      - n_unweighted : number of valid (x,w) observations
      - sum_weights  : sum of weights used

    Output:
      index   = group_cols
      columns = MultiIndex (variable, stat) by default
    """

    if isinstance(status_cols, str):
        status_cols = [status_cols]

    def _wstats(g):
        out = {}
        w = g[weight_col].astype(float)

        for v in status_cols:
            x = g[v].astype(float)

            mask = x.notna() & w.notna() & (w > 0)

            n = mask.sum()
            sw = w[mask].sum()

            if n == 0:
                out[(v, 'mean')] = np.nan
                out[(v, 'std')] = np.nan
                out[(v, 'n_unweighted')] = 0
                out[(v, 'sum_weights')] = 0
                continue

            xx = x[mask].to_numpy()
            ww = w[mask].to_numpy()

            mu = (ww * xx).sum() / sw
            var = (ww * (xx - mu) ** 2).sum() / sw

            if ddof == 1 and n > 1:
                neff = (sw ** 2) / (ww ** 2).sum()
                if neff > 1:
                    var = var * (neff / (neff - 1))

            out[(v, 'mean')] = mu
            out[(v, 'std')] = np.sqrt(var)
            out[(v, 'n_unweighted')] = int(n)
            out[(v, 'sum_weights')] = float(sw)

        return pd.Series(out)

    out = (
        df
        .groupby(group_cols, dropna=False)
        .apply(_wstats)
    )

    out.columns = pd.MultiIndex.from_tuples(
        out.columns, names=['variable', 'stat']
    )

    if flatten_cols:
        out.columns = [f"{a}{sep}{b}" for a, b in out.columns]

    return out





def make_weighted_stats_multi2(
    df,
    group_cols,
    status_cols,
    weight_col="factor_ci",
    ddof=0,
    flatten_cols=True,
    sep=" ",
    add_dummy_counts=True,
    dummy_values=(0, 1),
    include_n_unweighted=False,     # <--- NEW (default off)
    include_sum_weights=False,      # <--- NEW (default off)
):
    """
    Weighted mean and weighted std for multiple numeric variables by group.

    Optional:
      - add_dummy_counts: for dummy-like vars (0/1), add ones_unweighted and ones_weights
      - include_n_unweighted: include number of valid (x,w) obs per variable
      - include_sum_weights: include sum of weights used per variable
    """

    if isinstance(status_cols, str):
        status_cols = [status_cols]

    def _wstats(g):
        out = {}
        w_all = g[weight_col].astype(float)

        for v in status_cols:
            x_all = g[v].astype(float)

            mask = x_all.notna() & w_all.notna() & (w_all > 0)
            n = int(mask.sum())
            sw = float(w_all[mask].sum()) if n > 0 else 0.0

            # means/stds need at least one valid obs with positive weight
            if n == 0 or sw == 0:
                out[(v, "mean")] = np.nan
                out[(v, "std")] = np.nan

                if include_n_unweighted:
                    out[(v, "n_unweighted")] = 0
                if include_sum_weights:
                    out[(v, "sum_weights")] = 0.0

                if add_dummy_counts:
                    out[(v, "ones_unweighted")] = 0
                    out[(v, "ones_weights")] = 0.0
                continue

            xx = x_all[mask].to_numpy()
            ww = w_all[mask].to_numpy()

            mu = (ww * xx).sum() / ww.sum()
            var = (ww * (xx - mu) ** 2).sum() / ww.sum()

            if ddof == 1 and n > 1:
                neff = (ww.sum() ** 2) / (ww ** 2).sum()
                if neff > 1:
                    var = var * (neff / (neff - 1))

            out[(v, "mean")] = float(mu)
            out[(v, "std")] = float(np.sqrt(var))

            if include_n_unweighted:
                out[(v, "n_unweighted")] = n
            if include_sum_weights:
                out[(v, "sum_weights")] = sw

            if add_dummy_counts:
                uniq = pd.unique(pd.Series(xx).dropna())
                uniq_set = set(np.round(uniq, 12).tolist())
                is_dummy = uniq_set.issubset(set(dummy_values))

                if is_dummy:
                    out[(v, "ones_unweighted")] = int(np.nansum(xx))      # count of 1s
                    out[(v, "ones_weights")] = float(np.nansum(ww * xx))  # weighted count of 1s
                else:
                    out[(v, "ones_unweighted")] = np.nan
                    out[(v, "ones_weights")] = np.nan

        return pd.Series(out)

    out = (
        df
        .groupby(group_cols, dropna=False)
        .apply(_wstats)
    )

    out.columns = pd.MultiIndex.from_tuples(out.columns, names=["variable", "stat"])

    if flatten_cols:
        out.columns = [f"{a}{sep}{b}" for a, b in out.columns]

    return out





import pandas as pd

def make_weighted_pivot_multi(
    df,
    group_cols,                 # e.g. ['pais_c', 'foreign_born']
    status_cols,                # e.g. ['formal_ci','tipocontrato_ci'] (list)
    weight_col='factor_ci',
    fill_value=0,
    transpose=False,
    flatten_cols=True,
    sep=' ',
    include_unweighted=False,   # NEW: add unweighted counts
    unweighted_label='unweighted'  # NEW: label for the unweighted block
):
    """
    Creates pivot tables for multiple categorical variables and returns ONE combined table.

    - Weighted: sum of weights (like your original).
    - Optional unweighted: simple counts (N) for the same categories.

    Output columns are a MultiIndex by default:
      Weighted part:   (status_col, category)
      Unweighted part: (status_col, (unweighted_label, category))  [if include_unweighted=True]

    If flatten_cols=True and not transpose:
      Weighted:   'formal_ci <cat>'
      Unweighted: 'formal_ci unweighted <cat>'
    """

    if isinstance(status_cols, str):
        status_cols = [status_cols]

    tables = []
    for sc in status_cols:
        # --- weighted (sum of weights)
        t_w = (
            df.groupby(group_cols + [sc], dropna=False)[weight_col]
              .sum()
              .reset_index(name='counts')
              .pivot(index=group_cols, columns=sc, values='counts')
              .fillna(fill_value)
        )
        t_w.columns = pd.MultiIndex.from_product([[sc], t_w.columns])  # (sc, category)
        tables.append(t_w)

        # --- unweighted (simple counts)
        if include_unweighted:
            t_u = (
                df.groupby(group_cols + [sc], dropna=False)
                  .size()
                  .reset_index(name='counts')
                  .pivot(index=group_cols, columns=sc, values='counts')
                  .fillna(fill_value)
            )
            # make it 3-level columns: (sc, unweighted_label, category)
            t_u.columns = pd.MultiIndex.from_product([[sc], [unweighted_label], t_u.columns])
            tables.append(t_u)

    out = pd.concat(tables, axis=1)

    # optional transpose: groups become columns
    if transpose:
        out = out.T

    # optional flatten columns (only makes sense if NOT transposed)
    if flatten_cols and not transpose:
        if isinstance(out.columns, pd.MultiIndex):
            if out.columns.nlevels == 2:
                # (sc, category)
                out.columns = [f"{a}{sep}{b}" for a, b in out.columns]
            elif out.columns.nlevels == 3:
                # (sc, label, category)
                out.columns = [f"{a}{sep}{b}{sep}{c}" for a, b, c in out.columns]

    return out.T
