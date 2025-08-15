好嘞！下面给你一份**Matplotlib 速查表（实战版）**。每条都尽量配了最短可用代码，并在关键处给了“为什么/何时用”。（其中“非阻塞显示”“布局引擎”“性能优化/光栅化/Blitting”“后端选择与 Agg”这些点我都对照了官方文档与权威讨论区，文末有内联出处）

---

# 1) 非阻塞显示 & 交互更新

**目标**：程序继续往下跑，窗口不被 `show()` 卡住，同时能动态更新。

* 开启交互模式（自动触发重绘）

  ```python
  import matplotlib.pyplot as plt
  plt.ion()                       # 交互开
  fig, ax = plt.subplots()
  line, = ax.plot([], [])
  for i in range(100):
      line.set_data(range(i), range(i))
      plt.pause(0.01)             # 触发一次事件循环与重绘
  ```

  要点：`ion()` 控制是否在每次 pyplot 调用后触发绘制；`pause()` 可“喂”事件循环。([Matplotlib][1], [Stack Overflow][2])

* 明确不阻塞地显示窗口

  ```python
  import matplotlib.pyplot as plt
  plt.plot([1,2,3])
  plt.show(block=False)           # 不阻塞返回
  # 后续代码继续执行……
  ```

  `show(block=...)` 的语义见官方文档；在交互模式下默认就不阻塞，但不同环境下显式传 `False` 更稳。([Matplotlib][3])

> 小贴士：若你发现 `show()` 根本不弹窗，很可能当前是非 GUI 的 **Agg** 后端（只负责渲染到文件）。见“后端选择”。([Stack Overflow][4])

---

# 2) 布局引擎：优先用 Constrained Layout

* 推荐：**Constrained Layout**（更智能，能处理 colorbar、跨行列轴、`subplot_mosaic` 等）

  ```python
  import matplotlib.pyplot as plt
  fig, axs = plt.subplots(2, 2, layout='constrained')  # 3.6+ 推荐写法
  ```

  相比早期的 `tight_layout()`，Constrained Layout 更灵活、效果更好。([Matplotlib][5], [Scientific Computing][6])

* 传统：`tight_layout()` 依然可用（简单场景）

  ```python
  plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
  ```

  但官方也提示更现代的选择是 Constrained Layout。([Matplotlib][7])

---

# 3) 高亮区域：`fill_between` 的“where”用法

* 选择性填充（和你常用“标出插值区间”的思路一致）

  ```python
  ax.plot(x, y)
  mask = (y > 0)                  # True 的区间才会填充
  ax.fill_between(x, y, 0, where=mask, alpha=0.3)
  ```

  `where` 接收与 `x` 等长的布尔数组，连续的 True 段会被填充；不连续会自动分段。([Matplotlib][8])

---

# 4) 性能优化（大数据绘图）

* **光栅化（rasterized）**：大量元素转位图，极大减轻矢量渲染负担

  ```python
  ax.plot(x, y, rasterized=True)
  ```

  对海量点线条特别有效，官方“Performance”页有系统总结。([Matplotlib][9])

* **下采样 / 聚合**：`x[::k]`、统计聚合、或借助 Datashader（更适合百万级点）

  ```python
  ax.plot(x[::10], y[::10])  # 简单而直接
  ```

  思路参考：用光栅化或转向像素/网格聚合的可视化方式。([Medium][10])

* **Blitting 动画/交互**（只重绘变动对象，极大提速）

  ```python
  # 复杂项目建议用 FuncAnimation 或自定义 blit
  ```

  官方给出了手写 blitting 的模板与注意事项。([Matplotlib][11])

> 经验法则：散点>几千点就开始变慢，考虑降采样/聚合/光栅化。([Stack Overflow][12])

---

# 5) 风格与全局配置（rcParams / 样式表）

* 先选风格表，再微调 rc（优先级：**运行时 rcParams > 样式表 > matplotlibrc 文件**）

  ```python
  import matplotlib.pyplot as plt
  plt.style.use('seaborn-v0_8')   # 任选风格
  plt.rcParams.update({
      'font.size': 12,
      'axes.labelsize': 14,
      'axes.titlesize': 16,
  })
  ```

  三种自定义途径与优先级见官方“Customizing”页面。([Matplotlib][13])

---

# 6) 常用坐标轴/多轴技巧

* **双 Y 轴**

  ```python
  ax1 = plt.gca()
  ax2 = ax1.twinx()
  ax1.plot(x, y1); ax2.plot(x, y2)
  ```

* **共享坐标轴**

  ```python
  fig, (ax1, ax2) = plt.subplots(2, sharex=True)
  ```

（这些为 API 例行操作，详见“Interactive figures/pyplot 指南”。）([Matplotlib][14])

---

# 7) 后端选择与“只保存文件”的 Agg

* **查询与切换后端**

  ```python
  import matplotlib
  matplotlib.get_backend()
  matplotlib.use('Agg')    # 顶部尽早调用，渲染到文件、不弹窗
  ```

  Matplotlib 会自动选择可用 GUI 后端；`Agg` 是**非交互**后端，只能写文件。若你在服务器/CI 环境，常用 `Agg`。([Matplotlib][15])

* **遇到 “currently using agg… cannot show the figure”**
  说明当前是非 GUI 环境；要么改后端为 GUI（如 TkAgg/QtAgg），要么别 `show()`，直接 `savefig()`。([Stack Overflow][4])

