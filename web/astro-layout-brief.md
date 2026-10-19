# Brief: Layout & UI Web Berita Gaming (Astro)

> Dokumen ini untuk AI agent. Baca seluruhnya sebelum menulis kode.
> **Aturan kerja: tampilkan RENCANA dulu (struktur file, keputusan desain, token warna), tunggu persetujuan, baru bangun kodenya.**

---

## 1. Konteks proyek

Situs berita gaming berbahasa Indonesia. Artikel dihasilkan otomatis oleh pipeline Python (Gemini) dan disimpan di Supabase tiap pagi 06:00 WIB. Web ini **hanya membaca** data tersebut dan merendernya jadi HTML statis.

- Framework: **Astro** (`output: "static"`), folder `web/` di dalam monorepo
- Hosting: Cloudflare Pages (build lewat deploy hook setelah pipeline harian)
- Bahasa konten dan UI: **Indonesia** (`<html lang="id">`, format tanggal `id-ID`)
- Target: pembaca mobile (mayoritas), trafik dari Google, monetisasi AdSense/affiliate nanti
- Tujuan utama desain: **nyaman dibaca, cepat dimuat, lolos review AdSense**

## 2. Yang sudah ada (jangan dibuat ulang)

File `web/src/lib/supabase.ts` sudah tersedia dengan:

```ts
interface Article { id; slug; title; content_html; source_link; source_name | null; published_at }
type ArticleSummary = Omit<Article, "content_html">
getArticles(limit = 50): Promise<ArticleSummary[]>
getArticleBySlug(slug): Promise<Article | null>
getAllSlugs(): Promise<{ slug; published_at }[]>
```

Env: `PUBLIC_SUPABASE_URL`, `PUBLIC_SUPABASE_ANON_KEY` (anon key, hanya baca).
**Jangan** memakai service key di folder `web/`. **Jangan** mengubah skema database.

Catatan data: `content_html` adalah HTML dari output AI (tag `<p>`, `<h2>`, dll). Tidak ada gambar dan tidak ada field kategori.

## 3. Deliverables

```
web/
├── astro.config.mjs            (site, sitemap integration, output static)
├── src/
│   ├── config.ts               (SITE_NAME, SITE_URL, SITE_DESC, kontak; placeholder jelas)
│   ├── styles/global.css       (design tokens, reset ringan, tipografi artikel)
│   ├── layouts/Base.astro      (head SEO, header, footer, slot)
│   ├── components/
│   │   ├── Header.astro
│   │   ├── Footer.astro
│   │   ├── ArticleCard.astro
│   │   ├── Pagination.astro
│   │   ├── SourceBox.astro     (atribusi sumber asli)
│   │   ├── AdSlot.astro        (placeholder, lihat bagian 8)
│   │   └── ThemeToggle.astro
│   ├── pages/
│   │   ├── index.astro                 (daftar terbaru, halaman 1)
│   │   ├── halaman/[page].astro        (pagination statis, halaman 2 dst)
│   │   ├── artikel/[slug].astro
│   │   ├── tentang.astro
│   │   ├── privasi.astro
│   │   ├── kontak.astro
│   │   ├── 404.astro
│   │   └── robots.txt.ts
│   └── utils/
│       ├── format.ts           (tanggal id-ID, waktu baca, excerpt)
│       └── sanitize.ts         (sanitize-html untuk content_html)
```

## 4. Arah desain: tema "gaming news", bersih dan mudah dibaca

Karakter: modern, sedikit gelap khas dunia gaming, tapi **teks panjang tetap nyaman**. Hindari gaya neon berlebihan yang melelahkan mata dan merusak keterbacaan.

**Mode warna**
- Default mengikuti sistem (`prefers-color-scheme`), dengan tombol toggle manual (simpan di `localStorage`, dibungkus try/catch).
- Cegah flash tema salah: script inline kecil di `<head>` yang menyetel `data-theme` sebelum render.
- Dua tema lengkap lewat CSS variables (jangan hardcode warna di komponen).

**Token warna (titik awal, boleh disetel selama kontras lolos)**

| Token | Gelap | Terang |
|---|---|---|
| `--bg` | `#0e1117` | `#f7f8fa` |
| `--surface` | `#161b24` | `#ffffff` |
| `--border` | `#262d3a` | `#e2e6ee` |
| `--text` | `#e6e9ef` | `#171b24` |
| `--text-muted` | `#9aa4b5` | `#566074` |
| `--accent` | `#7c5cff` (ungu) | `#5b3fe0` |
| `--accent-2` | `#22d3a6` (hijau mint, untuk highlight kecil) | `#0e9f7e` |

Aksen dipakai hemat: link, tombol, garis penanda, hover. Bukan sebagai warna latar besar.

