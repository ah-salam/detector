# -*- coding: utf-8 -*-
"""
ZF Saham Syariah — satu siklus pemantauan (untuk GitHub Actions / cron / VPS).

Alur: fetch makro (auto-proxy) -> fetch 15 saham (harga+fundamental+timing)
      -> skor + overlay makro -> hitung alert -> kirim Telegram (hanya trigger
      BARU per hari) -> simpan state + tulis dashboard docs/index.html + CSV.

Secrets via environment:
  TG_TOKEN, TG_CHAT        -> token bot & chat id Telegram (GitHub Secrets)
  FORCE_SUMMARY=true       -> kirim ringkasan peringkat penuh (mis. saat open)
"""
import os, json, datetime, pathlib
import pandas as pd

from zf_core import (CONFIG, fetch_macro, theme_bias, apply_macro, fetch_one, score, apply_stockbit, price_filter, load_stockbit_csv,
                     build_live_news, add_recommendations, add_confluence, add_position_sizing,
                     compute_alerts, format_telegram, send_telegram,
                     render_dashboard, full_page)

STATE = pathlib.Path("state/alert_state.json")
TOKEN = os.environ.get("TG_TOKEN")
CHAT  = os.environ.get("TG_CHAT")
FORCE_SUMMARY = os.environ.get("FORCE_SUMMARY", "").lower() in ("1", "true", "yes")


def load_state():
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {}

def save_state(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1))


def main():
    today = datetime.date.today().isoformat()
    print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] mulai siklus")

    # Stockbit opsional: taruh stockbit.csv di repo utk mengisi otomatis
    if pathlib.Path('stockbit.csv').exists():
        try:
            _sb = load_stockbit_csv('stockbit.csv'); print('Stockbit dimuat:', len(_sb), 'saham')
        except Exception as _e: print('stockbit.csv gagal:', _e)

    macro = fetch_macro()
    tb, regime = theme_bias(macro)
    rows = [r for r in (fetch_one(t) for t in CONFIG["universe"]) if r]
    if not rows:
        print("Tidak ada data saham (rate limit / jaringan). Keluar tanpa kirim.")
        return
    df_all = score(pd.DataFrame(rows))
    df_all = apply_stockbit(df_all)  # lapis Stockbit (input manual, kalau diisi)
    df_all = apply_macro(df_all, tb, regime)
    live = build_live_news(CONFIG["universe"], CONFIG["theme_map"])   # berita AI (butuh GEMINI_API_KEY)
    print("berita:", "LIVE" if live else "snapshot")
    df_all = add_recommendations(df_all)               # saran beli/jual (ter-update)
    df_all = add_confluence(df_all); df_all = add_position_sizing(df_all)
    df_all.to_csv(CONFIG["export_csv"], index=False)   # CSV simpan SEMUA

    n_universe = len(df_all)
    df = price_filter(df_all, CONFIG.get("max_price"))  # filter harga < Rp3.000
    df.insert(0, "rank", df.index + 1)
    alerts = compute_alerts(df)
    pathlib.Path("docs").mkdir(exist_ok=True)
    html = full_page(render_dashboard(df, CONFIG, macro=macro, regime=regime, alerts=alerts,
                                      price_max=CONFIG.get("max_price"), n_universe=n_universe))
    pathlib.Path("docs/index.html").write_text(html, encoding="utf-8")

    # dedup harian: alert yg sama tak dikirim dua kali di hari yg sama
    state = load_state()
    if state.get("day") != today:
        state = {"day": today, "sent": {}}
    sent = state.setdefault("sent", {})
    new = [a for a in alerts if f"{a['ticker']}|{a['type']}" not in sent]

    if not (TOKEN and CHAT):
        print("TG_TOKEN/TG_CHAT belum diset — lewati kirim Telegram.")
    elif FORCE_SUMMARY:
        ok, info = send_telegram(format_telegram(df, macro, regime, alerts, top_n=8), TOKEN, CHAT)
        print("ringkasan harian:", "OK" if ok else "GAGAL", info)
    elif new:
        ok, info = send_telegram(format_telegram(df, macro, regime, new, top_n=5), TOKEN, CHAT)
        print(f"kirim {len(new)} alert baru:", "OK" if ok else "GAGAL", info)
    else:
        print("tidak ada alert baru.")

    for a in new:
        sent[f"{a['ticker']}|{a['type']}"] = today
    save_state(state)
    print(f"selesai · {len(df)} saham · {len(alerts)} alert ({len(new)} baru) · regime {regime}")


if __name__ == "__main__":
    main()
