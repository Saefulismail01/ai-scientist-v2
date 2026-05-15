# Title: Fractal-Based Mathematical Formulations for Bitcoin Trading

## Keywords
Bitcoin, fractal trading, Hurst exponent, R/S analysis, multifractal, scaling law, power law, stable Paretian, Mandelbrot, MMAR, MF-DFA, trading indicators, mathematical formulation, regime detection, entry-exit signals, stop loss, position sizing, risk management, fractal dimension, local scaling exponent, LLF, wild bubble, volatility clustering

## TL;DR
Menemukan rumusan matematis berbasis fractal theory untuk trading BTC — menentukan indikator-indikator fractal apa saja yang diperlukan (Hurst exponent, fractal dimension, multifractal spectrum width, local scaling exponent, LLF), bagaimana merumuskannya sebagai sinyal trading (entry, exit, stop loss), dan bagaimana mengkombinasikannya dalam suatu sistem trading yang terukur.

## Abstract
This research aims to derive actionable mathematical formulations for Bitcoin trading using Mandelbrot's fractal framework. Unlike previous descriptive studies, we focus on constructing concrete trading indicators from fractal theory: (1) Rolling Hurst exponent H(t) as trend persistence indicator — H > 0.65 confirms trend, H < 0.4 signals mean reversion; (2) Local scaling exponent α(t) from L-stable distribution fitting as volatility regime filter; (3) Multifractal spectrum width Δα(t) as regime change detector — widening spectrum precedes trend reversal; (4) Fractal dimension D(t) = 2 - H as market efficiency measure; (5) Leader-Lagging Factor (LLF) from cross-correlation analysis for momentum confirmation. Each indicator is derived from first principles (R/S analysis, DFA, MF-DFA, MLE stable fitting), formulated as a real-time computable function, and validated on Bitcoin data across multiple halving cycles. The output is a mathematical specification: given price vector P[1..n], compute indicator vector I(t) = [H(t), α(t), Δα(t), D(t), LLF(t)], with entry/exit rules defined as threshold conditions on I(t). Backtest framework evaluates Sharpe ratio, max drawdown, win rate across 2010-2025.

## Domain-specific notes
- Reference materials: documentation/chapter-01-lengkap.md, chapter-03-new-methods.md, chapter-04-discontinuity.md, chapter-05-self-affine.md, mandelbrot-bitcoin-analysis.md (all in project /documentation)
- Primary methods: R/S analysis (Chapter 3), DFA, MF-DFA, L-stable MLE fitting, multifractal spectrum estimation, rolling window Hurst exponent, local scaling exponents, fractal dimension estimation
- Data: Bitcoin daily price from 2010 (CoinGecko/Binance), tick data if accessible, 4 halving epochs
- Key focus: MATHEMATICAL FORMULATION of trading indicators from fractal theory — NOT just descriptive analysis. Each indicator must be defined as a mathematical function I(t) = f(P[1..n], params) with clear computational steps.
- Required outputs: (1) Mathematical specification of each fractal indicator, (2) Entry/exit rule set, (3) Backtest results, (4) Indicator combination logic, (5) Risk management rules
- Evaluation: Sharpe ratio, max drawdown, win rate, profit factor, number of trades, consistency across halving cycles
