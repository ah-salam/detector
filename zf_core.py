# -*- coding: utf-8 -*-
"""ZF-Core."""
import numpy as np, pandas as pd
import yfinance as yf

# ===== sec_config =====
# ======================================================================
# KONFIGURASI  — universe = 15 saham syariah dari screenshot Bibit
# ======================================================================
CONFIG = {
    "universe": [
        # === Watchlist Stockbit MASTER (26 Agu 2026, 08:00) ===
        "AADI", "ADRO", "AKRA", "ARCI", "ASGR", "BACH", "BRMS", "CTRA",
        "DSNG", "ELSA", "ERAA", "HRTA", "JPFA", "JSMR", "KLBF", "KOTA",
        "LSIP", "MAPA", "MBMA", "MDIA", "MDKA", "MEDC", "MYOR", "PGAS",
        "PSAB", "PTBA", "RGAS", "SIDO", "SMMT", "TINS", "TPIA",
    ],

    # Bobot faktor fundamental (basis skor 0-100 sebelum tilt makro)
    "weights": {
        "value": 0.25, "quality": 0.25, "growth": 0.15,
        "momentum": 0.20, "liquidity": 0.15,
    },

    # Peta saham -> tema komoditas (untuk overlay makro)
    "theme_map": {
        "AADI": ["coal"], "ADRO": ["coal"], "BYAN": ["coal"],
        "MEDC": ["oil_gas"], "PGAS": ["oil_gas"],
        "ANTM": ["gold", "nickel", "silver"], "MDKA": ["gold", "copper"], "MBMA": ["nickel"],
        "LSIP": ["cpo"], "INKP": ["paper"], "TPIA": ["petrochem"],
        "AKRA": ["distribution"], "CMRY": ["consumer_defensive"],
        "JPFA": ["poultry"], "KLBF": ["pharma"],
        # tambahan
        "TLKM": ["telco"], "ICBP": ["consumer_defensive"], "INDF": ["consumer_defensive"],
        "UNTR": ["coal", "gold"], "SIDO": ["pharma"], "MIKA": ["pharma"],
        "AMRT": ["consumer_defensive"], "ACES": ["consumer_defensive"],
        "PGEO": ["renewable"], "SMGR": ["cement"],
        "HRTA": ["gold"], "PSAB": ["gold"], "ARCI": ["gold", "silver"], "BRMS": ["gold", "silver"],
        # dari watchlist Stockbit
        "ASGR": ["tech"], "AUTO": ["auto"], "BSSR": ["coal"], "CTRA": ["property"],
        "DSNG": ["cpo"], "ELSA": ["oil_gas"], "ERAA": ["distribution"],
        "ITMG": ["coal"], "JSMR": ["infra"], "MAPA": ["consumer_cyclical"],
        "MYOR": ["consumer_defensive"], "PTBA": ["coal"], "TINS": ["tin"],
        "KOTA": ["property"], "MDIA": ["media"], "SMMT": ["coal"],
    },

    # Bias makro MANUAL untuk komoditas yg tak ada ticker gratis rapi.
    # Skala -2..+2. Default = pembacaan 29 Jul 2026 (UPDATE saat kondisi berubah).
    # coal ~US$130 konsolidasi (netral) · nickel ~US$16,3rb lemah/oversupply (-)
    # cpo ~MYR4,64rb melunak + tarif AS 10% (-) · paper/poultry netral
    "macro_manual": {
        "coal": 0, "nickel": 0, "cpo": 0, "paper": 0, "poultry": 0,
        "telco": 0, "renewable": 0, "cement": 0,
        "tech": 0, "auto": 0, "property": 0, "infra": 0, "consumer_cyclical": 0, "tin": 0,
        "_asof": "2026-07-29",
    },

    # Ambang rasio syariah (OJK / POJK 8-2025)
    "sharia_debt_to_assets_max": 0.45,
    "sharia_debt_watch_level":   0.33,
    "sharia_nonhalal_max":       0.05,

    # Gerbang kelayakan
    "min_history_days": 200,
    "min_avg_value_idr": 5e9,
    "min_data_completeness": 0.5,

    # Timing (ZF-Core, closed-bar)
    "ema_fast": 13, "ema_slow": 50, "atr_period": 14,
    "swing_lookback": 20,       # bar utk cari support
    "resist_lookback": 40,      # bar utk cari resistance
    "tp_R": [2.0, 4.0, 6.0],    # ladder take-profit dlm kelipatan risiko (R)

    # Alert & notifikasi
    "alert_buy_zone": True,      # picu saat harga masuk area beli
    "alert_sl_break": True,      # picu saat harga tembus stop loss
    "alert_breakout": True,
    "telegram_parse": "HTML",    # format pesan Telegram
    "scheduler_interval_min": 30,# jeda loop pemantauan (menit)

    # Filter harga: tampilkan hanya saham dgn harga < nilai ini (None = semua)
    "max_price": None,   # filter harga dinonaktifkan (None = tampilkan semua)

    "hanya_syariah_ok": False,
    "gemini_model": "gemini-2.0-flash",  # ganti bila perlu (model Gemini yg tersedia di akunmu)
    "sector_neutral": True,       # skoring z-score per sektor (apple-to-apple)
    "account_size": 100000000,    # modal (Rp) utk position sizing
    "risk_per_trade_pct": 0.01,   # risiko per trade (1% dari modal)
    "highlight_min_konfluensi": 4,  # baris di-highlight jika Saran BELI & konfluensi >= ini
    "scalp_min_value_idr": 10000000000,  # min likuiditas kandidat scalp (Rp/hari) = 10 M
    "scalp_liq_full": 50000000000,       # likuiditas utk skor penuh = 50 M/hari
    "scalp_score_min": 60,               # ambang kirim Telegram
    "scalp_top_n": 8,
    "ticker_suffix": ".JK",
    "gh_owner": "ah-salam",       # utk tombol Refresh di dashboard
    "gh_repo": "detector",
    "gh_workflow": "monitor.yml",
    "show_guide": True,    # panel "Cara Pakai" di dashboard
    "show_charts": True,   # grafik komoditas realtime (TradingView) di dashboard
    "top_n": 35,
    "sleep_between": 0.9,
    "export_csv":  "zf_syariah_timing_rank.csv",
    "export_xlsx": "zf_syariah_timing_rank.xlsx",
    "export_html": "zf_syariah_timing_dashboard.html",
}

_FUND_KEYS = ["per", "pbv", "div_yield", "roe", "net_margin", "der",
             "rev_growth", "earn_growth", "market_cap"]

