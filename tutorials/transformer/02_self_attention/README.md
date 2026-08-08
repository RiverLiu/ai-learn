# 02 Self-Attention

Self-Attention 是 Transformer 的核心。它让每个 token 根据当前上下文，动态汇总其它 token 的信息。

## 本章要点

- 每个 token 会生成 Query、Key、Value 三个向量。
- Query 和 Key 用来计算“我应该关注谁”。
- Value 是被加权汇总的信息内容。
- Attention 权重不是人工写死的，而是训练出来的。

## 为什么需要 Attention

句子：

```text
小明把苹果放进书包，因为它太重了。
```

模型处理“它”时，需要判断“它”指什么。

可能相关的 token：

- 小明
- 苹果
- 书包
- 重

Self-Attention 允许“它”这个位置去关注前面的 token，并组合出当前语境下的表示。

## Q/K/V 直觉

可以用检索系统类比：

| 名称 | 类比 | 作用 |
| --- | --- | --- |
| Query | 搜索问题 | 当前 token 想找什么 |
| Key | 文档索引 | 每个 token 能被什么问题匹配 |
| Value | 文档内容 | 真正被取出来的信息 |

当处理“它”时：

```text
Query(它)：我指代的是谁？
Key(苹果)：我是一个物体，可能被指代
Key(书包)：我是一个容器，也可能被指代
Value(苹果)：苹果的语义信息
Value(书包)：书包的语义信息
```

## 计算流程图

```mermaid
flowchart TD
    X[输入向量 x] --> WQ[乘以 Wq 得到 Q]
    X --> WK[乘以 Wk 得到 K]
    X --> WV[乘以 Wv 得到 V]
    WQ --> SCORE[QK^T 计算相关性]
    WK --> SCORE
    SCORE --> SCALE[除以 sqrt(d_k)]
    SCALE --> MASK[可选 Mask]
    MASK --> SOFTMAX[Softmax 得到注意力权重]
    SOFTMAX --> OUT[权重乘以 V 并求和]
    WV --> OUT
```

## 核心公式拆解

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

一步步看：

1. `QK^T`：每个 token 的 Query 和其它 token 的 Key 做点积，得到相关性分数。
2. `/ sqrt(d_k)`：缩放，避免分数过大导致 softmax 过于极端。
3. `softmax`：把分数变成概率分布，所有权重加起来等于 1。
4. `... V`：按权重加权求和，得到融合上下文的新向量。

## 一个简化例子

句子：

```text
猫 坐 垫子
```

当处理“坐”时，假设注意力权重为：

| 关注对象 | 权重 |
| --- | --- |
| 猫 | 0.50 |
| 坐 | 0.20 |
| 垫子 | 0.30 |

那么“坐”的新表示可以理解为：

```text
新向量 = 0.50 * V(猫) + 0.20 * V(坐) + 0.30 * V(垫子)
```

这个新向量不再只是“坐”本身，而是融合了“谁坐、坐在哪里”的上下文。

## Attention 矩阵

Self-Attention 会为每对 token 计算关系。

```text
          被关注 token
          猫     坐     垫子
当前 猫   0.60   0.30   0.10
token 坐  0.50   0.20   0.30
     垫子 0.20   0.40   0.40
```

每一行表示一个 token 在更新自己表示时关注其它 token 的比例。

## Masked Self-Attention

训练和生成大语言模型时，模型不能偷看未来 token。

输入：

```text
今天 天气 很 好
```

当模型预测“很”后面的 token 时，只能看：

```text
今天 天气 很
```

不能看未来的“好”。

Mask 图：

```text
        今天  天气  很   好
今天     ✓    ×    ×    ×
天气     ✓    ✓    ×    ×
很       ✓    ✓    ✓    ×
好       ✓    ✓    ✓    ✓
```

这就是 Decoder-only LLM 使用 causal mask 的原因。

## 常见误解

**误解：Attention 权重就是模型解释。**

Attention 权重能提供一些直觉，但不能完全等同于可靠解释。模型内部还有 MLP、残差、多层叠加等复杂机制。

**误解：模型总会关注正确 token。**

不会。注意力是统计学习结果，遇到歧义、缺少信息或干扰上下文时也会出错。

## 练习

分析句子：

```text
小红把水杯放进包里，因为它容易漏水。
```

“它”更可能关注哪个 token？如果句子改成“因为它空间很大”，注意力可能如何变化？
