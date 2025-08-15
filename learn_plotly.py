# import numpy as np
# import plotly.graph_objects as go
# from plotly.io import renderers
# from plotly.subplots import make_subplots

# x = np.array([0,1,2,3,4,5,6,7,8,9,10], dtype=float)
# y = np.array([0,0.3,2.5,2.5,1.0,4.0,3.8,3.8,1.5,2.2,0.5], dtype=float)
# line_shapes = ["linear", "spline", "hv", "vh", "hvh", "vhv"]

# fig = make_subplots(rows=2, cols=6, subplot_titles=line_shapes,
#                     vertical_spacing=0.12, horizontal_spacing=0.03)

# for i, ls in enumerate(line_shapes, start=1):
#     # 第一行：折线
#     fig.add_trace(
#         go.Scatter(x=x, y=y, mode="lines+markers",
#                    line_shape=ls, showlegend=False, marker=dict(size=6)),
#         row=1, col=i
#     )
#     # 第二行：填充
#     fig.add_trace(
#         go.Scatter(x=x, y=y, mode="lines",
#                    line_shape=ls, fill="tozeroy", showlegend=False),
#         row=2, col=i
#     )

# fig.update_layout(title="line_shape 对比（上：线，下：填充）",
#                   width=1600, height=650, margin=dict(l=40, r=20, t=60, b=60))
# fig.show(renderers="browser")

# %%

# fill_compare_with_gap.py
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1) 构造一段带 gap 的时间序列：y1 有一个 None 区间；y2 在 y1 基础上上移用于 tonexty/tonextx 对比
x = np.linspace(0, 10, 201)
y1 = np.sin(x)
y2 = y1 + 0.8

# 在 [3.5, 5.0] 范围制造 gap：用 None 让 Plotly 断开线段与填充
gap_mask = (x >= 3.5) & (x <= 5.0)
y1_gap = y1.copy()
y2_gap = y2.copy()
y1_gap[gap_mask] = None
y2_gap[gap_mask] = None

# 2) 2×3 子图：依次展示 None/tozeroy/tozerox/tonexty/tonextx/toself
titles = ["fill=None", "fill='tozeroy'", "fill='tozerox'",
          "fill='tonexty'", "fill='tonextx'", "fill='toself'"]
fig = make_subplots(rows=2, cols=3, subplot_titles=titles,
                    vertical_spacing=0.12, horizontal_spacing=0.08)

# --- (1,1) 无填充：可直观看到 None 造成的“断线 / 无填充”
fig.add_trace(
    go.Scatter(x=x, y=y1_gap, mode="lines+markers",
               name="y1 (gap)", showlegend=False),
    row=1, col=1
)

# --- (1,2) tozeroy：向 y=0 填充；gap 处会“断开”，不会跨越 None
fig.add_trace(
    go.Scatter(x=x, y=y1_gap, mode="lines", fill="tozeroy",
               name="y1→0", showlegend=False),
    row=1, col=2
)

# --- (1,3) tozerox：向 x=0 填充；同样会在 gap 处断开
fig.add_trace(
    go.Scatter(x=x, y=y1_gap, mode="lines", fill="tozerox",
               name="y1→x=0", showlegend=False),
    row=1, col=3
)

# --- (2,1) tonexty：第二条曲线相对“上一条曲线”的 y 值填充
# 先放基准曲线（不填充）
fig.add_trace(
    go.Scatter(x=x, y=y1_gap, mode="lines", name="base y1", showlegend=False),
    row=2, col=1
)
# 再放上层曲线（填充到上一条曲线）；注意顺序！gap 处同样断开
fig.add_trace(
    go.Scatter(x=x, y=y2_gap, mode="lines", fill="tonexty",
               name="y2 fill→prev y", showlegend=False, opacity=0.5),
    row=2, col=1
)

# --- (2,2) tonextx：与上一条曲线沿 x 方向闭合；同样需要“先上一条，再这一条”
fig.add_trace(
    go.Scatter(x=x, y=y1_gap, mode="lines", name="base y1", showlegend=False),
    row=2, col=2
)
fig.add_trace(
    go.Scatter(x=x, y=y2_gap, mode="lines", fill="tonextx",
               name="y2 fill→prev x", showlegend=False, opacity=0.5),
    row=2, col=2
)

# --- (2,3) toself：自闭合成多边形。这里用一条“带回环”的曲线构造闭合形状
# 为了直观，这里单独构造一个闭合路径（不引入 None，避免多边形破碎）
x_poly = np.r_[2, 3, 4, 5, 4, 3, 2]
y_poly = np.r_[0.5, 1.2, 1.6, 0.8, 0.2, 0.3, 0.5]
fig.add_trace(
    go.Scatter(x=x_poly, y=y_poly, mode="lines",
               fill="toself", showlegend=False, name="polygon"),
    row=2, col=3
)

# 3) 统一样式
for r in (1, 2):
    for c in (1, 2, 3):
        fig.update_xaxes(title_text="x", row=r, col=c)
        fig.update_yaxes(title_text="y", row=r, col=c)

fig.update_layout(
    title="Plotly fill 选项对比（包含 None 造成的 gap）",
    width=1200, height=700, margin=dict(l=50, r=30, t=60, b=50)
)

fig.show(renderers="browser")

# 小提示：
# 若想“跨越” gap 强行连线/填充，可在对应 trace 里加 connectgaps=True（谨慎使用）。
# 例如：
# go.Scatter(x=x, y=y1_gap, fill='tozeroy', connectgaps=True)