# ===== sec_utils =====
# ======================================================================
# UTILITAS
# ======================================================================
def rsi_wilder(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    ag = gain.ewm(alpha=1 / period, adjust=False).mean()
    al = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = ag / al.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return float(out.iloc[-1]) if len(out.dropna()) else np.nan


def safe_ret(close, lookback):
    if len(close) > lookback:
        return float(close.iloc[-1] / close.iloc[-lookback] - 1)
    return np.nan


def g(info, *keys):
    for k in keys:
        v = info.get(k)
        if v is not None and not (isinstance(v, float) and np.isnan(v)):
            return v
    return np.nan


def stmt_val(stmt, *names):
    """Ambil nilai kolom TERBARU utk baris yg cocok (fuzzy) dari laporan keuangan."""
    if stmt is None or getattr(stmt, "empty", True):
        return np.nan
    for name in names:
        for idx in stmt.index:
            if name.lower() in str(idx).lower():
                s = stmt.loc[idx].dropna()
                if len(s):
                    return float(s.iloc[0])
    return np.nan


def sector_zscore(df, col, higher_better=True):
    """Z-score dalam grup sektor (fallback global). Map ke 0..100. Grup kecil -> netral 50."""
    s = pd.to_numeric(df[col], errors="coerce")
    def zg(x):
        m, sd = x.mean(), x.std(ddof=0)
        if sd == 0 or np.isnan(sd):
            return pd.Series(0.0, index=x.index)
        return (x - m) / sd
    if "sector" in df.columns:
        z = s.groupby(df["sector"]).transform(zg)
    else:
        z = zg(s)
    z = z.fillna(0.0)
    if not higher_better:
        z = -z
    return (z.clip(-2.5, 2.5) / 2.5 * 50) + 50

# ===== sec_timing =====
# ======================================================================
# MESIN TIMING BELI/JUAL  (ZF-Core: closed-bar, ATR-based, R-ladder)
# ======================================================================
def atr_wilder(high, low, close, period=14):
    prev = close.shift(1)
    tr = pd.concat([(high - low), (high - prev).abs(), (low - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()

def compute_timing(hist):
    """Hitung sinyal + area beli, SL, TP ladder dari OHLC harian (closed-bar)."""
    c = hist["Close"].dropna()
    h = hist["High"].reindex(c.index)
    l = hist["Low"].reindex(c.index)
    if len(c) < 60:
        return {}
    cfg = CONFIG
    last  = float(c.iloc[-1])
    ema_f = float(c.ewm(span=cfg["ema_fast"], adjust=False).mean().iloc[-1])
    ema_s = float(c.ewm(span=cfg["ema_slow"], adjust=False).mean().iloc[-1])
    sma200 = float(c.rolling(200).mean().iloc[-1]) if len(c) >= 200 else float(c.mean())
    atr = float(atr_wilder(h, l, c, cfg["atr_period"]).iloc[-1])
    rsi = rsi_wilder(c)
    vol = hist["Volume"].reindex(c.index).fillna(0)
    _rng = (h - l).replace(0, np.nan)
    _mfv = (((c - l) - (h - c)) / _rng) * vol
    _cmf = _mfv.rolling(20).sum() / vol.rolling(20).sum().replace(0, np.nan)
    cmf = float(_cmf.iloc[-1]) if len(_cmf.dropna()) else 0.0
    support = float(l.tail(cfg["swing_lookback"]).min())
    resist  = float(h.tail(cfg["resist_lookback"]).max())

    uptrend   = (ema_f > ema_s) and (last > sma200)
    downtrend = (ema_f < ema_s) and (last < sma200)
    dist = (last - ema_s) / atr if atr > 0 else 0.0

    # --- sinyal ---
    if downtrend:
        signal = "HINDARI (downtrend)"
    elif last >= resist * 0.997:
        signal = "BREAKOUT"
    elif (rsi is not None and rsi > 72) or dist > 2.5:
        signal = "TUNGGU PULLBACK"
    elif uptrend and dist <= 0.8:
        signal = "BUY ZONE"
    elif uptrend:
        signal = "TREND (tahan/add)"
    else:
        signal = "NETRAL / AMATI"

    # --- area beli (pullback ke EMA-slow ala ZF) ---
    if signal == "BREAKOUT":
        entry_lo, entry_hi = resist, resist + 0.5 * atr
        entry_ref = resist
    else:
        entry_ref = ema_s
        entry_lo = max(support + 0.1 * atr, ema_s - 0.5 * atr)
        entry_hi = ema_s + 0.3 * atr

    # --- SL di bawah struktur, R = jarak entry->SL ---
    sl = min(support - 0.5 * atr, entry_ref - 2.5 * atr)
    R = max(entry_ref - sl, 0.5 * atr)
    tp = [entry_ref + m * R for m in cfg["tp_R"]]

    return {
        "last": last, "ema_fast": ema_f, "ema_slow": ema_s, "sma200": sma200,
        "atr": atr, "support": support, "resist": resist, "rsi_t": rsi,
        "signal": signal, "entry_lo": entry_lo, "entry_hi": entry_hi,
        "sl": sl, "tp1": tp[0], "tp2": tp[1], "tp3": tp[2],
        "risk_pct": (entry_ref - sl) / entry_ref if entry_ref else np.nan, "cmf": cmf,
    }

# ===== sec_sharia_fetch =====
# ======================================================================
# EVALUASI RASIO SYARIAH (Lapis 2)  +  PENGAMBILAN DATA
# ======================================================================
def status_from_ratios(dta, nhr):
    """Tentukan status syariah dari rasio utang/aset & nonhalal (dipakai ulang)."""
    c = CONFIG
    if dta is None or (isinstance(dta, float) and np.isnan(dta)):
        return "PERLU CEK (data rasio kurang)"
    if dta > c["sharia_debt_to_assets_max"]:
        return f"LEWAT BATAS UTANG ({dta:.0%} > 45%)"
    if (nhr is not None) and not (isinstance(nhr, float) and np.isnan(nhr)) and nhr > c["sharia_nonhalal_max"]:
        return f"NONHALAL >5% ({nhr:.1%})"
    if dta > c["sharia_debt_watch_level"]:
        return f"OK (waspada, {dta:.0%} menuju 33%)"
    return "SYARIAH OK"


def eval_sharia(bs, inc):
    """Hitung rasio utang/aset & pendapatan nonhalal, tentukan status syariah."""
    total_assets = stmt_val(bs, "Total Assets")
    total_debt   = stmt_val(bs, "Total Debt")
    if np.isnan(total_debt):
        ltd = stmt_val(bs, "Long Term Debt")
        std = stmt_val(bs, "Current Debt", "Short Term Debt")
        total_debt = np.nansum([ltd, std]) if not (np.isnan(ltd) and np.isnan(std)) else np.nan

    total_rev = stmt_val(inc, "Total Revenue", "Operating Revenue")
    int_inc   = stmt_val(inc, "Interest Income Non Operating", "Interest Income")

    dta = total_debt / total_assets if (total_assets and not np.isnan(total_debt) and total_assets > 0) else np.nan
    nhr = int_inc / total_rev if (total_rev and not np.isnan(int_inc) and total_rev > 0) else np.nan

    return {"debt_to_assets": dta, "nonhalal_ratio": nhr,
            "sharia_status": status_from_ratios(dta, nhr)}


def fetch_one(ticker):
    sym = f"{ticker}.JK"
    row = {"ticker": ticker, "symbol": sym}
    try:
        tk = yf.Ticker(sym)
        try:
            info = tk.info or {}
        except Exception:
            info = {}

        row["name"]   = g(info, "shortName", "longName")
        row["sector"] = g(info, "sector") or "Lainnya"
        row["price"]  = g(info, "currentPrice", "regularMarketPrice")
        row["per"]        = g(info, "trailingPE")
        row["pbv"]        = g(info, "priceToBook")
        dy                = g(info, "dividendYield")
        row["div_yield"]  = dy * 100 if (isinstance(dy, (int, float)) and dy < 1) else dy
        row["roe"]        = g(info, "returnOnEquity")
        row["net_margin"] = g(info, "profitMargins")
        row["der"]        = g(info, "debtToEquity")
        row["rev_growth"] = g(info, "revenueGrowth")
        row["earn_growth"]= g(info, "earningsGrowth")
        row["market_cap"] = g(info, "marketCap")

        hist = tk.history(period="1y", auto_adjust=False)
        if hist is None or hist.empty or len(hist) < 30:
            return None
        close = hist["Close"].dropna()
        vol   = hist["Volume"].dropna()
        row["hist_days"] = len(close)
        try:
            row["last_bar"] = str(pd.Timestamp(hist.index[-1]).date())
        except Exception:
            row["last_bar"] = ""
        n = min(60, len(close))
        row["avg_value_idr"] = float((close.tail(n) * vol.tail(n)).mean())
        row["ret_3m"] = safe_ret(close, 63)
        row["ret_6m"] = safe_ret(close, 126)
        sma50  = close.rolling(50).mean().iloc[-1]  if len(close) >= 50  else np.nan
        sma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else np.nan
        last = close.iloc[-1]
        row["above_sma50"]  = 1.0 if (pd.notna(sma50)  and last > sma50)  else 0.0
        row["above_sma200"] = 1.0 if (pd.notna(sma200) and last > sma200) else 0.0
        row["rsi"] = rsi_wilder(close)

        try:
            bs, inc = tk.balance_sheet, tk.income_stmt
        except Exception:
            bs, inc = None, None
        row.update(eval_sharia(bs, inc))

        # timing beli/jual (closed-bar)
        try:
            row.update(compute_timing(hist) or {})
        except Exception:
            pass

        avail = sum(1 for k in _FUND_KEYS if pd.notna(row.get(k)))
        row["data_completeness"] = avail / len(_FUND_KEYS)
        return row
    except Exception as e:
        print(f"  ! {ticker}: {e}")
        return None

# ===== sec_score =====
# ======================================================================
# SKORING  (percentile rank cross-sectional -> 0..100)
# ======================================================================
def pct(series, higher_better=True):
    s = pd.to_numeric(series, errors="coerce")
    r = s.rank(pct=True)
    if not higher_better:
        r = 1 - r
    return (r * 100).fillna(50.0)


def rsi_health(rsi):
    s = 100 - (np.abs(pd.to_numeric(rsi, errors="coerce") - 55).clip(upper=45) / 45 * 100)
    return s.fillna(50.0)


def kelayakan_row(r):
    notes = []
    if r.get("hist_days", 0) < CONFIG["min_history_days"]:
        notes.append("riwayat kurang")
    if r.get("avg_value_idr", 0) < CONFIG["min_avg_value_idr"]:
        notes.append("likuiditas tipis")
    if r.get("data_completeness", 0) < CONFIG["min_data_completeness"]:
        notes.append("data kurang")
    if str(r.get("sharia_status", "")).startswith(("LEWAT", "NONHALAL")):
        notes.append("rasio syariah")
    return "LAYAK" if not notes else "TIDAK LAYAK (" + ", ".join(notes) + ")"


def score(df):
    def col(name, default=np.nan):        # ambil kolom, aman jika tak ada
        return df[name] if name in df.columns else pd.Series(default, index=df.index)

    sn = CONFIG.get("sector_neutral", False) and ("sector" in df.columns)
    def R(name, higher=True):             # ranking: sektor-netral (z) atau global (persentil)
        if name not in df.columns:
            return pd.Series(50.0, index=df.index)
        return sector_zscore(df, name, higher) if sn else pct(df[name], higher)

    df["s_value"]  = (R("per", False) + R("pbv", False) + R("div_yield", True)) / 3
    df["s_quality"] = (R("roe", True) + R("net_margin", True) + R("der", False)) / 3
    df["s_growth"] = (R("rev_growth", True) + R("earn_growth", True)) / 2
    # momentum + bandarmology-lite (Chaikin Money Flow = akumulasi/distribusi)
    df["s_momentum"] = (R("ret_3m", True) + R("ret_6m", True) +
                        col("above_sma50", 0) * 100 + col("above_sma200", 0) * 100 +
                        rsi_health(col("rsi")) + pct(col("cmf"), True)) / 6
    df["s_liquidity"] = (R("market_cap", True) + R("avg_value_idr", True)) / 2

    w = CONFIG["weights"]
    df["skor"] = (df["s_value"] * w["value"] + df["s_quality"] * w["quality"] +
                  df["s_growth"] * w["growth"] + df["s_momentum"] * w["momentum"] +
                  df["s_liquidity"] * w["liquidity"])

    df["kelayakan"] = df.apply(kelayakan_row, axis=1)
    return df.sort_values("skor", ascending=False).reset_index(drop=True)

# ===== sec_stockbit =====
# ======================================================================
# LAPIS STOCKBIT (input MANUAL) — validasi silang & pertimbangan tambahan
# ----------------------------------------------------------------------
# Stockbit TIDAK punya API publik resmi; menyambung otomatis butuh kredensial,
# melanggar ToS, rapuh, & berisiko akun. Cara sah: isi manual angka yang KAMU
# lihat di akun Stockbit-mu. Kosong = dilewati (bot tetap jalan seperti biasa).
#
# Format per ticker (semua opsional):
#   "target": <harga target konsensus>,  "rating": "buy"/"add"/"hold"/"reduce"/"sell",
#   "flow":   +1 (asing akumulasi) / 0 / -1 (distribusi),
#   override fundamental (mengganti angka yfinance yg kamu ragukan):
#       "per","pbv","roe","der","debt_to_assets","nonhalal_ratio"
# ======================================================================
STOCKBIT = {
    # CONTOH — GANTI dgn angka dari Stockbit-mu, atau biarkan kosong:
    # "MEDC": {"target": 1450, "rating": "buy",  "flow": +1},
    # "ANTM": {"target": 3000, "rating": "hold", "flow": -1, "per": 10.5},
    # "MDKA": {"target": 3100, "rating": "add"},
}

_OVR_FUND = ["per", "pbv", "roe", "net_margin", "div_yield", "der", "debt_to_assets", "nonhalal_ratio"]
_RATING_TILT = {"buy": 1.0, "add": 0.7, "hold": 0.0, "reduce": -0.7, "sell": -1.0}

def _isnum(v):
    return v is not None and not (isinstance(v, float) and np.isnan(v))

def apply_stockbit(df, sb=None):
    """Terapkan input Stockbit: override + validasi silang + upside + tilt skor."""
    sb = sb if sb is not None else STOCKBIT
    for c, val in [("sb_target", np.nan), ("sb_upside", np.nan), ("sb_rating", ""),
                   ("sb_flow", np.nan), ("data_confidence", "yfinance"),
                   ("sb_tilt", 0.0)]:
        df[c] = val
    if not sb:
        return df

    for i, r in df.iterrows():
        d = sb.get(r["ticker"])
        if not d:
            continue
        # --- override fundamental + cek selisih vs yfinance (>15% => tandai) ---
        flags = []
        for k in _OVR_FUND:
            if k in d and d[k] is not None:
                old = r.get(k)
                if _isnum(old) and float(old) != 0 and abs(float(d[k]) - float(old)) / abs(float(old)) > 0.15:
                    flags.append(k)
                df.at[i, k] = d[k]
        df.at[i, "data_confidence"] = "stockbit\u2713" if not flags else "beda:" + ",".join(flags)
        # recompute status syariah bila rasio di-override
        if ("debt_to_assets" in d) or ("nonhalal_ratio" in d):
            df.at[i, "sharia_status"] = status_from_ratios(df.at[i, "debt_to_assets"],
                                                           df.at[i, "nonhalal_ratio"])
        # --- target, upside, rating, flow ---
        if _isnum(d.get("target")):
            df.at[i, "sb_target"] = d["target"]
            last = r.get("last") if _isnum(r.get("last")) else r.get("price")
            if _isnum(last) and float(last) > 0:
                df.at[i, "sb_upside"] = float(d["target"]) / float(last) - 1
        if d.get("rating"):
            df.at[i, "sb_rating"] = str(d["rating"]).lower()
        if _isnum(d.get("flow")):
            df.at[i, "sb_flow"] = d["flow"]

    # --- tilt skor dari upside + rating + flow (±8 poin) ---
    def sb_tilt(r):
        t = 0.0
        up = r.get("sb_upside")
        if _isnum(up):
            t += max(-1.0, min(1.0, up / 0.20))          # upside 20% -> +1
        t += _RATING_TILT.get(_norm_rating(r.get("sb_rating", "")), 0.0)
        fl = r.get("sb_flow")
        if _isnum(fl):
            t += 0.5 * np.sign(fl)
        return t
    df["sb_tilt"] = df.apply(sb_tilt, axis=1).clip(-2, 2) * 4.0
    df["skor"] = (df["skor"] + df["sb_tilt"]).clip(0, 100)
    # kelayakan bisa berubah bila rasio syariah di-override
    df["kelayakan"] = df.apply(kelayakan_row, axis=1)
    return df


# ----------------------------------------------------------------------
# Loader CSV: isi STOCKBIT dari file (biar tak perlu ketik dict manual)
# ----------------------------------------------------------------------
_RATING_ALIAS = {
    "strong buy": "buy", "buy": "buy", "beli": "buy",
    "overweight": "add", "outperform": "add", "accumulate": "add", "add": "add", "akumulasi": "add",
    "hold": "hold", "neutral": "hold", "tahan": "hold",
    "underweight": "reduce", "underperform": "reduce", "reduce": "reduce", "kurangi": "reduce",
    "sell": "sell", "strong sell": "sell", "jual": "sell",
}

def _norm_rating(x):
    return _RATING_ALIAS.get(str(x).strip().lower(), str(x).strip().lower())


_PCT_TO_FRAC = {"roe", "net_margin", "debt_to_assets", "nonhalal_ratio"}  # simpan sbg desimal
_PCT_KEEP    = {"div_yield"}                                              # simpan sbg persen

def _norm_num(k, v):
    v = float(v)
    if k in _PCT_TO_FRAC and abs(v) > 1.5:   # user ketik persen (mis. 19.87) -> 0.1987
        return v / 100.0
    if k in _PCT_KEEP and abs(v) <= 1.0:     # user ketik desimal (0.108) -> 10.8
        return v * 100.0
    return v

def stockbit_template(path="stockbit_template.csv", tickers=None):
    """Tulis CSV kosong berisi seluruh universe untuk kamu isi dari Stockbit."""
    tickers = tickers or CONFIG["universe"]
    cols = ["ticker", "target", "rating", "flow", "per", "pbv", "roe",
            "net_margin", "div_yield", "der", "debt_to_assets", "nonhalal_ratio"]
    tdf = pd.DataFrame({"ticker": tickers})
    for c in cols[1:]:
        tdf[c] = ""
    tdf.to_csv(path, index=False)
    return path

def load_stockbit_csv(path_or_buf, update=True):
    """Baca CSV Stockbit -> dict. Kolom wajib: 'ticker'. Sisanya opsional.
    target,per,pbv,roe,der,debt_to_assets,nonhalal_ratio (angka); rating (teks); flow (+1/0/-1)."""
    df = pd.read_csv(path_or_buf)
    df.columns = [str(c).strip().lower() for c in df.columns]
    if "ticker" not in df.columns:
        raise ValueError("CSV wajib punya kolom 'ticker'")
    numeric = ["target", "flow", "per", "pbv", "roe", "net_margin", "div_yield", "der", "debt_to_assets", "nonhalal_ratio"]
    out = {}
    for _, r in df.iterrows():
        tk = str(r.get("ticker", "")).strip().upper()
        if not tk or tk == "NAN":
            continue
        d = {}
        for k in numeric:
            if k in df.columns and pd.notna(r.get(k)) and str(r.get(k)).strip() != "":
                try:
                    d[k] = _norm_num(k, r[k])
                except Exception:
                    pass
        if "rating" in df.columns and pd.notna(r.get("rating")) and str(r.get("rating")).strip():
            d["rating"] = _norm_rating(r.get("rating"))
        if d:
            out[tk] = d
    if update:
        STOCKBIT.update(out)
    return out

# ===== sec_macro =====
# ======================================================================
# OVERLAY MAKRO — auto-fetch proksi pasar dunia + Indonesia (real-time)
# ======================================================================
MACRO_TICKERS = {
    "gold":   "GC=F",   # emas
    "silver": "SI=F",   # perak
    "copper": "HG=F",   # tembaga
    "brent":  "BZ=F",   # minyak Brent
    "gas":    "NG=F",   # gas alam
    "ihsg":   "^JKSE",  # IHSG
    "usdidr": "IDR=X",  # kurs USD/IDR
}

# Proksi untuk komoditas tanpa ticker komoditas gratis yg rapi.
# Dicoba berurutan; yg pertama berhasil dipakai. Kalau semua gagal -> read manual CONFIG.
PROXY = {
    "coal":   ["WHC.AX", "BTU"],        # Whitehaven (thermal Newcastle), Peabody
    "nickel": ["NIC.AX", "IGO.AX"],     # Nickel Industries (nikel Indonesia), IGO
    "cpo":    ["ZL=F", "AALI.JK"],      # minyak kedelai (proksi minyak nabati), Astra Agro
}

def _bias_from_trend(chg1m, above_sma50):
    if chg1m > 0.05 and above_sma50:  return 2
    if above_sma50:                   return 1
    if chg1m < -0.05:                 return -2
    if chg1m < 0:                     return -1
    return 0

def _series_bias(sym):
    try:
        h = yf.Ticker(sym).history(period="6mo")["Close"].dropna()
        if len(h) < 30:
            return None
        last = float(h.iloc[-1])
        sma50 = float(h.rolling(50).mean().iloc[-1]) if len(h) >= 50 else last
        chg1m = float(h.iloc[-1] / h.iloc[-21] - 1) if len(h) > 21 else 0.0
        return {"last": last, "chg1m": chg1m, "above_sma50": last > sma50,
                "bias": _bias_from_trend(chg1m, last > sma50), "sym": sym}
    except Exception:
        return None

def fetch_macro():
    """Ambil proksi makro live + proksi komoditas (auto-refresh nikel/batu bara/CPO)."""
    out = {}
    for k, sym in MACRO_TICKERS.items():
        d = _series_bias(sym)
        if d: out[k] = d
    prox = {}
    for theme, cands in PROXY.items():
        for sym in cands:
            d = _series_bias(sym)
            if d:
                prox[theme] = d
                break
    out["_proxy"] = prox
    return out

def theme_bias(macro):
    """Bias per-tema + regime IHSG. Komoditas: auto (proxy) bila ada, else manual."""
    man = CONFIG["macro_manual"]; prox = macro.get("_proxy", {})
    b = lambda k, d=0: macro.get(k, {}).get("bias", d)
    cm = lambda t: prox[t]["bias"] if t in prox else man.get(t, 0)   # commodity auto/manual
    tb = {
        "gold": b("gold"), "silver": b("silver"), "copper": b("copper"), "oil_gas": b("brent"),
        "petrochem": -b("brent"),
        "coal": cm("coal"), "nickel": cm("nickel"), "cpo": cm("cpo"),
        "paper": man["paper"], "poultry": man["poultry"],
    }
    ih = macro.get("ihsg", {})
    regime = ("risk_off" if (ih and not ih.get("above_sma50", True))
              else ("risk_on" if ih.get("bias", 0) >= 1 else "neutral"))
    defen = 1 if regime == "risk_off" else 0
    tb["consumer_defensive"] = defen; tb["pharma"] = defen; tb["distribution"] = 0
    for k, v in man.items():                 # tema manual lain (telco/renewable/cement/...)
        if not k.startswith("_"):
            tb.setdefault(k, v)
    return tb, regime

def ticker_macro(ticker, tb):
    themes = CONFIG["theme_map"].get(ticker, [])
    if not themes:
        return 0.0, ""
    vals = [tb.get(t, 0) for t in themes]
    return sum(vals) / len(vals), "/".join(themes)

def apply_macro(df, tb, regime):
    biases, labels = [], []
    for _, r in df.iterrows():
        a, lab = ticker_macro(r["ticker"], tb)
        biases.append(a); labels.append(lab)
    df["macro_bias"] = biases; df["theme"] = labels
    df["macro_tilt"] = df["macro_bias"].clip(-2, 2) * 5.0
    df["skor"] = (df["skor"] + df["macro_tilt"]).clip(0, 100)
    def gate(r):
        if r["macro_bias"] <= -1.5 and r["signal"] not in ("BREAKOUT",):
            return "HINDARI (makro lemah)"
        return r["signal"]
    if "signal" in df.columns:
        df["signal"] = df.apply(gate, axis=1)
    return df.sort_values("skor", ascending=False).reset_index(drop=True)


def price_filter(df, max_price=None):
    """Saring saham dgn harga < max_price (pakai 'last' jika ada, else 'price')."""
    if not max_price:
        return df.reset_index(drop=True)
    last = pd.to_numeric(df.get("last"), errors="coerce") if "last" in df.columns else pd.Series(np.nan, index=df.index)
    price = pd.to_numeric(df.get("price"), errors="coerce") if "price" in df.columns else pd.Series(np.nan, index=df.index)
    px = last.fillna(price)
    return df[px < max_price].reset_index(drop=True)

# ===== sec_alerts =====
# ======================================================================
# ALERT (buy zone / tembus SL / breakout)  +  NOTIFIKASI TELEGRAM
# ======================================================================
import urllib.request, urllib.parse, json as _json, html as _htmllib, datetime as _dt

def _n(v):
    try:
        f = float(v); return None if f != f else f
    except Exception:
        return None

def compute_alerts(df):
    """Deteksi trigger dari harga terakhir vs level timing. Return list dict."""
    c = CONFIG; out = []
    for _, r in df.iterrows():
        last = _n(r.get("last")); lo = _n(r.get("entry_lo")); hi = _n(r.get("entry_hi"))
        sl = _n(r.get("sl")); sig = str(r.get("signal", "")); tk = r["ticker"]
        if last is None:
            continue
        if c["alert_sl_break"] and sl is not None and last < sl:
            out.append({"ticker": tk, "type": "SL_BREAK", "prio": 0,
                        "msg": f"{tk} TEMBUS SL — Rp{last:,.0f} < SL Rp{sl:,.0f}. Pertimbangkan keluar/kurangi."})
        elif (c["alert_buy_zone"] and lo is not None and hi is not None and lo <= last <= hi
              and not sig.startswith(("HINDARI", "TUNGGU", "NETRAL"))):
            out.append({"ticker": tk, "type": "BUY_ZONE", "prio": 1,
                        "msg": f"{tk} MASUK AREA BELI — Rp{last:,.0f} (zona Rp{lo:,.0f}–Rp{hi:,.0f}) · {sig}. "
                               f"TP {r.get('tp1',0):,.0f}/{r.get('tp2',0):,.0f}/{r.get('tp3',0):,.0f} · SL Rp{sl:,.0f}"})
        elif c["alert_breakout"] and sig == "BREAKOUT" and lo is not None and last >= lo:
            out.append({"ticker": tk, "type": "BREAKOUT", "prio": 2,
                        "msg": f"{tk} BREAKOUT — Rp{last:,.0f} ≥ Rp{lo:,.0f}. SL Rp{sl:,.0f} bila gagal."})
    out.sort(key=lambda x: x["prio"])
    return out

_ICON = {"SL_BREAK": "🔴", "BUY_ZONE": "🟢", "BREAKOUT": "🔵"}

def format_telegram(df, macro, regime, alerts, top_n=5):
    """Susun pesan HTML ringkas utk Telegram (<4096 char)."""
    ih = macro.get("ihsg", {}).get("last")
    reg = {"risk_off": "RISK-OFF", "risk_on": "RISK-ON"}.get(regime, "NETRAL")
    lines = [f"<b>📊 ZF Saham Syariah</b> — {_dt.datetime.now():%d %b %Y %H:%M}",
             f"IHSG {ih:,.0f} · <b>{reg}</b>" if ih else f"Regime <b>{reg}</b>", ""]
    if alerts:
        lines.append("<b>⚡ Trigger:</b>")
        for a in alerts:
            lines.append(f"{_ICON.get(a['type'],'•')} {_htmllib.escape(a['msg'])}")
        lines.append("")
    else:
        lines.append("Tidak ada trigger area-beli/SL saat ini.\n")
    lines.append("<b>🏆 Peringkat teratas:</b>")
    for _, r in df.head(top_n).iterrows():
        lines.append(f"{r['rank']}. <b>{r['ticker']}</b> skor {r['skor']:.0f} · "
                     f"{_htmllib.escape(str(r.get('signal','')))}")
    lines.append("\n<i>Bukan nasihat keuangan. Eksekusi manual di Bibit.</i>")
    msg = "\n".join(lines)
    return msg[:4000]

def send_telegram(text, token, chat_id, parse_mode=None):
    """Kirim pesan via Bot API. Return (ok, info). Token TIDAK dicetak."""
    if not token or not chat_id:
        return False, "token/chat_id kosong"
    parse_mode = parse_mode or CONFIG.get("telegram_parse", "HTML")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id, "text": text,
        "parse_mode": parse_mode, "disable_web_page_preview": "true",
    }).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=20) as resp:
            j = _json.loads(resp.read().decode())
            return bool(j.get("ok")), ("terkirim" if j.get("ok") else str(j))
    except Exception as e:
        return False, f"gagal: {e}"

# ===== sec_news =====
# ======================================================================
# ANALISA BERITA & OUTLOOK 100 HARI (AI)  — snapshot 31 Jul 2026
# Disintesis dari berita valid yg beredar. Bukan ramalan pasti.
# "char": bullish / netral / hati-hati / campuran ; kosong = tak ada dasar berita.
# ======================================================================
NEWS_ASOF = "31 Jul 2026"

NEWS_NARRATIVE = [
 ("Global & The Fed",
  "The Fed menahan bunga di <b>3,50\u20133,75%</b> (30 Jul), namun 9-3 dengan <b>tiga pembelot minta NAIK</b> \u2014 sikap hawkish; "
  "pasar memperkirakan 1\u20132 kenaikan hingga akhir 2026, dipicu inflasi energi & tarif. "
  "Implikasi 100 hari: dolar cenderung kuat, biaya modal mahal (<i>higher-for-longer</i>) \u2192 menekan valuasi tinggi, properti, "
  "& emiten berutang besar; menguntungkan saham value, dividen tinggi, dan eksportir komoditas (rupiah lemah bantu margin)."),
 ("Geopolitik & energi",
  "Timur Tengah (AS\u2013Iran): gencatan Juni sempat membuka Selat Hormuz & menurunkan minyak ke ~$70, tetapi <b>eskalasi akhir Juli</b> "
  "mendorong Brent ke ~$88 lagi. Proyeksi 100 hari bias <b>turun ($70\u201382)</b> karena OPEC+ menambah pasokan \u2014 kecuali eskalasi berulang. "
  "Emas tetap dapat <i>safe-haven bid</i>; gangguan LNG di Hormuz menopang batu bara (permintaan Jepang/Korea)."),
 ("Indonesia & IHSG",
  "IHSG babak belur di H1 (\u221231% YtD, asing keluar ~Rp72 T, valuasi ~<b>9x PE</b> \u2014 sangat terkompresi). Muncul sinyal <b>bottoming</b>: "
  "broker (CGSI) menargetkan ~<b>7.000</b> akhir 2026 (~+12%) bila rupiah stabil (BI lebih agresif). "
  "Risiko: Fed hawkish, rupiah (Rp16.800\u201317.500), harga minyak (beban subsidi), & evaluasi <b>MSCI November</b> (bobot RI turun ke ~0,4%). "
  "Pergerakan volatil & tidak linier; defensif + dividen tinggi relatif aman."),
 ("Komoditas \u00b7 100 hari",
  "<b>Emas</b>: konsolidasi ~$4.100, bias naik (bank sentral beli). <b>Perak</b>: defisit struktural, diperkirakan outperform emas (volatil). "
  "<b>Tembaga</b>: struktural bullish (transisi energi + AI). <b>Nikel</b>: range $16\u201318rb, bias membaik (disiplin pasokan Indonesia). "
  "<b>Batu bara</b>: ~$125\u2013135, dividen tinggi menarik. <b>CPO</b>: firm RM4.400\u20134.700 (mandat B50 + risiko El Ni\u00f1o)."),
]

# Outlook per saham (hanya yg punya dasar berita/tema; sisanya kosong)
OUTLOOK = {
 # Batu bara
 "AADI": ("netral", "Batu bara $125\u2013135 + dividen ~10%; topangan LNG Hormuz, tertahan permintaan China."),
 "ADRO": ("netral", "Coal + top pick Mirae S2-2026; dividen ~10%; volatil ikut geopolitik energi."),
 "BSSR": ("netral", "Coal, dividen tinggi; likuiditas tipis \u2014 waspada eksekusi."),
 "ITMG": ("netral", "Coal, dividen tinggi; margin terbantu rupiah lemah."),
 "PTBA": ("netral", "Coal domestik + dividen; permintaan PLN relatif stabil."),
 # Logam mulia / metals
 "ANTM": ("campuran", "Emas (konsolidasi, bias naik) + nikel (range, bias membaik) + perak; net konstruktif."),
 "MDKA": ("bullish", "Tembaga (struktural bullish: transisi energi+AI) + emas; volatil, PER TTM negatif (rugi)."),
 "HRTA": ("netral", "Emas perhiasan; ikut harga emas + permintaan konsumen."),
 "ARCI": ("bullish", "Emas + PERAK (defisit struktural, outperform emas); spekulatif/volatil."),
 "BRMS": ("campuran", "Emas+perak, prospek besar tapi spekulatif/fase pengembangan \u2014 hati-hati risiko."),
 "PSAB": ("hati-hati", "Emas; likuiditas tipis, spekulatif."),
 "TINS": ("netral", "Timah; margin kuat (24,5%), rating analis Beli; ikut harga timah global."),
 # Nikel
 "MBMA": ("netral", "Nikel battery-grade; bias membaik (disiplin pasokan+Hormuz), tapi glut NPI membatasi; valuasi mahal (PER 52)."),
 # Migas & petrokimia
 "MEDC": ("campuran", "Migas; premium jangka pendek (eskalasi Juli) tapi forecast bias turun $70\u201382 akhir tahun (OPEC+)."),
 "PGAS": ("netral", "Gas; relatif stabil + dividen; mengikuti harga energi."),
 "ELSA": ("campuran", "Jasa migas; ikut belanja modal energi & harga minyak (volatil)."),
 "TPIA": ("campuran", "Petrokimia; PER TTM 98 (mahal). Margin membaik bila minyak turun, tapi permintaan lemah."),
 # CPO
 "LSIP": ("netral", "CPO firm RM4.400\u20134.700 (mandat B50 + El Ni\u00f1o); analis Overweight sawit."),
 "DSNG": ("netral", "CPO; ditopang mandat B50 + risiko El Ni\u00f1o."),
 # Konsumsi & farmasi (defensif)
 "INDF": ("netral", "Konsumsi defensif; tahan saat risk-off; rating Beli (target +21%)."),
 "CMRY": ("netral", "Konsumsi (dairy); top pick Mirae; premium defensif saat risk-off."),
 "MYOR": ("netral", "Konsumsi; defensif; likuiditas tipis di sesi tsb."),
 "JPFA": ("netral", "Unggas + top pick Mirae; rupiah lemah = beban pakan impor (jagung/soybean)."),
 "KLBF": ("netral", "Farmasi defensif; tahan siklus."),
 "SIDO": ("netral", "Herbal, ROE tinggi + dividen ~10%; ekspor; defensif."),
 # Distribusi / ritel / otomotif
 "AKRA": ("netral", "Distribusi BBM + kawasan industri (JIIPE); relatif resilient."),
 "ERAA": ("netral", "Ritel elektronik; sensitif daya beli & suku bunga tinggi."),
 "MAPA": ("netral", "Ritel sport; sensitif daya beli."),
 "AUTO": ("netral", "Komponen otomotif; DER sangat rendah + dividen; sensitif penjualan kendaraan."),
 # Properti / infrastruktur (tertekan bunga tinggi)
 "CTRA": ("hati-hati", "Properti; suku bunga tinggi (higher-for-longer) menekan KPR & permintaan."),
 "JSMR": ("hati-hati", "Tol; utang tinggi + suku bunga tinggi = beban bunga naik."),
 # Kertas
 "INKP": ("netral", "Kertas/pulp + top pick Mirae; siklikal global; rating Beli (target +66%)."),
 # ASGR: tak ada dasar berita spesifik -> kosong (tidak ada)
}

# ===== sec_news_live =====
# ======================================================================
# BERITA LIVE (tiap run) — Google News RSS (gratis) + Gemini (AI outlook)
# + SARAN beli/jual deterministik yg ikut ter-update tiap run.
# Tanpa GEMINI_API_KEY -> fallback ke snapshot statis (sec_news).
# ======================================================================
import urllib.request, urllib.parse, json as _json, os as _os
import xml.etree.ElementTree as _ET, datetime as _dt2

NEWS_QUERIES = {
    "makro_global": "Federal Reserve suku bunga rate decision",
    "geopolitik":   "Timur Tengah minyak Brent Selat Hormuz",
    "ihsg":         "IHSG prospek rupiah",
    "emas":         "harga emas gold price outlook",
    "perak":        "harga perak silver price",
    "nikel":        "harga nikel Indonesia nickel",
    "batubara":     "harga batu bara coal Newcastle",
    "cpo":          "harga CPO sawit biodiesel B50",
    "tembaga":      "harga tembaga copper price",
}

def fetch_news_rss(query, n=5, lang="id", country="ID"):
    """Judul berita terbaru via Google News RSS (tanpa API key)."""
    url = ("https://news.google.com/rss/search?q=" + urllib.parse.quote(query)
           + f"&hl={lang}&gl={country}&ceid={country}:{lang}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            root = _ET.fromstring(r.read())
        return [it.findtext("title") for it in root.findall(".//item")[:n] if it.findtext("title")]
    except Exception:
        return []

def gather_news(per=3):
    return {k: fetch_news_rss(q, per) for k, q in NEWS_QUERIES.items()}

def gemini_outlook(news, universe, theme_map, api_key=None, model=None):
    """Gemini menyusun narasi + outlook per saham (JSON). Return (narrative, outlook) atau (None, None)."""
    api_key = api_key or _os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None, None
    model = model or (CONFIG.get("gemini_model") if "CONFIG" in globals() else None) or "gemini-2.0-flash"
    news_txt = ""
    for k, items in news.items():
        if items:
            news_txt += f"\n[{k}]\n" + "\n".join(f"- {t}" for t in items[:3])
    prompt = (
        "Kamu analis pasar saham Indonesia. Dari HEADLINE berita terbaru di bawah, buat penilaian horizon ~100 hari.\n"
        "Balas HANYA JSON valid (tanpa teks lain) dengan bentuk:\n"
        '{"narrative":{"global_fed":"..","geopolitik":"..","indonesia":"..","komoditas":".."},'
        '"outlook":{"TICKER":{"char":"bullish|netral|hati-hati|campuran","note":"<=140 char alasan berbasis berita"}}}\n'
        "Aturan: narrative tiap poin 1-2 kalimat Bahasa Indonesia. Untuk outlook, nilai TIAP ticker berikut; "
        "jika tak ada dasar berita untuk sebuah ticker, JANGAN sertakan ticker itu.\n"
        f"TICKER: {', '.join(universe)}\n"
        f"TEMA per ticker: {_json.dumps(theme_map, ensure_ascii=False)}\n"
        f"HEADLINE:{news_txt}\n"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    body = _json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.3, "response_mime_type": "application/json"}}).encode()
    import time as _time, random as _random, urllib.error as _uerr
    last_err = ""
    for attempt in range(3):                        # retry 429/503 dgn backoff
        try:
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                resp = _json.loads(r.read())
            txt = resp["candidates"][0]["content"]["parts"][0]["text"]
            data = _json.loads(txt)
            nar = data.get("narrative", {})
            narrative = [("Global & The Fed", nar.get("global_fed", "")),
                         ("Geopolitik & energi", nar.get("geopolitik", "")),
                         ("Indonesia & IHSG", nar.get("indonesia", "")),
                         ("Komoditas \u00b7 100 hari", nar.get("komoditas", ""))]
            outlook = {}
            for tk, o in (data.get("outlook", {}) or {}).items():
                if o and o.get("char"):
                    outlook[str(tk).upper()] = (o["char"], o.get("note", ""))
            if any(t for _, t in narrative) or outlook:
                return narrative, outlook
            return None, None
        except _uerr.HTTPError as e:
            last_err = f"HTTP {e.code} ({'kuota/rate-limit' if e.code == 429 else e.reason})"
            if e.code in (429, 503) and attempt < 2:
                wait = (2 ** attempt) * 6 + _random.uniform(0, 3)   # ~6-9s, ~15-18s
                print(f"  (Gemini {e.code}, tunggu {wait:.0f}s lalu coba lagi...)")
                _time.sleep(wait); continue
            break
        except Exception as e:
            last_err = str(e); break
    print("  (Gemini gagal, pakai snapshot):", last_err)
    return None, None

