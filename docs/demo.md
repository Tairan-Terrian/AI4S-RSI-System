# 演示步骤

本示例用于说明一个任务如何经过候选生成、评价、选择和反馈进入下一轮。候选参数与指标均来自本地合成适配器。

## 准备

使用 Python 3.10 或更新版本，在仓库根目录打开终端。代码仅依赖 Python 标准库，无需安装额外包，也不需要外部服务凭据。

先查看 `configs/demo.json` 和 `examples/demo_task.json`，确认演示配置与任务定义。

## 运行

```bash
python3 -m ai4s_rsi run --config configs/demo.json --output /tmp/ai4s-rsi-demo
```

命令完成后，输出目录中会生成 `run.json` 和 `summary.md`。检查已有运行：

```bash
python3 -m ai4s_rsi inspect /tmp/ai4s-rsi-demo
```

需要保留不同配置的运行结果时，为每次运行指定不同的输出目录。

## 讲解顺序

1. **任务定义**：展示任务文件与运行配置，说明输入如何传给流程。
2. **候选与评价**：选取一轮，查看候选的 `id`、`parameters{x, y}` 及对应的 `metrics{quality, cost}`。
3. **选择依据**：查看 `selected`，结合当前选择规则解释哪些指标影响了保留结果。
4. **反馈与下一轮**：对照 `feedback` 和后续 `proposals`，说明合成生成逻辑如何使用反馈。
5. **完整记录**：用 `summary.md` 概览运行，再用 `run.json` 追踪具体轮次。

## 解读结果

演示重点是每一步的输入、输出和对应关系。`quality` 的变化反映当前合成评价函数与采样规则的作用。

可以修改随机种子或采样范围，对照运行记录，讲解选择规则和反馈如何影响后续候选。

## 后续扩展

可在保持候选和指标接口清晰的前提下，替换生成或评价适配器。扩展前先明确新指标的含义、选择规则以及反馈的实际用途，具体边界见 [架构说明](architecture.md)。