**Tipografi**
- Pilih **salah satu**: (a) system font stack (nol request, paling ringan), atau (b) satu font variabel self-hosted format `woff2` dengan `font-display: swap` dan subset Latin. **Dilarang** memuat Google Fonts dari CDN.
- Judul: tebal, `line-height` 1.2 sampai 1.3. Badan artikel: 17 sampai 19px, `line-height` 1.7.
- Skala fluid memakai `clamp()`, tanpa banyak breakpoint.

**Teks artikel (class `.prose-article`)**
- Lebar baca maksimal **~68ch**, rata kiri (bukan justify).
- Styling `h2`, `h3`, `p`, `ul/ol`, `a`, `blockquote`, `strong`, `table` (scroll horizontal di mobile).
- Jarak antar paragraf lega, `h2` punya ruang atas yang jelas.

**Kartu artikel tanpa gambar**
Data tidak punya gambar dan **tidak boleh** memakai gambar milik sumber. Buat penanda visual dari CSS saja: strip warna aksen di sisi kiri, atau blok gradien kecil dari token (variasi bisa diturunkan dari hash slug). **Nol request gambar.**

## 5. UX yang harus ada

**Beranda**
- Hero ringkas (nama situs + satu kalimat deskripsi), bukan banner besar.
- Artikel terbaru: kartu pertama sedikit lebih menonjol, sisanya daftar/grid rapi 1 kolom (mobile) dan 2 sampai 3 kolom (desktop).
- Tiap kartu: judul, excerpt 2 sampai 3 baris (diambil dari `content_html` setelah tag dibuang), tanggal, nama sumber.
- Pagination statis (12 artikel per halaman), tautan "Sebelumnya/Berikutnya" yang jelas dan besar untuk jari.

**Halaman artikel**
- Judul (`h1`), tanggal terbit, perkiraan waktu baca, lalu isi.
- **SourceBox** di akhir isi: "Sumber berita: {source_name}" dengan link ke `source_link` (`rel="noopener nofollow"`, `target="_blank"`). Ini wajib.
- Navigasi "Berita lainnya" (3 artikel terbaru selain yang sedang dibuka).
- Breadcrumb ringan.
- Tombol salin tautan atau bagikan memakai `navigator.share` jika ada (progressive enhancement, JS kecil dan opsional).

**Navigasi global**
- Header lengket tipis: nama situs, tautan Beranda dan Tentang, toggle tema.
- Mobile: tanpa hamburger berat. Dengan 3 sampai 4 tautan, cukup tampil inline atau menu `<details>` tanpa JS.
- Footer: tautan Tentang, Privasi, Kontak, serta pernyataan singkat bahwa sebagian konten disusun dengan bantuan AI dan dirangkum dari sumber yang dicantumkan.

**Halaman wajib untuk AdSense**
- `/tentang`: siapa pengelola situs, bagaimana konten dibuat (jujur soal bantuan AI dan atribusi sumber).
- `/privasi`: kebijakan privasi (memuat bagian cookie dan iklan pihak ketiga, dengan placeholder yang jelas untuk diisi).
- `/kontak`: email kontak (placeholder di `config.ts`).
- Isi teks awal dibuat wajar dan siap disunting, bukan lorem ipsum.

## 6. Aksesibilitas

- Target **WCAG AA**: kontras teks minimal 4.5:1 di kedua tema.
- HTML semantik: `header`, `nav`, `main`, `article`, `footer`, satu `h1` per halaman.
- Tautan "Lewati ke konten" di paling atas.
- `:focus-visible` yang jelas untuk semua elemen interaktif.
- Area sentuh minimal 44px.
- Hormati `prefers-reduced-motion` (nonaktifkan transisi).
- `aria-label` pada tombol berikon, `aria-current="page"` pada navigasi aktif.

## 7. Efisiensi sumber daya (aturan keras)

- **Nol JavaScript framework di client.** Tidak ada React/Vue island. JS hanya skrip inline kecil untuk tema, dan opsional untuk tombol bagikan. Total JS client di bawah **3 KB**.
- **Nol gambar** pada beranda dan kartu. Ikon memakai SVG inline.
- **Nol font eksternal** (lihat tipografi).
- CSS total (setelah build) idealnya di bawah **20 KB** sebelum kompresi. Boleh memakai CSS biasa dengan variables, atau Tailwind v4 bila mau (hasil akhirnya tetap dipurge).
- Halaman statis penuh: HTML dihasilkan saat build, tidak ada fetch ke Supabase dari browser.
- Aktifkan `compressHTML: true` di Astro.
- Hindari layout shift: slot iklan dan elemen dinamis harus punya ukuran tetap (lihat bagian 8).
- Tambahkan `<link rel="preconnect">` hanya bila memang dipakai (jangan asal).