def build_live_news(universe, theme_map):
    """Cari berita + minta Gemini. Set global NEWS_NARRATIVE/OUTLOOK/NEWS_ASOF. Return True bila LIVE."""
    global NEWS_NARRATIVE, OUTLOOK, NEWS_ASOF
    _static_asof = "31 Jul 2026"
    news = gather_news()
    nar, out = gemini_outlook(news, universe, theme_map)
    today = _dt2.date.today().strftime("%d %b %Y")
    if nar and out:
        NEWS_NARRATIVE = nar
        OUTLOOK = out
        NEWS_ASOF = today + " (live AI)"
        return True
    NEWS_ASOF = _static_asof + " (snapshot)"      # NEWS_NARRATIVE/OUTLOOK tetap statis
    return False

# ---------------------------------------------------------------
# SARAN beli/jual (deterministik) — fusi sinyal + fundamental + berita
# ---------------------------------------------------------------
def recommendation(r):
    if str(r.get("kelayakan", "")) != "LAYAK":
        return "HINDARI"
    sig = str(r.get("signal", ""))
    if sig.startswith("HINDARI"):
        return "HINDARI"
    sc = 0
    if sig.startswith("BUY ZONE") or sig == "BREAKOUT": sc += 2
    elif sig.startswith("TREND"):                        sc += 1
    char = None
    if "OUTLOOK" in globals():
        o = OUTLOOK.get(r["ticker"])
        if o: char = o[0]
    if char == "bullish":     sc += 1
    elif char == "hati-hati": sc -= 1
    rating = str(r.get("sb_rating", ""))
    if rating in ("buy", "add"):     sc += 1
    elif rating in ("sell", "reduce"): sc -= 1
    up = r.get("sb_upside")
    if _isnum(up):
        if up >= 0.20: sc += 1
        elif up < 0:   sc -= 1
    if sc >= 3:  return "BELI"
    if sc >= 1:  return "TAHAN"
    if sc <= -1: return "KURANGI"
    return "AMATI"

