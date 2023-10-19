<div align='center'> 

# 仓管排班问题

</div>


# Constraint

1. 人力班次结构以月为单位：一个月内每天的所有人力班次的时间段固定，但时间段内每天的分配人数可以变化

2. 人力班次开始时间点必须是某个到发车班次的开始时间点

3. 人力班次结束时间点必须是某个到发车班次的结束时间点

4. 人力班次的时间长度有限制（默认4-9小时）

5. （软约束）完成任务同时，不要有人力富裕

6. （软约束）人力资源是有限的

# Hypothesis

1. 人效恒定（不论哪一天哪一趟到发车班次）
2. 每天的到发车班次时间固定

# Problem Formulation

## 变量说明

- $m$: 第m个到发车班次， $m = 1 \dots M$
- $t$: 第t个时间粒度, $t=1 \dots T$
- $s$: 第s个到发车班次, $s=1 \dots S$
- $L_m$: 第m个人力班次的时长
- $\beta_m$：第m个人力班次是否与时间粒度t重合 $\beta_m = 0~or~1$
- $\alpha_{ts}$: 第s个到发车班次是否与时间粒度t重合 $\alpha_{ts} = 0~or~1$
- $e_{nt}$：第n天的第t个时间粒度的人效
- $Y_{ns}$: 第n天的第s个到发车班次的件量
- $L_s$: 第s个物流班次的时长
- $l_{nt}$: 第n天的第t个时间粒度的时长
- $f$或$f_n$: 每天的人力总数限制


## Step1 求解月度班次结构

模型:

$min\;\Sigma_{m=1}^M x_mL_m$

$s.t.$ 

$\Sigma_{m=1}^M \beta_{tm} x_m e l_{nt} + s_{tn}^- - s_{nt}^+ \geq \Sigma_{s=1}^S \alpha_{ts} \frac{Y_{ns}}{L_s}l_{nt}\;\forall{t}, \forall{n}$ 

$\Sigma_{m=1}^M x_{m} \leq f$

解得 $\mathbf{x} = \{x_1, x_2, \dots,x_m, \dots x_M \}$

然后获得新的班次结构 $\mathbf{x^{,}} = \{x_1, \dots,x_W | x_w \in \mathbf{x}\land x_w > 0 , w=1\dots W\}$

## Step2 求解日度解

分别求解每天的解

$for~n = 1\dots N:$

求解

$min\; \Sigma_{w=1}^{W}x_{tw}L_w$

$s.t.$

$\Sigma_{w=1}^W \beta_{tw} x_{tw} e_t l_{nt} + s_{nt}^- + s_{nt}^+ \geq \Sigma_{s=1}^{S}\alpha_{ts} \frac{Y_{ns}}{L_s} l_{nt}\; \forall{t}$

$\Sigma_{w=1}^W x_{tw} \leq f_n$

解得 $\mathbf{X^,} = \{\mathbf{x_1}, \mathbf{x_2}, \dots, \mathbf{x_N}\}，where~\mathbf{x_n} = \{x_1, x_2, \dots, x_W\}$