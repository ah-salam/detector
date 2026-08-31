# -*- coding: utf-8 -*-
"""
ZF Scalp Scanner — satu siklus (GitHub Actions).
Pindai kandidat scalping syariah (likuiditas + volatilitas + volume) -> Telegram + docs/scalp.html.
Anti-spam: hanya kirim bila set kandidat berubah (atau run manual FORCE_SEND).
Secrets: TG_TOKEN, TG_CHAT.
"""
import os, json, datetime, pathlib
from zf_core import (CONFIG, scan_scalp, format_scalp_telegram, render_scalp,
                     full_page, send_telegram)

TOKEN = os.environ.get("TG_TOKEN")
CHAT  = os.environ.get("TG_CHAT")
FORCE = os.environ.get("FORCE_SEND", "").lower() in ("1", "true", "yes")
STATE = pathlib.Path("state/scalp_state.json")


def main():
    print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] scalp scan mulai")
    df = scan_scalp(CONFIG["universe"])
    if df is None or len(df) == 0:
        print("Tak ada kandidat / data kosong (mungkin di luar jam bursa / rate-limit).")
        return
    df = df.head(CONFIG.get("scalp_top_n", 8))

    pathlib.Path("docs").mkdir(exist_ok=True)
    pathlib.Path("docs/scalp.html").write_text(full_page(render_scalp(df, CONFIG)), encoding="utf-8")

    top = df[df["scalp_score"] >= CONFIG.get("scalp_score_min", 60)]
    tickers = ",".join(sorted(top["ticker"].tolist()))

    prev = ""
    try:
        prev = json.loads(STATE.read_text()).get("set", "")
    except Exception:
        pass

    if not (TOKEN and CHAT):
        print("TG_TOKEN/TG_CHAT belum diset — lewati kirim.")
    elif len(top) == 0:
        print(f"tak ada kandidat >= ambang {CONFIG.get('scalp_score_min', 60)}.")
    elif FORCE or tickers != prev:
        ok, info = send_telegram(format_scalp_telegram(top, CONFIG), TOKEN, CHAT)
        print("kirim scalp:", "OK" if ok else "GAGAL", info)
    else:
        print("set kandidat sama seperti sebelumnya — skip kirim (anti-spam).")

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"set": tickers, "at": datetime.datetime.now().isoformat()}))
    print(f"selesai · {len(df)} dipindai · {len(top)} kandidat (skor>=ambang)")


if __name__ == "__main__":
    main()