def add_recommendations(df):
    df["saran"] = df.apply(recommendation, axis=1)
    return df

# ===== sec_pro =====
# ======================================================================
# UPGRADE PROFESIONAL — position sizing berbasis risiko + konfluensi sinyal
# ======================================================================
def _n(v):
    try:
        f = float(v); return None if f != f else f
    except Exception:
        return None

def add_position_sizing(df, config=None):
    """Hitung lot berdasarkan manajemen risiko: risiko/trade tetap % dari modal.
    1 lot = 100 lembar. lot = floor( (modal*risk%) / (jarak_entry_SL * 100) )."""
    config = config or CONFIG
    acct = float(config.get("account_size", 100_000_000))
    riskpct = float(config.get("risk_per_trade_pct", 0.01))
    budget = acct * riskpct
    lots, risks = [], []
    for _, r in df.iterrows():
        entry = _n(r.get("entry_hi")) or _n(r.get("last")) or _n(r.get("price"))
        sl = _n(r.get("sl"))
        if not entry or not sl or entry <= sl:
            lots.append(0); risks.append(0.0); continue
        rps = entry - sl                       # risiko per lembar
        lot = int(budget // (rps * 100))       # 100 lembar / lot
        lots.append(max(lot, 0)); risks.append(rps * 100 * max(lot, 0))
    df["lot"] = lots
    df["risk_rp"] = risks
    return df

def confluence(r):
    """Berapa sinyal INDEPENDEN yang sepakat (0..5). Ini 'keyakinan', bukan probabilitas terkalibrasi."""
    n = 0
    if str(r.get("signal", "")).startswith(("BUY ZONE", "BREAKOUT", "TREND")):
        n += 1                                                   # teknikal
    if (_n(r.get("s_value")) or 0) >= 55 and (_n(r.get("s_quality")) or 0) >= 50:
        n += 1                                                   # fundamental (murah + berkualitas)
    cmf, flow = _n(r.get("cmf")), _n(r.get("sb_flow"))
    if (cmf is not None and cmf > 0.02) or (flow is not None and flow > 0):
        n += 1                                                   # akumulasi (bandarmology)
    if str(r.get("sb_rating", "")) in ("buy", "add") and (_n(r.get("sb_upside")) or 0) > 0.15:
        n += 1                                                   # analis + upside
    o = OUTLOOK.get(r["ticker"]) if "OUTLOOK" in globals() else None
    if o and o[0] == "bullish":
        n += 1                                                   # berita
    return n

def add_confluence(df):
    df["konfluensi"] = df.apply(confluence, axis=1)
    return df

# ===== sec_render =====
# ======================================================================
# RENDER DASHBOARD HTML  (makro real-time + timing beli/jual, scoped #zfx)
# ======================================================================
import datetime as _dt

def _num(v):
    try:
        if v is None: return None
        f = float(v)
        return None if (f != f) else f
    except Exception:
        return None

def _f(v, dec=2, dash="\u2014"):
    x = _num(v); return dash if x is None else f"{x:,.{dec}f}"

def _rp(v, dash="\u2014"):
    x = _num(v); return dash if x is None else f"Rp{x:,.0f}"

def _pctf(v, dec=1, dash="\u2014"):
    x = _num(v); return dash if x is None else f"{x*100:.{dec}f}%"

def _clip(v, lo=0, hi=100):
    x = _num(v); return lo if x is None else max(lo, min(hi, x))

def _score_color(v):
    if v >= 66: return "#0C7A5B"
    if v >= 45: return "#128C74"
    if v >= 30: return "#B4832B"
    return "#9E3B3E"

def _meter(v, tilt=None):
    x = _clip(v)
    t = ""
    if tilt is not None and _num(tilt) not in (None, 0):
        sgn = "+" if tilt > 0 else ""
        col = "#0C7A5B" if tilt > 0 else "#9E3B3E"
        t = f'<span class="zfx-tilt" style="color:{col}">{sgn}{tilt:.0f} makro</span>'
    return (f'<div class="zfx-meter"><div class="zfx-track">'
            f'<div class="zfx-fill" style="width:{x:.0f}%;background:{_score_color(x)}"></div>'
            f'</div><span class="zfx-mv">{x:.1f}</span></div>{t}')

def _spill(status):
    s = str(status)
    if s.startswith("SYARIAH OK"): cls, txt = "ok", "Syariah OK"
    elif s.startswith("OK (waspada"): cls, txt = "warn", s.replace("OK (waspada, ", "Waspada ").rstrip(")")
    elif s.startswith("LEWAT"):     cls, txt = "bad", s.replace("LEWAT BATAS UTANG ", "Utang ").strip("()")
    elif s.startswith("NONHALAL"):  cls, txt = "bad", s.replace("NONHALAL >5% ", "Nonhalal ").strip("()")
    else:                            cls, txt = "chk", "Perlu cek"
    return f'<span class="zfx-pill zfx-{cls}"><i></i>{txt}</span>'

_SIG = {
    "BUY ZONE":            ("buy",  "Buy zone"),
    "TREND (tahan/add)":   ("trend", "Trend \u00b7 add"),
    "BREAKOUT":            ("brk",  "Breakout"),
    "TUNGGU PULLBACK":     ("wait", "Tunggu pullback"),
    "NETRAL / AMATI":      ("neu",  "Amati"),
}
def _sigpill(sig):
    s = str(sig)
    if s in _SIG: cls, txt = _SIG[s]
    elif s.startswith("HINDARI"): cls, txt = "avd", ("Hindari \u00b7 makro" if "makro" in s else "Hindari")
    else: cls, txt = "neu", s
    return f'<span class="zfx-sig zfx-s-{cls}">{txt}</span>'

def _mchip(label, val, bias, sub=""):
    if bias is None: col, arr, cls = "#6D6A5E", "\u2192", "n"
    elif bias >= 1:  col, arr, cls = "#0C7A5B", "\u2197", "u"
    elif bias <= -1: col, arr, cls = "#9E3B3E", "\u2198", "d"
    else:            col, arr, cls = "#6D6A5E", "\u2192", "n"
    return (f'<div class="zfx-chip zfx-c-{cls}"><span class="cl">{label}</span>'
            f'<span class="cv">{val} <b style="color:{col}">{arr}</b></span>'
            f'<span class="cs">{sub}</span></div>')

def _sb_cell(r):
    up = _num(r.get("sb_upside")); rt = str(r.get("sb_rating") or "")
    conf = str(r.get("data_confidence") or "")
    if up is None and not rt:
        return '<span class="zfx-mut">\u2014</span>'
    parts = []
    if up is not None:
        col = "#0C7A5B" if up >= 0 else "#9E3B3E"
        parts.append(f'<span class="zfx-n" style="color:{col};font-weight:600">{up*100:+.0f}%</span>')
    if rt:
        rc = {"buy": "ok", "add": "ok", "hold": "chk", "reduce": "bad", "sell": "bad"}.get(rt, "chk")
        parts.append(f'<span class="zfx-pill zfx-{rc}" style="padding:1px 7px"><i></i>{rt}</span>')
    sub = f'<div class="zfx-th" style="color:#B4832B">{conf}</div>' if (conf and conf not in ("yfinance",)) else ""
    return " ".join(parts) + sub

def _guide_section(config):
    if not config.get("show_guide", True):
        return ""
    steps = [
        ("1", "Pilih saham",
         'Cari baris dengan <b>Saran AI = BELI</b> dan titik konfluensi banyak (\u25cf\u25cf\u25cf\u25cf\u25cb). '
         'Pastikan <b>Status syariah = Syariah OK</b> (hijau) dan <b>Sinyal = Buy zone</b> (harga sedang di area beli, bukan \u201cTunggu pullback\u201d).'),
        ("2", "Tentukan masuk & ukuran",
         'Beli di rentang <b>Area beli</b>, sebanyak angka <b>Sizing (lot)</b>. '
         'Lot sudah dihitung agar rugi maksimalmu \u2248 1% modal (atur modal di CONFIG). Jangan kejar harga yang sudah lari jauh.'),
        ("3", "Kelola risiko & profit",
         'Pasang <b>Stop loss</b> \u2014 jual/kurangi bila harga <b>tutup</b> di bawahnya. '
         'Ambil untung bertahap di <b>TP1 \u00b7 TP2 \u00b7 TP3</b>. Setelah TP1, geser SL ke titik impas (breakeven).'),
    ]
    steps_html = "".join(
        f'<div class="zfx-step"><span class="zfx-stepn">{n}</span>'
        f'<div><b class="zfx-steph">{h}</b><p>{t}</p></div></div>' for n, h, t in steps)

    legend = [
        ("\u25cf\u25cf\u25cf\u25cb\u25cb", "Konfluensi \u2014 berapa dari 5 sinyal sepakat (teknikal, fundamental, akumulasi, analis, berita). Makin banyak makin kuat."),
        ("Hijau / Kuning / Merah", "Pill: hijau = bagus, kuning = waspada, merah = hindari."),
        ("\u2197 / \u2198", "Di strip komoditas: hijau naik / merah turun."),
        ("\u2605 baris hijau", "Pilihan otomatis \u2014 Saran BELI dengan konfluensi \u22654 (kualifikasi tertinggi)."),
    ]
    legend_html = "".join(f'<div class="zfx-lg"><span class="zfx-lgk">{k}</span><span>{v}</span></div>' for k, v in legend)

    cols = [
        ("Skor", "Nilai gabungan 0\u2013100 dibanding saham lain di sektornya. Meter + tag \u201c+/\u2212 makro\u201d menunjukkan arah geseran kondisi pasar."),
        ("Saran AI", "Rekomendasi aksi (BELI/TAHAN/KURANGI/HINDARI/AMATI) hasil fusi semua sinyal. Ter-update tiap run."),
        ("Sinyal", "Posisi teknikal harga: Buy zone / Trend / Breakout / Tunggu pullback / Hindari."),
        ("Area beli", "Rentang harga yang wajar untuk masuk (pullback ke EMA-50 atau breakout resistance)."),
        ("Stop loss", "Batas rugi \u2014 titik keluar bila skenario salah. Kunci disiplin."),
        ("Sizing", "Jumlah lot berbasis risiko: rugi rupiah dijaga tetap ~1% modal berapa pun harga sahamnya."),
        ("TP1\u00b7TP2\u00b7TP3", "Target ambil-untung bertahap (kelipatan risiko 2R\u00b74R\u00b76R)."),
        ("Stockbit", "Upside % ke target analis + rating (dari input Bibit-mu). Flag \u201cbeda:x\u201d = angka Bibit \u2260 yfinance."),
        ("Outlook 100h", "Arah ~100 hari dari analisa berita AI. Arahkan kursor untuk melihat alasannya."),
        ("Status syariah", "Kepatuhan syariah: Syariah OK / Waspada / Lewat batas / Perlu cek."),
    ]
    cols_html = "".join(f'<div class="zfx-dc"><b>{k}</b><span>{v}</span></div>' for k, v in cols)

    return (
        '<details class="zfx-guide" open>'
        '<summary>\U0001f4d6 Cara Pakai \u2014 panduan singkat (klik untuk buka/tutup)</summary>'
        '<div class="zfx-gbody">'
        '<p class="zfx-gintro">Bot ini <b>memeringkat saham syariah</b> dan memberi <b>sinyal beli/jual</b> + kondisi pasar &amp; berita. '
        'Semua eksekusi tetap <b>manual di Bibit</b>. Ikuti 3 langkah:</p>'
        '<div class="zfx-steps">' + steps_html + '</div>'
        '<div class="zfx-gsub">Arti warna &amp; simbol</div><div class="zfx-lgwrap">' + legend_html + '</div>'
        '<div class="zfx-gsub">Kamus kolom</div><div class="zfx-dcs">' + cols_html + '</div>'
        '<div class="zfx-ging">\u26a0\ufe0f <b>Ingat:</b> ini alat bantu, <b>bukan jaminan</b>. Yang paling menentukan hasil jangka panjang '
        'adalah <b>disiplin Stop loss &amp; ukuran lot</b>, bukan menebak arah. Bukan nasihat keuangan.</div>'
        '</div></details>')

def _charts_section(config):
    if not config.get("show_charts", True):
        return ""
    specs = [("Emas \u00b7 XAU/USD", "OANDA:XAUUSD"),
             ("Perak \u00b7 XAG/USD", "OANDA:XAGUSD"),
             ("Nikel \u00b7 MCX", "MCX:NICKEL1!"),
             ("Minyak Brent", "TVC:UKOIL")]
    cards = ""
    for label, sym in specs:
        cfg = ('{"symbol":"%s","width":"100%%","height":168,"locale":"id",'
               '"dateRange":"3M","colorTheme":"light","isTransparent":true,'
               '"autosize":false,"chartOnly":false}') % sym
        cards += ('<div class="zfx-chart"><div class="zfx-chart-h">' + label + '</div>'
                  '<div class="tradingview-widget-container">'
                  '<div class="tradingview-widget-container__widget"></div>'
                  '<script type="text/javascript" '
                  'src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" '
                  'async>' + cfg + '</script></div></div>')
    return ('<div class="zfx-eyebrow">Grafik komoditas realtime</div>'
            '<div class="zfx-charts">' + cards + '</div>'
            '<div class="zfx-chartnote">Grafik hidup saat HTML dibuka di browser / GitHub Pages '
            '(di dalam Colab bisa jadi tak tampil karena batasan skrip). Sumber: TradingView, harga dapat tertunda.</div>')


def _outlook_pill(tk):
    o = OUTLOOK.get(tk) if "OUTLOOK" in globals() else None
    if not o:
        return '<span class="zfx-mut">\u2014</span>'
    char, note = o
    cls = {"bullish": "ok", "netral": "chk", "hati-hati": "warn", "campuran": "brk2"}.get(char, "chk")
    lbl = {"bullish": "Bullish", "netral": "Netral", "hati-hati": "Hati-hati", "campuran": "Campuran"}.get(char, char)
    note_esc = str(note).replace('"', "&quot;")
    return f'<span class="zfx-pill zfx-{cls}" title="{note_esc}"><i></i>{lbl}</span>'

def _saran_pill(r):
    v = str(r.get("saran", ""))
    if not v:
        return '<span class="zfx-mut">\u2014</span>'
    cls = {"BELI": "buy", "TAHAN": "trend", "AMATI": "neu", "KURANGI": "wait", "HINDARI": "avd"}.get(v, "neu")
    k = r.get("konfluensi")
    dots = ""
    if _num(k) is not None:
        k = int(k)
        dots = ('<div class="zfx-conf" title="Konfluensi ' + str(k) + '/5 sinyal sepakat">'
                + '\u25cf' * k + '<span class="zfx-conf-o">' + '\u25cb' * (5 - k) + '</span></div>')
    return f'<span class="zfx-sig zfx-s-{cls}">{v}</span>{dots}'

def _sizing_cell(r):
    lot = _num(r.get("lot")); risk = _num(r.get("risk_rp"))
    if not lot:
        return '<span class="zfx-mut">\u2014</span>'
    rr = f'Rp{risk/1000:,.0f}rb' if risk else ""
    return f'<span class="zfx-n" style="font-weight:600">{int(lot)} lot</span><div class="zfx-th">risiko {rr}</div>'

def _news_section():
    if "NEWS_NARRATIVE" not in globals():
        return ""
    cards = ""
    for title, text in NEWS_NARRATIVE:
        cards += f'<div class="zfx-newscard"><h4>{title}</h4><p>{text}</p></div>'
    return ('<div class="zfx-eyebrow">Analisa berita &amp; outlook 100 hari (AI) \u00b7 per ' + NEWS_ASOF + '</div>'
            '<div class="zfx-news">' + cards + '</div>'
            '<div class="zfx-chartnote">Sintesis AI dari berita valid per ' + NEWS_ASOF + ' \u2014 <b>snapshot, bukan ramalan pasti</b>; '
            'kondisi bisa berubah. Kolom \u201cOutlook 100h\u201d di tabel: arahkan kursor untuk alasan tiap saham. Bukan nasihat keuangan.</div>')

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');
#zfx *{box-sizing:border-box;margin:0;padding:0}
#zfx{font-family:'Inter',system-ui,sans-serif;color:#1C2621;background:#F6F4ED;border-radius:14px;
  overflow:hidden;max-width:1180px;margin:0 auto;border:1px solid #E4DFD2;box-shadow:0 8px 30px rgba(16,32,27,.08);line-height:1.45}
#zfx .zfx-n{font-family:'IBM Plex Mono',monospace}
#zfx .zfx-head{position:relative;background:#10201B;color:#EDECE3;padding:24px 30px 20px;overflow:hidden}
#zfx .zfx-head:before{content:"";position:absolute;inset:0;opacity:.13;
  background:repeating-linear-gradient(30deg,transparent 0 13px,#3d6b57 13px 14px),repeating-linear-gradient(-30deg,transparent 0 13px,#3d6b57 13px 14px)}
#zfx .zfx-head>*{position:relative}
#zfx .zfx-brand{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#7FCBB2;margin-bottom:7px}
#zfx h1{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:26px;letter-spacing:-.5px}
#zfx .zfx-sub{color:#A9B7AE;font-size:13px;margin-top:5px;max-width:660px}
#zfx .zfx-badges{position:absolute;top:24px;right:30px;display:flex;flex-direction:column;gap:6px;align-items:flex-end}
#zfx .zfx-badge{font-family:'IBM Plex Mono',monospace;font-size:10.5px;background:rgba(127,203,178,.14);border:1px solid rgba(127,203,178,.35);color:#B8E6D6;padding:4px 9px;border-radius:20px}
/* macro strip */
#zfx .zfx-macro{background:#17302A;padding:12px 22px;display:flex;gap:9px;flex-wrap:wrap;align-items:stretch;border-bottom:1px solid #244037}
#zfx .zfx-chip{background:#1F3A32;border:1px solid #2C4B41;border-radius:9px;padding:7px 11px;min-width:104px}
#zfx .zfx-chip .cl{display:block;font-size:9.5px;letter-spacing:.8px;text-transform:uppercase;color:#8FB3A6}
#zfx .zfx-chip .cv{display:block;font-family:'IBM Plex Mono',monospace;font-size:13px;color:#EDECE3;margin-top:2px;font-weight:500}
#zfx .zfx-chip .cs{display:block;font-size:9.5px;color:#6E9184;margin-top:1px}
#zfx .zfx-regime{margin-left:auto;display:flex;align-items:center;gap:8px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:#C9D6CD}
#zfx .zfx-reg-pill{padding:4px 11px;border-radius:20px;font-weight:600;letter-spacing:.5px}
#zfx .reg-off{background:#3a1e1f;color:#E79A9C;border:1px solid #5a2e2f}
#zfx .reg-neu{background:#2a2a1e;color:#D8C98A;border:1px solid #4a4630}
#zfx .reg-on{background:#173a2c;color:#7FCBB2;border:1px solid #275542}
/* kpi */
#zfx .zfx-kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:#E4DFD2;border-bottom:1px solid #E4DFD2}
#zfx .zfx-kpi{background:#FBFAF5;padding:14px 18px}
#zfx .zfx-kpi .l{font-size:10px;letter-spacing:1.1px;text-transform:uppercase;color:#8A8776}
#zfx .zfx-kpi .v{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:600;margin-top:3px;color:#10201B}
#zfx .zfx-kpi .s{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:#6D6A5E;margin-top:1px}
#zfx .zfx-body{padding:20px 30px 8px}
#zfx .zfx-eyebrow{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#0C7A5B;margin:18px 0 10px;display:flex;align-items:center;gap:9px}
#zfx .zfx-eyebrow:before{content:"";width:16px;height:2px;background:#0C7A5B}
#zfx .zfx-panels{display:grid;grid-template-columns:1fr 1fr;gap:16px}
#zfx .zfx-panel{background:#FFF;border:1px solid #E9E4D8;border-radius:10px;padding:15px 17px}
#zfx .zfx-panel h3{font-family:'Space Grotesk',sans-serif;font-size:13.5px;margin-bottom:8px;color:#10201B}
#zfx .zfx-panel p,#zfx .zfx-panel li{font-size:12.4px;color:#4A4E45}
#zfx .zfx-legend{display:flex;flex-wrap:wrap;gap:7px;margin-top:4px}
#zfx table{width:100%;border-collapse:collapse;font-size:12.5px;min-width:1040px}
#zfx .zfx-tablewrap{overflow-x:auto;border:1px solid #E9E4D8;border-radius:10px;margin-top:4px}
#zfx thead th{background:#10201B;color:#C9D6CD;font-family:'IBM Plex Mono',monospace;font-weight:500;font-size:10px;letter-spacing:.5px;text-transform:uppercase;padding:10px 11px;text-align:left;white-space:nowrap}
#zfx tbody td{padding:10px 11px;border-bottom:1px solid #EFEBE0;vertical-align:middle;white-space:nowrap}
#zfx tbody tr:nth-child(even){background:#FBFAF5}
#zfx tbody tr:hover{background:#F1F6F3}
#zfx tbody tr.zfx-top td{background:#F3F8F5}
#zfx .zfx-rk{font-family:'Space Grotesk',sans-serif;font-weight:700;color:#10201B;width:30px}
#zfx tr.zfx-top .zfx-rk{color:#0C7A5B}
#zfx .zfx-tk{font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:13.5px;color:#10201B}
#zfx .zfx-th{font-size:10px;color:#8A8776;text-transform:uppercase;letter-spacing:.4px}
#zfx .zfx-meter{display:flex;align-items:center;gap:7px;min-width:106px}
#zfx .zfx-track{flex:1;height:7px;background:#E7E2D6;border-radius:4px;overflow:hidden}
#zfx .zfx-fill{height:100%;border-radius:4px}
#zfx .zfx-mv{font-family:'IBM Plex Mono',monospace;font-weight:600;font-size:12px;color:#10201B;width:32px;text-align:right}
#zfx .zfx-tilt{font-family:'IBM Plex Mono',monospace;font-size:9px;display:block;margin-top:2px}
#zfx .zfx-pill{display:inline-flex;align-items:center;gap:5px;font-size:10.5px;font-weight:500;padding:3px 8px;border-radius:20px;white-space:nowrap}
#zfx .zfx-pill i{width:6px;height:6px;border-radius:50%}
#zfx .zfx-ok{background:#E7F3ED;color:#0A5E47}#zfx .zfx-ok i{background:#0C7A5B}
#zfx .zfx-warn{background:#FBF1DF;color:#8C641E}#zfx .zfx-warn i{background:#B4832B}
#zfx .zfx-bad{background:#F7E7E7;color:#8A2F32}#zfx .zfx-bad i{background:#9E3B3E}
#zfx .zfx-chk{background:#ECEBE4;color:#6D6A5E}#zfx .zfx-chk i{background:#9A968A}
#zfx .zfx-sig{display:inline-block;font-size:10.5px;font-weight:600;padding:3px 9px;border-radius:6px;white-space:nowrap}
#zfx .zfx-s-buy{background:#DEF1E7;color:#0A5E47}
#zfx .zfx-s-trend{background:#DDEFEA;color:#0C6B5A}
#zfx .zfx-s-brk{background:#E2E8F7;color:#37528C}
#zfx .zfx-s-wait{background:#FBF1DF;color:#8C641E}
#zfx .zfx-s-avd{background:#F7E7E7;color:#8A2F32}
#zfx .zfx-s-neu{background:#ECEBE4;color:#6D6A5E}
#zfx td.zfx-buy{color:#0A5E47;font-weight:600}
#zfx td.zfx-sl{color:#9E3B3E;font-weight:600}
#zfx .zfx-tps{font-family:'IBM Plex Mono',monospace;font-size:11px;color:#2A4A40}
#zfx .zfx-tps b{color:#0A5E47}
#zfx .zfx-alertbox{display:flex;flex-direction:column;gap:7px;margin-top:2px}
#zfx .zfx-alert{display:flex;gap:9px;align-items:flex-start;font-size:12.5px;padding:10px 13px;border-radius:9px;border:1px solid #E9E4D8;background:#FFF}
#zfx .zfx-alert .ad{margin-top:3px;font-size:9px}
#zfx .zfx-al-sl{border-left:3px solid #9E3B3E}#zfx .zfx-al-sl .ad{color:#9E3B3E}
#zfx .zfx-al-bz{border-left:3px solid #0C7A5B}#zfx .zfx-al-bz .ad{color:#0C7A5B}
#zfx .zfx-al-bk{border-left:3px solid #37528C}#zfx .zfx-al-bk .ad{color:#37528C}
#zfx .zfx-a-empty{color:#6D6A5E;font-size:12.5px;font-style:italic}
#zfx .zfx-charts{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:2px}
#zfx .zfx-chart{background:#FFF;border:1px solid #E9E4D8;border-radius:10px;padding:9px 9px 5px;min-height:186px}
#zfx .zfx-chart-h{font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:600;color:#10201B;margin:2px 4px 6px}
#zfx .zfx-chartnote{font-size:10.5px;color:#8A8776;margin-top:7px;font-style:italic}
@media(max-width:900px){#zfx .zfx-charts{grid-template-columns:repeat(2,1fr)}}
@media(max-width:520px){#zfx .zfx-charts{grid-template-columns:1fr}}
#zfx .zfx-brk2{background:#E2E8F7;color:#37528C}#zfx .zfx-brk2 i{background:#37528C}
#zfx .zfx-conf{font-size:8px;letter-spacing:1px;color:#0C7A5B;margin-top:3px}
#zfx .zfx-conf-o{color:#C9C4B5}
#zfx .zfx-news{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:2px}
#zfx .zfx-newscard{background:#FFF;border:1px solid #E9E4D8;border-left:3px solid #0C7A5B;border-radius:10px;padding:13px 16px}
#zfx .zfx-newscard h4{font-family:'Space Grotesk',sans-serif;font-size:13px;color:#10201B;margin-bottom:6px}
#zfx .zfx-newscard p{font-size:12.4px;color:#44493F;line-height:1.55}
#zfx .zfx-newscard b{color:#0A5E47}
@media(max-width:760px){#zfx .zfx-news{grid-template-columns:1fr}}
#zfx tbody tr.zfx-pick td{background:#E8F5EE !important}
#zfx tbody tr.zfx-pick td:first-child{box-shadow:inset 3px 0 0 #0C7A5B}
#zfx tbody tr.zfx-pick:hover td{background:#DDF0E5 !important}
#zfx .zfx-star{color:#0C7A5B;margin-right:4px;font-size:12px}
#zfx .zfx-guide{background:#FFF;border:1px solid #E9E4D8;border-radius:11px;margin-top:2px;overflow:hidden}
#zfx .zfx-guide>summary{cursor:pointer;list-style:none;padding:13px 18px;background:#10201B;color:#EDECE3;font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:14px;display:flex;align-items:center;gap:8px}
#zfx .zfx-guide>summary::-webkit-details-marker{display:none}
#zfx .zfx-guide>summary:after{content:"\25be";margin-left:auto;font-size:13px;transition:transform .2s}
#zfx .zfx-guide[open]>summary:after{transform:rotate(180deg)}
#zfx .zfx-gbody{padding:16px 20px}
#zfx .zfx-gintro{font-size:12.7px;color:#44493F;margin-bottom:12px;line-height:1.55}
#zfx .zfx-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:14px}
#zfx .zfx-step{display:flex;gap:10px;background:#F7F5EF;border:1px solid #EAE5D9;border-radius:9px;padding:11px 13px}
#zfx .zfx-stepn{flex:none;width:22px;height:22px;border-radius:50%;background:#0C7A5B;color:#fff;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:12px;display:flex;align-items:center;justify-content:center}
#zfx .zfx-steph{font-family:'Space Grotesk',sans-serif;font-size:12.5px;color:#10201B;display:block;margin-bottom:3px}
#zfx .zfx-step p{font-size:11.8px;color:#4A4E45;line-height:1.5}
#zfx .zfx-gsub{font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:1.5px;text-transform:uppercase;color:#0C7A5B;margin:12px 0 7px}
#zfx .zfx-lgwrap{display:flex;flex-direction:column;gap:5px}
#zfx .zfx-lg{display:flex;gap:10px;font-size:11.8px;color:#4A4E45}
#zfx .zfx-lgk{flex:none;min-width:130px;font-weight:600;color:#10201B}
#zfx .zfx-dcs{display:grid;grid-template-columns:1fr 1fr;gap:6px 18px}
#zfx .zfx-dc{display:flex;gap:8px;font-size:11.8px;color:#4A4E45;line-height:1.45}
#zfx .zfx-dc b{flex:none;min-width:96px;color:#0A5E47;font-family:'IBM Plex Mono',monospace;font-size:11px}
#zfx .zfx-ging{margin-top:13px;background:#FBF1DF;border:1px solid #EAD9B4;border-radius:8px;padding:10px 13px;font-size:11.8px;color:#6E561F;line-height:1.5}
@media(max-width:760px){#zfx .zfx-steps{grid-template-columns:1fr}#zfx .zfx-dcs{grid-template-columns:1fr}#zfx .zfx-lgk{min-width:90px}}
#zfx .zfx-notes{background:#10201B;color:#C9D6CD;border-radius:10px;padding:17px 21px;margin:6px 0 4px}
#zfx .zfx-notes h3{font-family:'Space Grotesk',sans-serif;color:#EDECE3;font-size:13.5px;margin-bottom:9px}
#zfx .zfx-notes ol{margin-left:16px;display:flex;flex-direction:column;gap:6px}
#zfx .zfx-notes li{font-size:12px;line-height:1.5}
#zfx .zfx-notes b{color:#7FCBB2}
#zfx .zfx-foot{padding:13px 30px 18px;font-size:10.5px;color:#8A8776;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;font-family:'IBM Plex Mono',monospace;border-top:1px solid #E4DFD2}
@media(max-width:760px){#zfx .zfx-kpis{grid-template-columns:repeat(2,1fr)}#zfx .zfx-panels{grid-template-columns:1fr}#zfx .zfx-badges{display:none}#zfx .zfx-regime{margin-left:0}}
</style>
"""

def _macro_strip(macro, regime):
    m = lambda k: macro.get(k, {})
    def chip(lbl, key, unit="", mult=1, dec=0):
        d = m(key)
        if not d: return _mchip(lbl, "\u2014", None)
        val = f"{d['last']*mult:,.{dec}f}{unit}"
        sub = f"{d['chg1m']*100:+.1f}% /bln"
        return _mchip(lbl, val, d.get("bias"), sub)
    man = CONFIG["macro_manual"]; prox = macro.get("_proxy", {})
    def commo(lbl, theme):
        if theme in prox:                       # auto via proxy
            d = prox[theme]
            return _mchip(lbl + "*", f"{d['chg1m']*100:+.1f}%", d["bias"], f"auto {d['sym']}")
        return _mchip(lbl, "\u2014", man.get(theme, 0), "read manual")
    chips = "".join([
        chip("Emas $/oz", "gold"),
        chip("Perak $/oz", "silver", dec=2),
        chip("Tembaga $/lb", "copper", dec=2),
        chip("Brent $/bbl", "brent", dec=1),
        commo("Batu bara", "coal"),
        commo("Nikel", "nickel"),
        commo("CPO", "cpo"),
        chip("USD/IDR", "usdidr", dec=0),
    ])
    rc = {"risk_off": ("reg-off", "RISK-OFF"), "risk_on": ("reg-on", "RISK-ON")}.get(regime, ("reg-neu", "NETRAL"))
    ih = m("ihsg")
    ih_txt = f"IHSG {ih['last']:,.0f}" if ih else "IHSG \u2014"
    return (f'<div class="zfx-macro">{chips}'
            f'<div class="zfx-regime">{ih_txt}<span class="zfx-reg-pill {rc[0]}">{rc[1]}</span></div></div>')

def _alerts_panel(alerts):
    ic = {"SL_BREAK": ("sl", "\u25cf"), "BUY_ZONE": ("bz", "\u25cf"), "BREAKOUT": ("bk", "\u25cf")}
    if not alerts:
        return ('<div class="zfx-alertbox zfx-a-empty">Tidak ada trigger area-beli / tembus-SL saat ini. '
                'Notifikasi Telegram akan terkirim begitu ada.</div>')
    items = ""
    for a in alerts:
        cls, dot = ic.get(a["type"], ("bk", "\u25cf"))
        items += f'<div class="zfx-alert zfx-al-{cls}"><span class="ad">{dot}</span>{a["msg"]}</div>'
    return f'<div class="zfx-alertbox">{items}</div>'

def _refresh_button(config=None):
    config = config or CONFIG
    owner = config.get("gh_owner", ""); repo = config.get("gh_repo", ""); wf = config.get("gh_workflow", "monitor.yml")
    if not (owner and repo):
        return ""
    css = ("<style>"
        "#zfx .zfx-refresh{position:fixed;bottom:18px;right:18px;z-index:60;background:#0C7A5B;color:#fff;border:none;"
        "border-radius:24px;padding:12px 18px;font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:14px;"
        "box-shadow:0 6px 18px rgba(0,0,0,.28);cursor:pointer}"
        "#zfx .zfx-refresh:active{transform:scale(.96)}#zfx .zfx-refresh[disabled]{opacity:.6}"
        "#zfx .zfx-refresh-msg{position:fixed;bottom:66px;right:18px;z-index:60;max-width:300px;background:#10201B;"
        "color:#EDECE3;font-size:12px;line-height:1.5;padding:9px 13px;border-radius:9px;box-shadow:0 6px 18px rgba(0,0,0,.28)}"
        "#zfx .zfx-refresh-msg:empty{display:none}#zfx .zfx-refresh-msg a{color:#7FCBB2}</style>")
    btn = ('<button id="zf-refresh" class="zfx-refresh" onclick="zfRefresh()">\u27f3 Refresh data</button>'
        '<div id="zf-refresh-msg" class="zfx-refresh-msg"></div>')
    js = ("<script>(function(){"
        "var O='__O__',R='__R__',W='__W__';"
        "var m=function(){return document.getElementById('zf-refresh-msg');};"
        "window.zfResetToken=function(){localStorage.removeItem('zf_gh_token');m().innerHTML='Token dihapus. Klik Refresh untuk token baru.';};"
        "window.zfRefresh=function(){"
        "var t=localStorage.getItem('zf_gh_token');"
        "if(!t){t=prompt('Tempel GitHub token (fine-grained, izin Actions: Read and write). Disimpan HANYA di perangkat ini:');"
        "if(!t){return;}t=t.trim();localStorage.setItem('zf_gh_token',t);}"
        "var b=document.getElementById('zf-refresh');b.disabled=true;m().textContent='Menjalankan bot di GitHub...';"
        "fetch('https://api.github.com/repos/'+O+'/'+R+'/actions/workflows/'+W+'/dispatches',{method:'POST',"
        "headers:{'Authorization':'Bearer '+t,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'},"
        "body:JSON.stringify({ref:'main'})}).then(function(r){b.disabled=false;"
        "if(r.status===204){var s=140;m().textContent='\u2713 Bot dijalankan. Reload otomatis ~'+s+' detik...';"
        "var iv=setInterval(function(){s-=5;if(s<=0){clearInterval(iv);location.reload();}else{m().textContent='\u2713 Dijalankan. Reload dalam '+s+' detik (bot+Pages sedang proses)...';}},5000);}"
        "else if(r.status===401||r.status===403){localStorage.removeItem('zf_gh_token');"
        "m().innerHTML='\u2717 Token salah/kurang izin. Klik Refresh lagi untuk token baru.';}"
        "else{r.text().then(function(x){m().innerHTML='\u2717 Gagal ('+r.status+'). <a href=\"https://github.com/'+O+'/'+R+'/actions\" target=\"_blank\">Jalankan manual</a>.';});}"
        "}).catch(function(e){b.disabled=false;m().innerHTML='\u2717 Tak bisa memanggil GitHub (CORS/jaringan). <a href=\"https://github.com/'+O+'/'+R+'/actions\" target=\"_blank\">Jalankan manual</a>.';});"
        "};})();</script>")
    js = js.replace("__O__", owner).replace("__R__", repo).replace("__W__", wf)
    return css + btn + js

def render_dashboard(df, config=None, macro=None, regime="neutral", generated_at=None, alerts=None, data_asof=None, price_max=None, n_universe=None):
    config = config or CONFIG
    macro = macro or {}
    alerts = alerts or []
    _filter_badge = f'<span class="zfx-badge" style="background:rgba(180,131,43,.16);border-color:rgba(180,131,43,.4);color:#E7C86B">Filter \u2264 Rp{price_max:,.0f}</span>' if price_max else ""
    _rank_suffix = f" \u00b7 harga &lt; Rp{price_max:,.0f}" if price_max else ""
    _univ_sub = (f"dari {n_universe} (filter aktif)" if (price_max and n_universe) else "watchlist Bibit")
    _dash = "\u2014"
    _now = _dt.datetime.now()
    if generated_at is None:
        generated_at = _now.strftime("%d %b %Y, %H:%M")
    _now_iso = _now.strftime("%Y-%m-%dT%H:%M:%S")
    if data_asof is None and "last_bar" in df.columns:
        try:
            data_asof = max(x for x in df["last_bar"].astype(str) if x and x != "nan")
        except Exception:
            data_asof = ""
    if generated_at is None:
        generated_at = _dt.datetime.now().strftime("%d %b %Y, %H:%M")

    n_total = len(df)
    n_layak = int((df["kelayakan"] == "LAYAK").sum())
    n_buy = int(df["signal"].astype(str).str.startswith(("BUY", "BREAKOUT", "TREND")).sum()) if "signal" in df else 0
    top = df.iloc[0] if n_total else None

    kpis = [
        ("Saham dipantau", f"{n_total}", _univ_sub),
        ("Layak (syariah+likuid)", f"{n_layak}", "lolos gerbang"),
        ("Sinyal beli/trend", f"{n_buy}", "buy/trend/breakout"),
        ("Peringkat #1", (top["ticker"] if top is not None else "\u2014"),
         (f"skor {_num(top['skor']):.1f}" if top is not None else "")),
        ("Regime IHSG", regime.replace("_", "-").upper(),
         (f"{macro.get('ihsg',{}).get('last',0):,.0f}" if macro.get("ihsg") else "")),
    ]
    kpi_html = "".join(f'<div class="zfx-kpi"><div class="l">{l}</div><div class="v">{v}</div><div class="s">{s}</div></div>'
                       for l, v, s in kpis)

    rows = ""
    for i, r in df.head(config["top_n"]).iterrows():
        _kf = r.get("konfluensi")
        _pick = (str(r.get("saran", "")) == "BELI" and _num(_kf) is not None
                 and _kf >= config.get("highlight_min_konfluensi", 4))
        top_cls = " ".join(x for x in ["zfx-top" if i < 3 else "", "zfx-pick" if _pick else ""] if x)
        _star = '<span class="zfx-star" title="Pilihan: Saran BELI + konfluensi tinggi">\u2605</span>' if _pick else ""
        tps = (f'<span class="zfx-tps"><b>{_rp(r.get("tp1"))}</b> \u00b7 '
               f'{_rp(r.get("tp2"))} \u00b7 {_rp(r.get("tp3"))}</span>')
        rows += (
            f'<tr class="{top_cls}">'
            f'<td class="zfx-rk">{r["rank"]}</td>'
            f'<td><div class="zfx-tk">{_star}{r["ticker"]}</div><div class="zfx-th">{str(r.get("theme") or "")[:18]}</div></td>'
            f'<td>{_meter(r.get("skor"), r.get("macro_tilt"))}</td>'
            f'<td>{_saran_pill(r)}</td>'
            f'<td>{_sigpill(r.get("signal"))}</td>'
            f'<td class="zfx-n zfx-buy">{_rp(r.get("entry_lo"))}\u2013{_rp(r.get("entry_hi"))}</td>'
            f'<td class="zfx-n zfx-sl">{_rp(r.get("sl"))}</td>'
            f'<td>{_sizing_cell(r)}</td>'
            f'<td>{tps}</td>'
            f'<td>{_sb_cell(r)}</td>'
            f'<td>{_outlook_pill(r["ticker"])}</td>'
            f'<td>{_spill(r.get("sharia_status"))}</td>'
            f'</tr>')

    legend = "".join(_sigpill(k) for k in ["BUY ZONE", "TREND (tahan/add)", "BREAKOUT", "TUNGGU PULLBACK", "HINDARI (downtrend)"])
    _guide_html = _guide_section(config)
    _charts_html = _charts_section(config)
    _news_html = _news_section()
    _refresh_html = _refresh_button(config)

    html = f"""
<div id="zfx">
{_CSS}
{_refresh_html}
  <div class="zfx-head">
    <div class="zfx-brand">ZF-Core \u00b7 Sharia Equity Desk \u00b7 Timing + Macro</div>
    <h1>Rekomendasi &amp; Timing Saham Syariah</h1>
    <div class="zfx-sub">Peringkat saham syariah watchlist Stockbit, dengan overlay kondisi pasar dunia &amp; Indonesia dan level beli/jual (closed-bar). Eksekusi manual di Bibit.</div>
    <div class="zfx-badges">
      <span class="zfx-badge zfx-fresh" data-ts="{_now_iso}">\u25cf Diperbarui {generated_at} WIB</span>
      <span class="zfx-badge">Data harga per {data_asof or _dash}</span>
      {_filter_badge}
      <span class="zfx-badge">POJK 8/2025</span>
    </div>
  </div>
  {_macro_strip(macro, regime)}
  <div class="zfx-kpis">{kpi_html}</div>
  <div class="zfx-body">
    {_guide_html}
    {_charts_html}
    <div class="zfx-eyebrow">Cara membaca</div>
    <div class="zfx-panels">
      <div class="zfx-panel">
        <h3>Skor &amp; overlay makro</h3>
        <p>Skor 0\u2013100 = peringkat persentil 5 faktor fundamental (value, quality, growth, momentum, likuiditas), lalu <b>digeser \u00b110 poin</b> oleh kondisi komoditas/tema masing-masing saham. Tag \u201c+/\u2212 makro\u201d di bawah skor menunjukkan arah geseran. Bila kolom <b>Stockbit</b> diisi (target/rating/flow dari akunmu), skor digeser tambahan \u00b18 poin &amp; angka fundamental yg berbeda >15% ditandai untuk validasi silang.</p>
      </div>
      <div class="zfx-panel">
        <h3>Sinyal timing (closed-bar, ZF-Core)</h3>
        <p style="margin-bottom:7px">Area beli = pullback ke EMA-50 / breakout resistance. SL di bawah struktur swing. TP ladder = kelipatan risiko (2R\u00b74R\u00b76R). <b>Jual/kurangi bila close di bawah SL</b> atau EMA-13 memotong turun EMA-50.</p>
        <div class="zfx-legend">{legend}</div><p style="margin-top:8px;font-size:11.5px">Skoring <b>sektor-netral</b> (z-score dalam sektor). <b>Saran AI</b> = fusi sinyal+fundamental+akumulasi+berita+analis; titik di bawahnya = <b>konfluensi</b> (0–5 sinyal sepakat). <b>Sizing</b> = lot berbasis risiko (default 1% modal per trade, set di CONFIG). Akumulasi/distribusi via Chaikin Money Flow + net-asing.</p>      </div>
    </div>
    <div class="zfx-eyebrow">Alert aktif &middot; terhubung Telegram</div>
    {_alerts_panel(alerts)}
    <div class="zfx-eyebrow">Peringkat + kapan beli/jual{_rank_suffix}</div>
    <div class="zfx-tablewrap"><table>
      <thead><tr><th>#</th><th>Saham \u00b7 tema</th><th>Skor</th><th>Saran AI</th><th>Sinyal</th><th>Area beli</th><th>Stop loss</th><th>Sizing</th><th>TP1 \u00b7 TP2 \u00b7 TP3</th><th>Stockbit \u25b4</th><th>Outlook 100h</th><th>Status syariah</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
    {_news_html}
    <div class="zfx-eyebrow">Yang wajib diketahui</div>
    <div class="zfx-notes">
      <h3>Sebelum eksekusi</h3>
      <ol>
        <li><b>Snapshot makro.</b> Angka komoditas/IHSG di atas adalah kondisi saat notebook dijalankan; batu bara/nikel/CPO memakai <i>read manual</i> (tanggal di CONFIG) \u2014 perbarui bila pasar bergerak.</li>
        <li><b>Level = mekanis, bukan ramalan.</b> Area beli, SL, dan TP dihitung dari EMA/ATR/struktur closed-bar. Bukan jaminan; harga bisa lompati level (gap).</li>
        <li><b>Event risk.</b> Sekitar rapat Fed &amp; gejolak geopolitik, spread melebar &amp; volatilitas naik \u2014 pertimbangkan ukuran lebih kecil / tunggu konfirmasi.</li>
        <li><b>Syariah.</b> Status = verifikasi rasio (proksi laporan tahunan); keanggotaan DES final tetap dicek di filter \u201cSyariah\u201d Bibit.</li>
        <li><b>Stockbit = input manual.</b> Stockbit tak punya API publik resmi; angkanya kamu isi sendiri dari akunmu (target konsensus, rating, net asing). Bot memakainya untuk validasi silang &amp; pertimbangan, bukan menyambung/scraping otomatis.</li>
        <li><b>Telegram.</b> Notifikasi dikirim saat harga masuk area beli / tembus SL. Jaga token bot rahasia (jangan dibagikan). Untuk pantau 24/7, jalankan di VPS/cron atau GitHub Actions \u2014 sesi Colab bisa mati saat idle.</li>
        <li><b>Bukan nasihat keuangan.</b> Sesuaikan dgn horizon &amp; profil risiko. Eksekusi beli/jual manual di Bibit.</li>
      </ol>
    </div>
  </div>
  <div class="zfx-foot"><span>ZF-Core Sharia Equity Desk \u00b7 25 saham \u00b7 Timing+Macro+Stockbit</span><span>Data harga per {data_asof or _dash} \u00b7 dijalankan {generated_at} WIB</span></div>
  <script>
  (function(){{
    var els=document.querySelectorAll('#zfx .zfx-fresh');
    els.forEach(function(e){{
      var t=new Date(e.dataset.ts);
      function upd(){{
        var s=(Date.now()-t.getTime())/1000, txt, col;
        if(isNaN(s)){{return;}}
        if(s<90){{txt='baru saja';col='#7FCBB2';}}
        else if(s<3600){{txt=Math.round(s/60)+' mnt lalu';col='#7FCBB2';}}
        else if(s<86400){{txt=Math.round(s/3600)+' jam lalu';col='#E7C86B';}}
        else {{txt=Math.round(s/86400)+' hari lalu \u2014 mungkin basi';col='#E79A9C';}}
        e.innerHTML='\u25cf Diperbarui '+txt;
        e.style.color=col; e.style.borderColor=col;
      }}
      upd(); setInterval(upd,30000);
    }});
  }})();
  </script>
</div>
"""
    return html

def full_page(inner, title="ZF Saham Syariah"):
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        f'<title>{title}</title>'
        '<link rel="manifest" href="manifest.json">'
        '<meta name="theme-color" content="#10201B">'
        '<meta name="mobile-web-app-capable" content="yes">'
        '<meta name="apple-mobile-web-app-capable" content="yes">'
        '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'
        '<meta name="apple-mobile-web-app-title" content="ZF Syariah">'
        '<link rel="apple-touch-icon" href="apple-touch-icon.png">'
        '<link rel="icon" type="image/png" href="icon-192.png">'
        '</head>'
        '<body style="margin:0;padding:16px;background:#ECE9DF">'
        f'{inner}'
        '<script>if("serviceWorker" in navigator){navigator.serviceWorker.register("sw.js").catch(function(){});}</script>'
        '</body></html>')

# ===== sec_buyzone =====
# ======================================================================
# SCREENER "AREA BELI SEKARANG" (real-time) — saham syariah yg siap beli
# + aturan JUAL eksplisit. Fokus & ringkas. Reuse helper dari sec_render.
# Catatan: harga yfinance IDX tertunda ~15 menit (bukan tick real-time).
# ======================================================================
import datetime as _dt3

def _zone_status(r):
    last = _num(r.get("last")); lo = _num(r.get("entry_lo")); hi = _num(r.get("entry_hi"))
    sl = _num(r.get("sl")); sig = str(r.get("signal", ""))
    if last is None or lo is None or hi is None:
        return None
    if sl is not None and last < sl:      # sudah tembus SL -> bukan kandidat beli
        return None
    if lo <= last <= hi:                 return "MASUK"      # harga DI area beli
    if sig == "BREAKOUT" and last >= lo:  return "BREAKOUT"   # tembus resistance
    if lo * 0.98 <= last <= hi * 1.02:    return "DEKAT"      # dalam 2% dari zona
    if sig.startswith("BUY ZONE"):        return "SIAP"       # sinyal buy zone
    return None

_STPRI = {"MASUK": 0, "BREAKOUT": 1, "SIAP": 2, "DEKAT": 3}

def screen_buyzone(df):
    """Saring saham syariah LAYAK yang sedang di/dekat area beli. Urut prioritas."""
    rows = []
    for _, r in df.iterrows():
        if str(r.get("kelayakan", "")) != "LAYAK":
            continue
        if str(r.get("sharia_status", "")).startswith(("LEWAT", "NONHALAL")):
            continue
        st = _zone_status(r)
        if st is None:
            continue
        d = dict(r); d["_zone"] = st
        rows.append(d)
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows)
    out["_pri"] = out["_zone"].map(_STPRI).fillna(9)
    out = out.sort_values(["_pri", "konfluensi", "skor"], ascending=[True, False, False]).reset_index(drop=True)
    return out

def refresh_pipeline():
    """Ambil ulang data + hitung semua (untuk loop real-time). Return (df, macro, regime)."""
    macro = fetch_macro(); tb, regime = theme_bias(macro)
    _rows = [r for r in (fetch_one(t) for t in CONFIG["universe"]) if r]
    df = apply_macro(apply_stockbit(score(pd.DataFrame(_rows))), tb, regime)
    df = add_recommendations(df); df = add_confluence(df); df = add_position_sizing(df)
    df.insert(0, "rank", df.index + 1)
    return df, macro, regime

# ---------------------- tampilan ringkas ----------------------
_ZBADGE = {
    "MASUK":    ("#0C7A5B", "MASUK AREA BELI"),
    "BREAKOUT": ("#37528C", "BREAKOUT"),
    "SIAP":     ("#128C74", "SIAP (buy zone)"),
    "DEKAT":    ("#B4832B", "DEKAT AREA"),
}

_BZ_CSS = """
<style>
#zfx .bz-wrap{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:4px}
#zfx .bz{background:#FFF;border:1px solid #E9E4D8;border-radius:11px;padding:14px 16px;border-left:4px solid #0C7A5B}
#zfx .bz-top{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
#zfx .bz-tk{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:19px;color:#10201B}
#zfx .bz-px{font-family:'IBM Plex Mono',monospace;font-size:14px;color:#10201B}
#zfx .bz-badge{margin-left:auto;font-size:10.5px;font-weight:700;color:#fff;padding:3px 10px;border-radius:20px}
#zfx .bz-conf{font-size:9px;letter-spacing:1px;color:#0C7A5B;margin-top:2px}
#zfx .bz-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:11px 0 9px}
#zfx .bz-cell{background:#F7F5EF;border:1px solid #EAE5D9;border-radius:8px;padding:7px 9px}
#zfx .bz-cell .l{font-size:9px;letter-spacing:.8px;text-transform:uppercase;color:#8A8776}
#zfx .bz-cell .v{font-family:'IBM Plex Mono',monospace;font-size:12.5px;font-weight:600;margin-top:2px}
#zfx .bz-sell{background:#FBF1DF;border:1px solid #EAD9B4;border-radius:8px;padding:8px 11px;font-size:11.5px;color:#6E561F;line-height:1.5}
#zfx .bz-sell b{color:#8A2F32}
#zfx .bz-empty{background:#FFF;border:1px dashed #D8D2C2;border-radius:11px;padding:26px;text-align:center;color:#6D6A5E;font-size:13px}
@media(max-width:720px){#zfx .bz-wrap{grid-template-columns:1fr}#zfx .bz-grid{grid-template-columns:1fr 1fr}}
</style>
"""

def render_buyzone(bz, macro=None, regime="neutral", generated_at=None):
    macro = macro or {}
    if generated_at is None:
        generated_at = _dt3.datetime.now().strftime("%d %b %Y, %H:%M")
    ih = macro.get("ihsg", {}).get("last")
    reg = {"risk_off": "RISK-OFF", "risk_on": "RISK-ON"}.get(regime, "NETRAL")

    if bz is None or len(bz) == 0:
        cards = ('<div class="bz-empty">Belum ada saham syariah yang di area beli saat ini.<br>'
                 'Tunggu harga pullback ke zona, atau cek lagi nanti (screener akan memantau).</div>')
    else:
        cards = '<div class="bz-wrap">'
        for _, r in bz.iterrows():
            col, lbl = _ZBADGE.get(r["_zone"], ("#6D6A5E", r["_zone"]))
            last = _num(r.get("last")); sl = _num(r.get("sl"))
            sl_pct = f" ({(sl/last-1)*100:+.0f}%)" if (last and sl) else ""
            k = int(r["konfluensi"]) if _num(r.get("konfluensi")) is not None else 0
            dots = "\u25cf" * k + "\u25cb" * (5 - k)
            lot = int(r["lot"]) if _num(r.get("lot")) else 0
            cards += (
                '<div class="bz" style="border-left-color:%s">' % col +
                '<div class="bz-top"><span class="bz-tk">%s</span>' % r["ticker"] +
                '<span class="bz-px">Rp%s</span>' % (f"{last:,.0f}" if last else "\u2014") +
                '<span class="bz-badge" style="background:%s">%s</span></div>' % (col, lbl) +
                '<div class="bz-conf">%s \u00b7 %s \u00b7 %s</div>' % (dots, str(r.get("theme") or ""), str(r.get("sharia_status") or "")) +
                '<div class="bz-grid">' +
                '<div class="bz-cell"><div class="l">Area beli</div><div class="v" style="color:#0A5E47">%s\u2013%s</div></div>' % (_rp(r.get("entry_lo")), _rp(r.get("entry_hi"))) +
                '<div class="bz-cell"><div class="l">Stop loss</div><div class="v" style="color:#9E3B3E">%s%s</div></div>' % (_rp(r.get("sl")), sl_pct) +
                '<div class="bz-cell"><div class="l">Lot (risiko 1%%)</div><div class="v">%s</div></div>' % (lot if lot else "\u2014") +
                '</div>' +
                '<div class="bz-cell" style="margin-bottom:9px"><div class="l">Target profit (TP1\u00b7TP2\u00b7TP3)</div>'
                '<div class="v" style="color:#0A5E47">%s \u00b7 %s \u00b7 %s</div></div>' % (_rp(r.get("tp1")), _rp(r.get("tp2")), _rp(r.get("tp3"))) +
                '<div class="bz-sell">\U0001f6d1 <b>Kapan jual:</b> keluar bila harga <b>tutup &lt; Stop Loss</b> (%s); '
                'ambil untung bertahap di TP1/TP2/TP3; atau keluar bila tren patah (EMA-13 memotong turun EMA-50). '
                'Setelah TP1 tercapai, geser SL ke titik impas.</div>' % _rp(r.get("sl")) +
                '</div>')
        cards += '</div>'

    n = 0 if (bz is None) else len(bz)
    ih_txt = f"IHSG {ih:,.0f} \u00b7 " if ih else ""
    return f"""
<div id="zfx">
{_CSS}{_BZ_CSS}
  <div class="zfx-head">
    <div class="zfx-brand">ZF-Core \u00b7 Screener Area Beli</div>
    <h1>\U0001f3af Saham Syariah di Area Beli Sekarang</h1>
    <div class="zfx-sub">{n} saham syariah siap/dekat area beli. {ih_txt}{reg}. Data harga tertunda ~15 menit \u2014 konfirmasi di Bibit sebelum eksekusi.</div>
    <div class="zfx-badges"><span class="zfx-badge zfx-fresh" data-ts="{_dt3.datetime.now():%Y-%m-%dT%H:%M:%S}">\u25cf Diperbarui {generated_at}</span></div>
  </div>
  <div class="zfx-body">
    {cards}
    <div class="zfx-eyebrow">Yang wajib diketahui</div>
    <div class="zfx-notes"><h3>Aturan main</h3><ol>
      <li><b>Area beli</b> = rentang harga masuk (pullback ke EMA-50 / breakout). Beli hanya saat harga di dalam zona, jangan dikejar.</li>
      <li><b>Kapan jual</b>: tutup di bawah SL (batasi rugi), atau bertahap di TP, atau saat tren patah (EMA-13 &lt; EMA-50).</li>
      <li><b>Sizing</b> lot sudah dihitung agar rugi maksimal ~1% modal. Set modalmu di CONFIG.</li>
      <li>Sudah lolos gerbang <b>syariah + likuiditas</b>. Tetap konfirmasi keanggotaan DES di filter \u201cSyariah\u201d Bibit.</li>
      <li>Data tertunda ~15 menit; ini alat bantu, <b>bukan nasihat keuangan</b>. Eksekusi manual di Bibit.</li>
    </ol></div>
  </div>
  <div class="zfx-foot"><span>ZF-Core \u00b7 Screener Area Beli</span><span>Data: Yahoo Finance (IDX) \u00b7 {generated_at}</span></div>
</div>
"""

# ===== sec_scalp =====
# ======================================================================
# ZF SCALP SCANNER — saring saham syariah PALING LAYAK di-scalp hari ini.
# Ini SCANNER KANDIDAT (likuiditas + volatilitas + volume), BUKAN sinyal
# entry presisi. Data yfinance IDX tertunda ~15 mnt → konfirmasi chart Bibit.
# ======================================================================
import datetime as _dts

def _scalp_metrics(ticker):
    """Ambil daily(3bln)+intraday(5m) -> metrik scalping. None bila data kurang."""
    try:
        tk = yf.Ticker(ticker)
        d = tk.history(period="3mo", interval="1d", auto_adjust=False)
        if d is None or d.empty or len(d) < 20:
            return None
        close = d["Close"].dropna(); high = d["High"]; low = d["Low"]; vol = d["Volume"]
        last = float(close.iloc[-1])
        if not last or last <= 0:
            return None
        tr = pd.concat([(high - low), (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
        atr_pct = atr / last * 100.0
        rng_pct = float(((high - low) / close).tail(10).mean() * 100.0)
        vavg = float(vol.tail(20).mean()); vtoday = float(vol.iloc[-1])
        vol_surge = (vtoday / vavg) if vavg else None
        avg_value = float((close.tail(20) * vol.tail(20)).mean())
        # VWAP intraday (opsional; bisa kosong pra-bursa)
        vwap = None; vs_vwap = "—"; cur = last
        try:
            it = tk.history(period="1d", interval="5m", auto_adjust=False)
            if it is not None and not it.empty and it["Volume"].sum() > 0:
                tp = (it["High"] + it["Low"] + it["Close"]) / 3.0
                cvol = it["Volume"].cumsum()
                vwap = float((tp * it["Volume"]).cumsum().iloc[-1] / cvol.iloc[-1])
                cur = float(it["Close"].iloc[-1])
                vs_vwap = "di atas" if cur >= vwap else "di bawah"
        except Exception:
            pass
        return {"ticker": ticker, "last": cur, "atr_pct": atr_pct, "range_pct": rng_pct,
                "vol_surge": vol_surge, "avg_value_idr": avg_value, "vwap": vwap, "vs_vwap": vs_vwap}
    except Exception as e:
        print(f"  !scalp {ticker}: {e}")
        return None

def _vol_sweetspot(atr_pct):
    """Volatilitas ideal utk scalp ~1.5-4% (puncak 2.5%). Terlalu sepi/terlalu liar -> skor turun."""
    if atr_pct is None: return 0.0
    x = atr_pct
    if x < 0.8:  return max(0.0, x / 0.8 * 35)
    if x <= 4.0: return max(35.0, 100 - abs(x - 2.5) * 12)
    if x <= 7.0: return max(25.0, 100 - (x - 4) * 18)
    return max(0.0, 25 - (x - 7) * 6)

def scalp_score(m, cfg=None):
    cfg = cfg or CONFIG
    liq = m.get("avg_value_idr") or 0.0
    liq_s = min(100.0, liq / float(cfg.get("scalp_liq_full", 50e9)) * 100.0)   # 50 M/hari -> 100
    vol_s = _vol_sweetspot(m.get("atr_pct"))
    surge = m.get("vol_surge") or 0.0
    surge_s = min(100.0, surge * 50.0)                                          # 2x -> 100
    rng = m.get("range_pct") or 0.0
    rng_s = min(100.0, rng / 3.0 * 100.0)                                       # 3% -> 100
    return round(0.40 * liq_s + 0.30 * vol_s + 0.18 * surge_s + 0.12 * rng_s, 1)

def scan_scalp(universe=None, cfg=None):
    """Pindai universe -> DataFrame kandidat scalp (likuid + bergerak), urut skor."""
    cfg = cfg or CONFIG
    universe = universe or cfg["universe"]
    minval = float(cfg.get("scalp_min_value_idr", 10e9))
    rows = []
    for t in universe:
        m = _scalp_metrics(_jk(t, cfg))
        if not m:
            continue
        if (m.get("avg_value_idr") or 0) < minval:       # gerbang likuiditas (wajib utk scalp)
            continue
        m["scalp_score"] = scalp_score(m, cfg)
        m["ticker"] = t
        rows.append(m)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).sort_values("scalp_score", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", df.index + 1)
    return df

def _jk(t, cfg):
    suf = cfg.get("ticker_suffix", ".JK")
    return t if t.endswith((".JK", ".SR")) else t + suf

# ---------------------- Telegram ----------------------
def format_scalp_telegram(df, cfg=None):
    cfg = cfg or CONFIG
    t = _dts.datetime.now().strftime("%d %b %Y %H:%M")
    L = [f"<b>\U0001f3af ZF Scalp Scanner</b> \u2014 {t} WIB",
         "Kandidat scalping syariah (likuid + bergerak):", ""]
    for _, r in df.iterrows():
        av = (r.get("avg_value_idr") or 0) / 1e9
        surge = r.get("vol_surge"); srg = f"{surge:.1f}\u00d7" if surge else "\u2014"
        atrp = r.get("atr_pct"); atrs = f"{atrp:.1f}%" if atrp else "\u2014"
        vw = r.get("vs_vwap") or "\u2014"
        L.append(f"{int(r['rank'])}. <b>{r['ticker']}</b> \u00b7 skor {r['scalp_score']:.0f}")
        L.append(f"   Rp{r['last']:,.0f} \u00b7 ATR {atrs} \u00b7 vol {srg} \u00b7 VWAP: {vw}")
        L.append(f"   likuiditas \u2248Rp{av:,.0f} M/hari")
    L += ["", "<i>\u26a0\ufe0f Ini kandidat likuiditas/volatilitas, BUKAN sinyal entry. "
              "Konfirmasi di chart real-time Bibit; data tertunda ~15 mnt. Bukan nasihat keuangan.</i>"]
    return "\n".join(L)

# ---------------------- HTML ringkas ----------------------
def render_scalp(df, cfg=None):
    cfg = cfg or CONFIG
    now = _dts.datetime.now().strftime("%d %b %Y, %H:%M")
    if df is None or len(df) == 0:
        cards = ('<div class="bz-empty">Belum ada kandidat scalping yang lolos gerbang likuiditas saat ini. '
                 'Coba lagi saat sesi bursa lebih ramai.</div>')
    else:
        cards = '<div class="bz-wrap">'
        for _, r in df.iterrows():
            sc = r["scalp_score"]
            col = "#0C7A5B" if sc >= 75 else ("#128C74" if sc >= 60 else "#B4832B")
            surge = r.get("vol_surge"); srg = f"{surge:.1f}\u00d7" if surge else "\u2014"
            atrp = r.get("atr_pct"); atrs = f"{atrp:.1f}%" if atrp else "\u2014"
            av = (r.get("avg_value_idr") or 0) / 1e9
            vwap = r.get("vwap")
            cards += (
                '<div class="bz" style="border-left-color:%s">' % col +
                '<div class="bz-top"><span class="bz-tk">%s</span>' % r["ticker"] +
                '<span class="bz-px">Rp%s</span>' % (f"{r['last']:,.0f}") +
                '<span class="bz-badge" style="background:%s">SCALP %.0f</span></div>' % (col, sc) +
                '<div class="bz-grid">'
                '<div class="bz-cell"><div class="l">ATR harian</div><div class="v">%s</div></div>' % atrs +
                '<div class="bz-cell"><div class="l">Lonjakan vol</div><div class="v">%s</div></div>' % srg +
                '<div class="bz-cell"><div class="l">vs VWAP</div><div class="v">%s</div></div>' % (r.get("vs_vwap", "\u2014")) +
                '</div>'
                '<div class="bz-cell" style="margin-bottom:9px"><div class="l">Likuiditas (nilai transaksi/hari)</div>'
                '<div class="v" style="color:#0A5E47">\u2248Rp%s miliar %s</div></div>' % (f"{av:,.0f}", (f"\u00b7 VWAP Rp{vwap:,.0f}" if vwap else "")) +
                '<div class="bz-sell">\u26a1 <b>Cara pakai:</b> ini kandidat paling likuid & bergerak untuk di-scalp. '
                'Buka chart real-time (1m/5m) di Bibit, cari entry di sekitar VWAP/level, target kecil, '
                'stop ketat. Skor tinggi = likuiditas & volatilitas lebih cocok \u2014 <b>bukan</b> aba-aba beli.</div>'
                '</div>')
        cards += '</div>'
    n = 0 if df is None else len(df)
    return f"""
<div id="zfx">
{_CSS}{_BZ_CSS}
  <div class="zfx-head">
    <div class="zfx-brand">ZF-Core \u00b7 Scalp Scanner</div>
    <h1>\u26a1 Kandidat Scalping Saham Syariah</h1>
    <div class="zfx-sub">{n} kandidat lolos gerbang likuiditas. Data tertunda ~15 menit \u2014 scanner kandidat, bukan sinyal entry.</div>
    <div class="zfx-badges"><span class="zfx-badge zfx-fresh" data-ts="{_dts.datetime.now():%Y-%m-%dT%H:%M:%S}">\u25cf Diperbarui {now}</span></div>
  </div>
  <div class="zfx-body">
    {cards}
    <div class="zfx-eyebrow">Yang wajib diketahui</div>
    <div class="zfx-notes"><h3>Batasan jujur</h3><ol>
      <li>Ini <b>penyaring kandidat</b> (likuiditas + volatilitas + volume), <b>bukan</b> sinyal beli/jual menit-per-menit.</li>
      <li>Data yfinance IDX <b>tertunda ~15 menit</b> \u2014 untuk scalping sungguhan kamu butuh chart & kuotasi real-time (mis. langganan di Bibit).</li>
      <li>Likuiditas adalah syarat utama scalping (mudah masuk-keluar). Volatilitas ideal ~1,5\u20134% ATR harian.</li>
      <li>Scalping berisiko tinggi & sering diperdebatkan secara syariah \u2014 pertimbangkan sendiri. Bukan nasihat keuangan.</li>
    </ol></div>
  </div>
  <div class="zfx-foot"><span>ZF-Core \u00b7 Scalp Scanner</span><span>Data: Yahoo Finance (IDX, delayed) \u00b7 {now}</span></div>
</div>
"""