# %%
# fill_break_on_none.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 造一段带 gap 的数据：中间一段置为 None
x = np.linspace(0, 10, 201)
y = np.sin(x)
gap_mask = (x >= 4.0) & (x <= 6.0)
y_gap = y.copy().astype(object)     # 注意：要支持 None，转成 object 或用 np.nan 也行
y_gap[gap_mask] = np.nan

# 第二条曲线用于 tonexty（与 y_gap 同步出现 gap）
y2_gap = y_gap.copy()
y2_gap = np.where(pd.isna(y2_gap), np.nan, y_gap + 0.8)

fig = make_subplots(rows=2, cols=2,
                    subplot_titles=[
                        "方法A：单条trace + None（connectgaps=False）",
                        "方法B：按非空段拆分为多条trace",
                        "tonexty：基线+上层（都带 None）",
                        "tonexty（拆段更稳）"
                    ],
                    vertical_spacing=0.12, horizontal_spacing=0.08)

# ── 方法A：单条 trace，None 自动打断；显式设置 connectgaps=False（默认就是 False）
fig.add_trace(
    go.Scatter(x=x, y=y_gap, mode="lines",
               fill="tozeroy", connectgaps=False,
               name="tozeroy - single trace", showlegend=False),
    row=1, col=1
)

# ── 方法B：把连续非空段拆分后逐段画（最可靠）
def segments_by_valid(x, y):
    y = np.asarray(y, dtype=object)
    valid = ~pd.isna(y)
    if not valid.any():
        return
    # 找到有效/无效的边界
    edges = np.flatnonzero(np.diff(valid.astype(int)) != 0) + 1
    chunks = np.split(np.arange(len(x)), edges)
    for idx in chunks:
        if valid[idx].all():    # 仅输出“全有效”的段
            yield x[idx], y[idx]

for xi, yi in segments_by_valid(x, y_gap):
    fig.add_trace(
        go.Scatter(x=xi, y=yi, mode="lines",
                   fill="tozeroy", showlegend=False,
                   name="tozeroy - segmented"),
        row=1, col=2
    )

# ── tonexty：两条曲线之间填充
# 方式A：单段（两条曲线都带 None，顺序：先基线，再上层 with fill='tonexty'）
fig.add_trace(
    go.Scatter(x=x, y=y_gap, mode="lines", name="base y", showlegend=False),
    row=2, col=1
)
fig.add_trace(
    go.Scatter(x=x, y=y2_gap, mode="lines", fill="tonexty",
               name="upper fill→prev y", showlegend=False, opacity=0.4),
    row=2, col=1
)

# 方式B：拆段更稳（尤其叠加复杂时不易出现意外多边形）
for xi, yi in segments_by_valid(x, y_gap):
    # 基线段
    fig.add_trace(
        go.Scatter(x=xi, y=yi, mode="lines", showlegend=False),
        row=2, col=2
    )
    # 上层段（x 范围一致），注意：为了简洁，直接用同一段的上层值
    yi2 = np.asarray(yi, dtype=float) + 0.8
    fig.add_trace(
        go.Scatter(x=xi, y=yi2, mode="lines", fill="tonexty",
                   showlegend=False, opacity=0.4),
        row=2, col=2
    )

fig.update_layout(
    width=1200, height=800,
    title="在 None 处断开填充，后续数据再继续填充（含 tonexty 示例）",
    margin=dict(l=50, r=30, t=60, b=50)
)
fig.show(renderers="browser")

# 备注：
# - connectgaps=False 会在 None 处打断线段与填充；若设置 True 会跨越 gap（通常不符合你的需求）。
# - tonexty/tonextx 一定要“先添加基线，再添加带 fill 的上层 trace”，且两条曲线在 gap 处都需要 None。
# - 拆段法在复杂布局（多轨迹叠加、线形/填充混合）时更稳，不会出现跨 gap 的“意外三角形”。


import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 造数据：一段 NaN 作为 gap
x = np.linspace(0, 10, 201)
y1 = np.sin(x)
y2 = y1 + 0.8
gap = (x >= 4.0) & (x <= 6.0)
y1[gap] = np.nan
y2[gap] = np.nan  # 关键：两条曲线在同一位置都为 NaN

fig = make_subplots(rows=3, cols=1, subplot_titles=["tozeroy（单曲线）", "tonexty（拆段更稳）"])

# A) 单曲线 tozeroy：NaN 处会断开填充（connectgaps 默认 False）
fig.add_trace(go.Scatter(x=x, y=y1, mode="lines", fill="tozeroy", name="y1"),
              row=1, col=1)

# B) tonexty：按“同时有效”的区段拆开画（每段两条：基线 + 上层）
mask_both = np.isfinite(y1) & np.isfinite(y2)
# 找连续 True 的区段
edges = np.flatnonzero(np.diff(mask_both.astype(int)) != 0) + 1
idx_chunks = np.split(np.arange(len(x)), edges)

for idx in idx_chunks:
    if not mask_both[idx].all():
        continue
    xi, y1i, y2i = x[idx], y1[idx], y2[idx]
    # 先基线
    fig.add_trace(go.Scatter(x=xi, y=y1i, mode="lines", showlegend=False),
                  row=2, col=1)
    # 再上层，填充到“上一条”（即基线）
    fig.add_trace(go.Scatter(x=xi, y=y2i, mode="lines", fill="tonexty",
                             opacity=0.45, showlegend=False),
                  row=2, col=1)

fig.add_trace(go.Scatter(x=x, y=y1, mode="lines", name="y1"),
              row=3, col=1)
fig.add_trace(go.Scatter(x=x, y=y2, mode="lines", name="y2", fill="tonexty"),
              row=3, col=1)

fig.update_layout(width=1000, height=420, title="gap 处不填充：推荐用拆段法确保稳定")
fig.show()
