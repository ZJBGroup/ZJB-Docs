# 使用手册

定义
---
ZJB平台基于面向对象的模式开发, 我们在平台中定义了一些对象用于组织, 管理以及复用各种数据.

### 数字孪生脑(DTB)
[数字孪生脑](#数字孪生脑dtb)是由真实大脑信息约束的数字化大脑, 能够产生与真实大脑活动相似的模拟大脑活动. 在ZJB平台中, 数字孪生脑主要由[被试](#被试subject), [数字孪生脑模型](#数字孪生脑模型dtbmodel)以及连接矩阵构成. 
- 被试中保存了来自真实大脑的各种信息
- 数字孪生脑模型定义了数字孪生脑随时间演化的动力学, 真实大脑的信息如何约束动力学, 以及数字孪生脑输出何种形式的大脑活动等
- 连接矩阵是数字孪生脑的结构基础, 定义了数字孪生脑中各个脑区之间的连接强度

### 被试(Subject)
[被试](#被试subject)指真实大脑所属的个体. 在ZJB平台中, 被试用于保存个体信息以及大脑相关的数据等, 如由DTI纤维追踪得到的结构连接矩阵, 来自fMRI的BOLD信号及功能连接, 受体密度分布, 重建的皮层结构等.

### 数字孪生脑模型(DTBModel)
在ZJB平台中, [数字孪生脑模型](#数字孪生脑模型dtbmodel)主要由[图谱](#图谱atlas)和[动力学模型](#动力学模型dynamicsmodel)(通常是神经质量模型)构成.
- 图谱刻画了对大脑的分区, 使我们可以将大脑看作由脑区作为节点组成的脑网络
- 动力学模型则描述了网络中各个节点随时间演化的动力学

数字孪生脑模型的核心实际上是一个具有特定分区的脑网络模型. 此外, 数字孪生脑模型还包含了仿真这个脑网络模型所需要的动力学参数, 求解器(Solver),监测器(Monitor)以及默认仿真时间等.
- 动力学参数可以引入来自真实大脑的信息约束, 对动力学模型进行微调等
- 求解器包含了求解微分方程组所需要的参数, 目前包括时间步长(dt)和噪声强度(noises)
- 监测器定义了数字孪生脑模型的输出结果, 其在仿真过程中采样感兴趣变量(或表达式), 并将结果保存下来

### 图谱(Atlas)
在ZJB平台中, [图谱](#图谱atlas)主要是功能性的, 由N个感兴趣区域(脑区)组成, 这些区域通常被定义为空间连续且功能连贯的灰质组织. 图谱可以确定一个由脑区组成的离散空间, 数字孪生脑的大部分数据和活动都在这个空间中.

### 动力学模型(DynamicsModel)
我们定义了结构化的动力学模型, 使得创建一个自定义的动力学模型变得十分容易. 动力学模型由一组状态变量(StateVariable), 一组耦合变量(CouplingVariable), 一组瞬态变量(TransientVariable)和一组默认参数值构成. 状态变量, 耦合变量和瞬态变量都需要一个有效的Python表达式(更具体的,是支持numba编译的表达式), 同时这些表达式中所有变量和结果都应当支持矢量值(由各脑区的值构成).
- 状态变量是指模型中需要积分的变量,其表达式是该状态变量对时间微分的表达式
- 耦合变量是指模型中描述节点之间耦合的项, 对于任一节点, 该项描述了所有节点对该项的作用加权和, 其中权重是节点之间的连接强度(也就是连接矩阵中的元素), 耦合变量的表达式中通常会用到保留变量`__C`(对应仿真时传入的连接矩阵)
- 瞬态变量是指模型中一些需要直接计算或者重复计算的项, 将这些项单独提出来可以降低其他单个变量的表达式的复杂度, 同时避免多个表达式重复计算降低效率.

示例
---
以上部分自上而下地介绍了数字孪生脑及其组成部分, 以下将自下而上地给出创建数字孪生脑的示例.

### 创建动力学模型
平台内置了多种常用的动力学模型, 可以使用`DynamicsModel.list_names()`获取内置动力学模型列表.

```python
>>> from zjb.main.api import DynamicsModel
>>> DynamicsModel.list_names()
['DumontGutkin', 'ReducedWongWang', 'EpileptorRestingState', 'SupHopf', 'MontbrioPazoRoxin', 'CoombesByrne', 'DynamicHopfield', 'GastSchmidtKnosche_SF', 'Hopfield', 'ZetterbergJansen', 'LarterBreakspear', 'ReducedWongWangExcInh', 'Epileptor2D', 'Linear', 'JansenRit', 'GastSchmidtKnosche_SD', 'Generic2dOscillator', 'CoombesByrne2D', 'KIonEx', 'Epileptor', 'WilsonCowan']
```

使用`DynamicsModel.from_name(name)`可以直接创建相应的动力学模型, 如:

```python
>>> dynamics = DynamicsModel.from_name("SupHopf")
```

#### 自定义动力学模型(可选)
当内置的动力学模型不能满足需求时, 平台支持快速创建一个自定义的动力学模型. 以[Suphopf模型](https://www.nature.com/articles/s41598-017-03073-5)为例(该模型已经内置于平台, 此处仅用于演示自定义动力学模型的流程), 该模型(单个节点)可以由如下方程描述:

$$
\begin{align*}
\frac{d{x}_{j}}{dt}&=[{a}_{j}-{x}_{j}^{2}-{y}_{j}^{2}]{x}_{j}-{\omega }_{j}{y}_{j}+G\,\sum _{i}{C}_{ij}({x}_{i}-{x}_{j}) \\
\frac{d{y}_{j}}{dt}&=[{a}_{j}-{x}_{j}^{2}-{y}_{j}^{2}]{y}_{j}+{\omega }_{j}{x}_{j}+G\,\sum _{i}{C}_{ij}({y}_{i}-{y}_{j})
\end{align*}
$$

首先从中提取出以下几个部分:
- 状态变量: 
    - $x$
    - $y$
- 耦合项:
    - $\sum _{i}{C}_{ij}({x}_{i}-{x}_{j})$
    - $\sum _{i}{C}_{ij}({y}_{i}-{y}_{j})$
- 重复计算项:
    - ${a}_{j}-{x}_{j}^{2}-{y}_{j}^{2}$
- 参数:
    - $a$
    - $\omega$
    - $G$

然后可以确定各个变量的表达式及默认参数值, 注意, 表达式必须是合法的Python表达式, 且需要写成矢量形式:
- 状态变量(表达式是对时间的微分)
    - x: ax2y2 * x - omega * y + G * Cx
    - y: ax2y2 * y + omega * x + G * Cy
- 耦合变量(表达式是耦合项, 保留变量`__C`是连接矩阵, `__C_1`相当于`np.sum(__C, 1)`)
    - Cx: __C @ x - __C_1 * x (`@`操作符相当与于`np.matmul`)
    - Cy: __C @ y - __C_1 * y
- 瞬态变量(表达式是直接或重复计算项)
    - ax2y2: a - x * x - y * y
- 参数
    - a: 0
    - omega: 1
    - G: 1



最后, 可以直接创建该自定义模型:

```python
>>> from zjb.main.dtb.dynamics_model import DynamicsModel, StateVariable, CouplingVariable, TransientVariable
>>> dynamics = DynamicsModel(state_variables={
...     "x": StateVariable(expression="ax2y2 * x - omega * y + G * Cx"),
...     "y": StateVariable(expression="ax2y2 * y + omega * x + G * Cy"),
... }, coupling_variables={
...     "Cx": CouplingVariable(expression="__C @ x - __C_1 * x"),
...     "Cy": CouplingVariable(expression="__C @ y - __C_1 * y"),
... }, transient_variables={
...     "ax2y2": TransientVariable(expression="a - x * x - y * y")
... }, parameters={
...     "a": 0,
...     "omega": 1,
...     "G": 1
... })
```

### 创建图谱
如果仅考虑仿真用途, 在平台中创建一个图谱将十分简单, 只需要提供图谱定义的各个脑区的标签(名称). 例如使用数字作为标签创建一个具有246分区的图谱:


```python
>>> from zjb.main.api import Atlas
>>> atlas = Atlas(labels=[f"{i}" for i in range(246)])
```

此外, 平台还支持从[FreeSurfer](https://surfer.nmr.mgh.harvard.edu/)的颜色查找表, .label.gii文件(需要安装`nibabel`)创建图谱

```python
>>> atlas = Atlas.from_lut("atlas name", "/path/to/lut")
>>> atlas = Atlas.from_label_gii("atlas name", "/path/to/.label.gii")
```

### 创建数字孪生脑模型
使用刚刚创建的动力学模型与图谱可以直接创建一个数字孪生脑模型, 只需要额外提供监测器来确定模型要输出的结果, 用于求解动力学模型的求解器是可选的, 默认会使用时间步长为0.1(单位取决于动力学模型本身)的欧拉法求解器.

平台内置了多种监测器, 可以通过`MONITOR_DICT`查看:

```python
>>> from zjb.main.api import MONITOR_DICT
>>> MONITOR_DICT
{'raw': <class 'zjb.main.simulation.monitor.Raw'>, 'sub_sample': <class 'zjb.main.simulation.monitor.SubSample'>, 'temporal_average': <class 'zjb.main.simulation.monitor.TemporalAverage'>, 'bold': <class 'zjb.main.simulation.monitor.BOLD'>}
>>> 
```

其中`Raw`监测器在每一个时间步进行采样后输出结果; `SubSample`监测器在固定间隔的时间步离散采样并输出结果; `TemporalAverage`在固定间隔的时间步内连续采样并将间隔内的结果平均后输出; `BOLD`监测器在每个时间步进行采样, 将其作为血氧气球模型的输入, 然后在固定间隔的时间步采样血氧气球模型的结果作为输出.

监测器需要提供一个有效的Python表达式作为采样目标, 这个表达式可以使用动力学模型中的任意变量和参数进行计算. 如:

```
>>> from zjb.main.api import Raw
>>> monitor=Raw(expression="x + y * 1j")
```

该监测器将在每个求解时间步上采样SupHopf模型的状态变量$x$作为实部, $y$作为虚部的复数作为结果.

据此可以构建一个数字孪生脑模型:

```python
>>> from zjb.main.api import DTBModel
>>> model=DTBModel(atlas=atlas, dynamics=dynamics, monitors=[monitor])
```

#### 设置状态变量初值(可选)
仿真中状态变量的默认初值为0, 这个初值可以在数字孪生脑模型中修改:

```python
>>> model.states = {"x": 0.1, "y": 0.1}
```

#### 使用非默认的动力学参数(可选)
有时候需要使用动力学模型的不同参数进行建模, 可以在数字孪生脑模型中设置非默认的动力学参数而不需要创建新的动力学模型:

```python
>>> model.parameters = {"a": -0.01}
```

数字孪生脑模型的参数应当是动力学模型参数的一个子集, 在仿真时, 这个参数集中的值会覆盖动力学模型中同名参数的值.

#### 使用脑区异质性的参数(可选)
数字孪生脑模型的参数值不仅可以是浮点数, 还可以是一个其图谱脑区空间的向量(长度与图谱脑区数相同):

```python
>>> import numpy as np
>>> model.parameters |= {"omega": np.random.rand(246)}
```

#### 使用来自被试的数据作为参数(可选)
数字孪生脑模型是一个通用的数据, 可以与不同的被试组合建立不同的数字孪生脑. 有时候同样的数据在被试之间存在差异, 因此数字孪生脑模型支持使用字符串作为参数, 这样在数字孪生脑仿真的时候会从被试数据中查找相应的参数作为仿真中所用的实际参数. 例如使用来自被试的BOLD信号圆频率作为模型的圆频率参数:

```python
>>> model.parameters |= {"omega": "bold_omega"}
```

在使用被试数据作为参数时, 在进行数字孪生脑仿真前, 其关联被试必须导入同名的数据(参考[导入其他被试数据](#导入其他被试数据可选))

### 创建被试
被试用于存储来自真实大脑的信息, 可以将构建数字孪生脑所必须的连接矩阵等数据保存到被试数据中. 导入结构/功能连接需要提供一个图谱所定义的脑区空间:

```python
>>> atlas.space
<zjb.main.dtb.atlas.RegionSpace object at 0x7f0fedaff1f0>
>>> from zjb.main.data.correlation import StructuralConnectivity
>>> conn = StructuralConnectivity.from_npy("/path/to/SC/matrix.npy", atlas.space)
```

被试可以直接从类进行创建, `data`属性是一个用于保存数据的字典, 创建时可以传入, 创建后也可以进行更新:

```python
>>> from zjb.main.api import Subject
>>> subject=Subject(data={"SC": conn})
>>> subject.data |= {"SC": conn}
```

#### 导入其他被试数据(可选)
有些数字孪生脑模型可能需要使用被试个性化的参数, 此时需要先将必要的数据导入被试, 如[前文](#使用来自被试的数据作为参数可选)中的模型需要一个BOLD信号圆频率:

```python
>>> import numpy as np
>>> subject.data |= {"bold_omega": np.random.rand(246)}
```

这里使用了一个随机生成的数据作为示例, 实际应用中这个值可以通过对被试的BOLD信号进行处理得到或从外部文件导入等.

### 创建数字孪生脑
有了数字孪生脑模型, 被试和一个来自被试的连接矩阵就可以创建数字孪生脑了:

```python
>>> from zjb.main.api import DTB
>>> dtb = DTB(subject=subject, model=model, connectivity=subject.data["SC"])
```

至此一个具有真实大脑结构约束和SupHopf动力学的数字孪生脑已经创建好了, 只需要调用其仿真函数即可得到数字孪生脑的模拟活动:

```python
>>> dtb.simulate()
<zjb.main.dtb.dtb.SimulationResult at 0x7f3e13acbd30>
```