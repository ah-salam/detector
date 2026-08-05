# ZF Saham Syariah — Monitor Otomatis 24/7

Pemantau 25 saham syariah (watchlist Bibit) yang berjalan otomatis via **GitHub Actions**:
fetch makro (dengan auto-proxy nikel/batu bara/CPO) → skor + timing → **alert area-beli / tembus-SL** → **notifikasi Telegram**. Dashboard punya indikator **"Terakhir diperbarui"** (waktu relatif otomatis: hijau=segar, kuning=beberapa jam, merah=mungkin basi) + **tanggal bar harga**. Tanpa perlu Colab tetap terbuka.

## Isi repo

```
zf_core.py                     # semua logika (config, makro, timing, alert, telegram, render)
run_monitor.py                 # satu siklus: fetch → alert → Telegram → simpan state + dashboard
requirements.txt
.github/workflows/monitor.yml  # jadwal otomatis (cron) + commit state kembali
state/                         # alert_state.json (dedup harian, dibuat otomatis)
docs/                          # index.html (dashboard, bisa dipublikasi via GitHub Pages)
```

## Setup (sekali, ~10 menit)

**1. Buat repo GitHub** (private disarankan) lalu unggah semua file ini apa adanya.

**2. Buat bot Telegram**
- Chat `@BotFather` → `/newbot` → salin **token**.
- Chat bot barumu sekali (kirim "halo"), lalu buka
  `https://api.telegram.org/bot<TOKEN>/getUpdates` dan salin **chat id** (`"chat":{"id":...}`).
  Alternatif: chat `@userinfobot` untuk melihat id-mu.

**3. Simpan sebagai GitHub Secrets**
Repo → **Settings → Secrets and variables → Actions → New repository secret**:
- `TG_TOKEN` = token bot
- `TG_CHAT`  = chat id

**4. Aktifkan Actions**
Tab **Actions** → izinkan workflow. Uji manual: pilih *ZF Saham Syariah Monitor* → **Run workflow**.
Bila token benar, ringkasan akan masuk ke Telegram.

**5. (Opsional) Dashboard online**
Settings → **Pages** → Source: *Deploy from a branch* → `main` / folder `/docs`.
Dashboard live tampil di `https://<user>.github.io/<repo>/`.

## Jadwal

Cron GitHub memakai **UTC** (WIB = UTC+7). Default di `monitor.yml`:
- `5 2 * * 1-5` → **09:05 WIB**, ringkasan peringkat harian (`FORCE_SUMMARY`).
- `*/30 2-9 * * 1-5` → tiap **30 menit, 09:00–16:00 WIB** (jam bursa), kirim hanya alert **baru**.

Ubah sesuai selera. Alert yang sama tak dikirim dua kali di hari yang sama (dedup via `state/alert_state.json`, reset tiap hari).

## Jalankan lokal (opsional)

```bash
pip install -r requirements.txt
export TG_TOKEN=xxxx   # atau kosongkan untuk sekadar tulis dashboard tanpa kirim
export TG_CHAT=123456
python run_monitor.py
```

## Tuning

Semua di `CONFIG` (atas `zf_core.py`): `universe`, `weights`, `tp_R`, `ema_fast/slow`,
ambang `sharia_*`, `alert_*`, `scheduler_interval_min`.
Proxy komoditas ada di konstanta `PROXY` (sel macro): ganti ticker bila perlu; bila fetch gagal, otomatis fallback ke `macro_manual`.

## Yang wajib diketahui

- **Cron Actions bersifat best-effort** — bisa telat beberapa menit saat runner sibuk; bukan real-time presisi.
- **Kuota:** Actions gratis untuk repo publik; repo privat dapat jatah menit/bulan (cek billing). Beban di sini ringan.
- **Proxy ≠ harga komoditas asli** — arah trennya berkorelasi; untuk angka Newcastle/LME persis perlu sumber berbayar.
- **yfinance bisa rate-limit / kadang data tak lengkap.** Status "Perlu cek" = data laporan kurang, bukan berarti tidak syariah. Keanggotaan DES final tetap dicek di filter "Syariah" Bibit.
- **Jaga `TG_TOKEN` rahasia.** Jangan commit ke kode; pakai Secrets.
- **Bukan nasihat keuangan.** Level bersifat mekanis (EMA/ATR/struktur), bukan ramalan. Sesuaikan dengan horizon & profil risiko. Eksekusi beli/jual **manual di Bibit**.

---

## 📱 Pasang sebagai APLIKASI di HP (Android / Huawei) — PWA

Dashboard sudah jadi **Progressive Web App**: bisa di-"Add to Home Screen" dan tampil seperti aplikasi (ikon, layar penuh), di Android maupun Huawei — tanpa Play Store.

**Aktifkan GitHub Pages (sekali):**
1. Repo → **Settings → Pages** → Source: *Deploy from a branch* → Branch `main`, folder `/docs` → Save.
2. Tunggu ~1 menit. URL muncul: `https://<user>.github.io/<repo>/`.
3. Jalankan workflow sekali (tab **Actions** → Run workflow) agar `docs/index.html` terisi data.

**Pasang di HP:**
- **Android (Chrome):** buka URL di atas → menu ⋮ → **Add to Home screen / Install app**.
- **Huawei (browser bawaan / Chrome):** buka URL → menu → **Tambah ke layar utama**.
- **iPhone (Safari):** tombol Share → **Add to Home Screen**.

Ikon ZF (chart hijau + bulan sabit) akan muncul di layar utama. Buka = dashboard terbaru (di-update otomatis oleh GitHub Actions). Alert tetap via Telegram.

**Isi folder `docs/`** (jangan dihapus): `index.html` (dashboard, dibuat otomatis), `manifest.json`, `sw.js`, `icon-192.png`, `icon-512.png`, `apple-touch-icon.png`.

Catatan: butuh internet untuk data terbaru (network-first); versi terakhir tersimpan offline. Eksekusi beli/jual tetap manual di Bibit.