**Target Lighthouse (mobile) untuk halaman artikel:** Performance ≥ 95, Accessibility ≥ 95, Best Practices ≥ 95, SEO = 100.

## 8. Slot iklan (persiapan AdSense, belum aktif)

- Buat komponen `AdSlot.astro` yang **tidak memuat skrip apa pun**.
- Jika `config.ADS_ENABLED === false` (default), komponen tidak merender apa-apa.
- Jika aktif nanti, wadahnya memakai `min-height` tetap supaya tidak menggeser layout.
- Posisi yang disiapkan: setelah paragraf ke-2 artikel, dan sebelum SourceBox. **Jangan** menaruh iklan di atas judul atau menempel dengan tombol navigasi.
- Jangan menambahkan skrip AdSense sekarang. Akun belum disetujui.

## 9. SEO

Di `Base.astro`, terima props `title`, `description`, `canonical`, `type` (`website` atau `article`), `publishedTime`:

- `<title>` format `{judul} | {SITE_NAME}`, meta description (maks ~155 karakter, dari excerpt)
- `<link rel="canonical">` memakai `SITE_URL`
- Open Graph dan Twitter Card (tanpa gambar, `summary` bukan `summary_large_image`)
- JSON-LD `NewsArticle` di halaman artikel (`headline`, `datePublished`, `inLanguage: "id"`, `publisher`, dan `isBasedOn` yang menunjuk `source_link`)
- `@astrojs/sitemap` untuk `sitemap-index.xml`, serta `robots.txt` yang menunjuk ke sitemap
- Pagination memakai `rel="prev"/"next"` bila praktis
- Halaman 404 diberi `noindex`

## 10. Keamanan konten

`content_html` berasal dari AI, jadi **wajib disanitasi saat build** dengan `sanitize-html` sebelum dipakai di `set:html`:

- Izinkan hanya: `p, h2, h3, h4, ul, ol, li, strong, em, a, blockquote, br, table, thead, tbody, tr, th, td`
- Atribut: hanya `href` pada `a` (skema `http`/`https`), dan paksa `rel="noopener nofollow"` serta `target="_blank"` pada link eksternal
- Buang `script`, `style`, `iframe`, `img`, dan semua atribut event (`onclick`, dll)
- Jika artikel punya `<h1>` di dalam isi, turunkan menjadi `<h2>` agar halaman hanya punya satu `h1`

## 11. Larangan

- Jangan memakai gambar, logo, atau aset dari PCGamer/IGN/Wccftech.
- Jangan menyalin teks asli sumber.
- Jangan menambah dependensi besar (tidak ada framework UI, tidak ada library animasi, tidak ada ikon pack lengkap).
- Jangan memakai CDN pihak ketiga untuk CSS, font, atau skrip.
- Jangan membuat fitur komentar, login, atau pencarian sisi server pada tahap ini.
- Jangan menyentuh folder `scraping-data/` atau skema Supabase.

## 12. Kriteria selesai (checklist)

- [ ] `npm run build` sukses dan menghasilkan halaman statis untuk semua artikel di Supabase
- [ ] Beranda, pagination, detail artikel, Tentang, Privasi, Kontak, 404 semuanya berfungsi
- [ ] Dua tema berfungsi tanpa flash, dan pilihan tersimpan
- [ ] Tampilan nyaman di lebar 360px, 768px, dan 1280px (tanpa scroll horizontal)
- [ ] Kontras AA terpenuhi di kedua tema
- [ ] Navigasi keyboard penuh dan skip link berfungsi
- [ ] Sanitasi HTML aktif dan teruji (coba masukkan `<script>` ke data uji)
- [ ] SourceBox muncul di setiap artikel dengan link sumber yang benar
- [ ] Meta SEO, JSON-LD, sitemap, dan robots.txt valid
- [ ] Total JS client < 3 KB, tanpa request font/gambar/CDN eksternal
- [ ] Lighthouse mobile sesuai target di bagian 7
- [ ] `config.ts` berisi semua placeholder (nama situs, domain, email) di satu tempat

## 13. Urutan kerja yang diharapkan

1. **Rencana:** usulkan nama file, token desain final, dan pilihan font (system vs self-hosted). Tunggu persetujuan.
2. `config.ts`, `global.css` (token, tipografi, `.prose-article`), `Base.astro`.
3. Header, Footer, ThemeToggle.
4. ArticleCard, Pagination, lalu `index.astro` dan `halaman/[page].astro`.
5. `artikel/[slug].astro`, SourceBox, sanitasi, JSON-LD.
6. Halaman statis (Tentang, Privasi, Kontak, 404), `robots.txt`, sitemap.
7. AdSlot (nonaktif), audit Lighthouse dan aksesibilitas, lalu laporan hasil.