---

# 8) 导出设置（打印/论文友好）

```python
plt.savefig('fig.png', dpi=300, bbox_inches='tight', transparent=False)
```

* `dpi=300`：高分辨率
* `bbox_inches='tight'`：裁掉多余留白（若布局已用 constrained\_layout，一般不需要再 tight）
  （布局建议见 §2）([Matplotlib][5])

---

# 9) 开发中常见“坑位”与对策

* **`plt.legend(loc="best")` 在大数据下变慢**：自己指定 `loc='upper right'` 等，或减少图元数量（合并线条、下采样）。
* **窗口不刷新/无响应**：交互模式配合 `plt.pause()`；或用 GUI 后端并确保事件循环在跑（IDE/Notebook 差异较大）。([Matplotlib][1])
* **子图/标题/色条挤在一起**：优先 `layout='constrained'`，少用 `tight_layout()` 叠加调参。([Matplotlib][5])

---

## 迷你模板（可直接复用）

```python
import matplotlib
# 若在服务器/CI：取消下一行改用 Agg；若要弹窗显示，请不要用 Agg
# matplotlib.use('Agg')

import matplotlib.pyplot as plt
plt.style.use('seaborn-v0_8')
plt.rcParams.update({'font.size': 12})

plt.ion()                        # 需要非阻塞交互就开
fig, ax = plt.subplots(layout='constrained')

x = range(1000)
y = [i**0.5 for i in x]
ax.plot(x, y, rasterized=True)   # 大量点可开启光栅化
mask = [v > 20 for v in y]
ax.fill_between(x, y, 0, where=mask, alpha=0.2)

plt.show(block=False)            # 不阻塞（或在循环里用 plt.pause）
# 后续代码……
```

---

### 我做的修正说明

* 你之前提到“程序不等待、图像保留”的需求，我在本速查表里明确增加了**两种稳妥方案**：`plt.ion()+plt.pause()` 与 `plt.show(block=False)`，并给出官方语义出处，避免只用 `ion()` 但不触发事件循环导致窗口无响应的情况。([Matplotlib][1], [Stack Overflow][16])
* 关于布局，我建议**优先用 Constrained Layout** 而非一律 `tight_layout()`，这是基于官方当前推荐与近年的实践更新。([Matplotlib][5])
* 大数据绘图我补充了**rasterized** 与 **blitting** 的官方指引，避免仅靠“降采样”这一条路。([Matplotlib][9])

---

需要我把这份速查表做成**一页 PDF**（适合打印/贴墙）吗？我可以再加上“中文字体配置、日期坐标、美化配色循环、保存为矢量 PDF/SVG 的注意点”等一页内搞定。

[1]: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.ion.html?utm_source=chatgpt.com "matplotlib.pyplot.ion — Matplotlib 3.10.5 documentation"
[2]: https://stackoverflow.com/questions/6130341/exact-semantics-of-matplotlibs-interactive-mode-ion-ioff?utm_source=chatgpt.com "Exact semantics of Matplotlib's \"interactive mode\" (ion(), ioff ..."
[3]: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html?utm_source=chatgpt.com "matplotlib.pyplot.show"
[4]: https://stackoverflow.com/questions/56656777/userwarning-matplotlib-is-currently-using-agg-which-is-a-non-gui-backend-so?utm_source=chatgpt.com "Matplotlib is currently using agg, which is a non-GUI ..."
[5]: https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html?utm_source=chatgpt.com "Constrained layout guide"
[6]: https://www.scivision.dev/matplotlib-constrained-layout-tight-layout/?utm_source=chatgpt.com "Matplotlib constrained_layout vs. tight_layout"
[7]: https://matplotlib.org/stable/users/explain/axes/tight_layout_guide.html?utm_source=chatgpt.com "Tight layout guide — Matplotlib 3.10.5 documentation"
[8]: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.fill_between.html?utm_source=chatgpt.com "matplotlib.pyplot.fill_between"
[9]: https://matplotlib.org/stable/users/explain/artists/performance.html?utm_source=chatgpt.com "Performance — Matplotlib 3.10.5 documentation"
[10]: https://medium.com/data-science/how-to-create-fast-and-accurate-scatter-plots-with-lots-of-data-in-python-a1d3f578e551?utm_source=chatgpt.com "How to create fast and accurate scatter plots with lots of ..."
[11]: https://matplotlib.org/stable/users/explain/animations/blitting.html?utm_source=chatgpt.com "Faster rendering by using blitting"
[12]: https://stackoverflow.com/questions/42639129/is-matplotlib-scatter-plot-slow-for-large-number-of-data?utm_source=chatgpt.com "Is matplotlib scatter plot slow for large number of data?"
[13]: https://matplotlib.org/stable/users/explain/customizing.html?utm_source=chatgpt.com "Customizing Matplotlib with style sheets and rcParams"
[14]: https://matplotlib.org/stable/users/explain/figure/interactive.html?utm_source=chatgpt.com "Interactive figures — Matplotlib 3.10.5 documentation"
[15]: https://matplotlib.org/stable/users/explain/figure/backends.html?utm_source=chatgpt.com "Backends — Matplotlib 3.10.5 documentation"
[16]: https://stackoverflow.com/questions/64043973/matplotlib-interactive-mode-wont-work-no-matter-what-i-do?utm_source=chatgpt.com "Matplotlib interactive mode won't work, no matter what I do"
