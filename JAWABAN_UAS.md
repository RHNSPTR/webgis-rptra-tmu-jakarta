# 📝 JAWABAN UJIAN AKHIR SEMESTER — Sistem Informasi Geografis (SIG)

> **Nama:** Rehan Saputra
> **NIM:** 41523010065

> **Mata Kuliah:** Sistem Informasi Geografis (SIG)  
> **Jenis Tugas:** Ujian Akhir Semester (UAS)  
> **Topik:** Peta Interaktif Monitoring Kapasitas TMU & Aksesibilitas RPTRA di DKI Jakarta  
> **Bahasa Pemrograman:** Python (scikit-learn), QGIS Desktop, Streamlit + Folium

---

## PENDAHULUAN & SUMBER DATA (DISCLAIMER)

Aplikasi WebGIS dan algoritma Machine Learning yang dijelaskan dalam dokumen ini dibangun menggunakan pendekatan **Data Hibrida (*Hybrid Data*)**:
1. **Data Spasial (Real Data):** Titik koordinat (*Latitude/Longitude*) lokasi TMU dan RPTRA diekstraksi secara presisi dari dunia nyata menggunakan **OpenStreetMap** dan **Google Maps**.
2. **Data Atribut (Mock Data):** Untuk mendemonstrasikan kapabilitas analisis spasial, *geoprocessing* (buffer), *filtering*, dan klasifikasi Machine Learning, atribut pelengkap (seperti luas area, status kapasitas, kepadatan anak, persentase lahan kosong) digenerasi sebagai **Data Simulasi (Sintetik)** menggunakan pustaka Python `pandas` dan `numpy` dengan mengacu pada asumsi parameter logis wilayah DKI Jakarta.

---

## DAFTAR ISI

- [Bagian A — Spatial Feature Engineering di QGIS](#bagian-a--spatial-feature-engineering-di-qgis)
  - [A.1 Menghitung Jarak Minimal ke TMU untuk Setiap RW](#a1-menghitung-jarak-minimal-ke-tmu-untuk-setiap-rw)
  - [A.2 Menghitung Persentase Lahan Kosong di Setiap RW](#a2-menghitung-persentase-lahan-kosong-di-setiap-rw)
- [Bagian B — Implementasi Algoritma Random Forest](#bagian-b--implementasi-algoritma-random-forest)
- [Bagian C — Pemetaan Hasil & Kesimpulan](#bagian-c--pemetaan-hasil--kesimpulan)
  - [C.1 Ekspor & Join Hasil Prediksi ke Layer Vektor](#c1-ekspor--join-hasil-prediksi-ke-layer-vektor)
  - [C.2 Pengaturan Graduated/Categorized Symbology](#c2-pengaturan-graduatedcategorized-symbology)

---

## Bagian A — Spatial Feature Engineering di QGIS

### A.1 Menghitung Jarak Minimal ke TMU untuk Setiap RW

**Tujuan:** Menghitung jarak geodesik/planimetrik terdekat dari setiap titik centroid RW ke lokasi TMU terdekat. Fitur `Jarak_Minimal_ke_TMU` ini nantinya menjadi salah satu variabel prediktor dalam model Random Forest; semakin jauh suatu RW dari TMU, semakin layak dijadikan lokasi RPTRA baru (mempertimbangkan dampak lingkungan dan psikologis).

#### Langkah-Langkah di QGIS Desktop

**Prasyarat Layer:**

| No | Nama Layer | Tipe | Deskripsi |
|----|-----------|------|-----------|
| 1 | `Batas_RW_Jakarta.shp` | Poligon | Batas administrasi RW seluruh DKI Jakarta |
| 2 | `Lokasi_TMU.shp` | Titik | Lokasi titik koordinat seluruh TMU di Jakarta |

**Langkah 1 — Membuat Centroid RW (opsional jika layer sudah berupa titik)**

Jika layer RW berupa poligon, kita perlu mengekstrak titik pusat (centroid) terlebih dahulu agar perhitungan jarak menjadi point-to-point.

1. Buka **Processing Toolbox** → cari **"Centroids"**.
2. Atur parameter:
   - **Input layer:** `Batas_RW_Jakarta`
   - **Output:** `Centroid_RW` (simpan sebagai layer baru atau temporary)
3. Klik **Run**.

**Langkah 2 — Menghitung Jarak ke Hub Terdekat**

Tool yang digunakan: **Distance to nearest hub (points)** — tersedia di Processing Toolbox di bawah grup *Vector analysis*.

1. Buka **Processing Toolbox** → cari **"Distance to nearest hub (points)"**.
2. Atur parameter berikut:

   | Parameter | Nilai |
   |-----------|-------|
   | **Source points layer** | `Centroid_RW` (hasil Langkah 1) |
   | **Destination hubs layer** | `Lokasi_TMU` |
   | **Hub layer name attribute** | `Nama_TMU` (kolom nama di layer TMU) |
   | **Measurement unit** | `Meters` |
   | **Output shape type** | `Point` (atau `Line` jika ingin visualisasi garis penghubung) |
   | **Output** | `RW_dengan_Jarak_TMU` |

3. Klik **Run**.

**Hasil:** Layer output `RW_dengan_Jarak_TMU` akan memiliki dua kolom tambahan:
- `HubName` — Nama TMU terdekat.
- `HubDist` — Jarak dalam meter ke TMU terdekat.

**Langkah 3 — Rename Field**

1. Buka **Attribute Table** layer hasil → aktifkan mode **Edit** (ikon pensil).
2. Buka **Field Calculator** (ikon sempoa).
3. Buat field baru:
   - **Nama field baru:** `Jarak_Minimal_ke_TMU`
   - **Tipe:** `Decimal number (real)`
   - **Ekspresi:** `"HubDist"`
4. Simpan dan nonaktifkan mode edit.

> **Alternatif dengan GRASS GIS:**  
> Jika menggunakan `v.distance` melalui Processing Toolbox:
> 1. Cari **"v.distance"** di Processing Toolbox.
> 2. **from** = `Centroid_RW`, **to** = `Lokasi_TMU`, **output** = layer baru.
> 3. Kolom `dist` pada output berisi jarak minimum ke fitur terdekat.
> 4. Rename kolom `dist` menjadi `Jarak_Minimal_ke_TMU` via Field Calculator.

---

### A.2 Menghitung Persentase Lahan Kosong di Setiap RW

**Tujuan:** Menghitung rasio luas lahan kosong di dalam setiap RW terhadap total luas RW tersebut. Fitur `Persentase_Lahan_Kosong` menjadi variabel prediktor penting — RW dengan lahan kosong yang lebih banyak lebih berpotensi sebagai lokasi RPTRA baru.

#### Langkah-Langkah di QGIS Desktop

**Prasyarat Layer:**

| No | Nama Layer | Tipe | Deskripsi |
|----|-----------|------|-----------|
| 1 | `Batas_RW_Jakarta.shp` | Poligon | Batas administrasi RW |
| 2 | `Lahan_Kosong_Pemkot.shp` | Poligon | Sebaran lahan kosong milik Pemerintah Kota |

**Langkah 1 — Intersection (Irisan Spasial)**

Operasi *Intersection* akan memotong poligon lahan kosong mengikuti batas poligon RW sehingga setiap potongan lahan kosong mendapat atribut `ID_RW` dari RW yang melingkupinya.

1. Buka **Menu Vector** → **Geoprocessing Tools** → **Intersection** (atau via Processing Toolbox → cari "Intersection").
2. Atur parameter:

   | Parameter | Nilai |
   |-----------|-------|
   | **Input layer** | `Lahan_Kosong_Pemkot` |
   | **Overlay layer** | `Batas_RW_Jakarta` |
   | **Output** | `Irisan_Lahan_Kosong_per_RW` |

3. Klik **Run**.

**Hasil:** Layer `Irisan_Lahan_Kosong_per_RW` berisi potongan-potongan poligon lahan kosong, masing-masing dilengkapi atribut dari kedua layer asal (termasuk `ID_RW`).

**Langkah 2 — Hitung Luas Lahan Kosong per RW**

1. Buka **Processing Toolbox** → **"Statistics by categories"** (atau gunakan tool **"Dissolve"** + **Field Calculator**).

   **Cara Manual (Field Calculator):**
   1. Buka **Attribute Table** layer `Irisan_Lahan_Kosong_per_RW`.
   2. Aktifkan mode **Edit**.
   3. Buka **Field Calculator**, buat field baru:
      - **Nama:** `Luas_Irisan`
      - **Tipe:** `Decimal number (real)`
      - **Ekspresi:** `$area`
   4. Simpan.

2. Selanjutnya, gunakan **Processing Toolbox** → **"Statistics by categories"**:
   - **Input:** `Irisan_Lahan_Kosong_per_RW`
   - **Field to calculate statistics on:** `Luas_Irisan`
   - **Field(s) with categories:** `ID_RW`
   - Ini menghasilkan tabel statistik yang mencakup `sum` luas irisan per `ID_RW`.

   Atau gunakan **Dissolve**:
   1. **Processing Toolbox** → **"Dissolve"**
   2. **Input:** `Irisan_Lahan_Kosong_per_RW`
   3. **Dissolve field:** `ID_RW`
   4. Output: poligon gabungan per RW → hitung `$area` pada layer yang sudah di-dissolve.

**Langkah 3 — Join Luas Irisan ke Layer RW & Hitung Persentase**

1. Klik kanan layer `Batas_RW_Jakarta` → **Properties** → tab **Joins**.
2. Tambahkan Join baru:
   - **Join layer:** Tabel statistik (atau layer dissolve) dari Langkah 2.
   - **Join field:** `ID_RW`
   - **Target field:** `ID_RW`
3. Klik **OK**.

4. Buka **Field Calculator** pada `Batas_RW_Jakarta`:
   - **Nama field baru:** `Persentase_Lahan_Kosong`
   - **Tipe:** `Decimal number (real)`
   - **Ekspresi:**

   ```
   ( "statistik_sum_Luas_Irisan" / $area ) * 100
   ```

   > **Catatan:** Pastikan kedua layer menggunakan CRS yang sama dan bersifat *projected* (misalnya EPSG:32748 — UTM 48S) agar perhitungan `$area` menghasilkan satuan meter persegi yang akurat. Jika masih dalam WGS84 (EPSG:4326), lakukan **Reproject** terlebih dahulu.

5. Simpan dan nonaktifkan mode edit.

**Validasi:**
- Pastikan nilai `Persentase_Lahan_Kosong` berada dalam rentang **0–100**.
- RW tanpa lahan kosong (tidak ada irisan) akan bernilai `NULL`; ganti dengan `0` menggunakan ekspresi: `coalesce("Persentase_Lahan_Kosong", 0)`.

---

## Bagian B — Implementasi Algoritma Random Forest

Pada iterasi terbaru aplikasi ini, algoritma **Random Forest** telah **diintegrasikan secara langsung (Live Pipeline) ke dalam Dashboard WebGIS Streamlit (`app.py`) pada Tab 2**. Ini memungkinkan pengguna untuk melihat hasil pelatihan model, akurasi, dan *Feature Importance* secara interaktif, serta melakukan simulasi prediksi untuk RW baru.

### Skrip Python: Integrasi ML di dalam Streamlit (`app.py`)

Berikut adalah inti potongan kode (snippet) yang digunakan di dalam `app.py` (Tab 2) untuk membangun *Live Pipeline* Random Forest:

```python
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 1. Dataset Simulasi Tingkat RW (Mock Data Spasial & Atribut)
np.random.seed(42)
n_samples = 20

data_rw = {
    "ID_RW": [f"RW-{str(i).zfill(3)}" for i in range(1, n_samples + 1)],
    "Nama_RW": [f"RW {i:02d} Kel. Simulasi" for i in range(1, n_samples + 1)],
    "Wilayah_Administrasi": np.random.choice(["Jakarta Pusat", "Jakarta Selatan", "Jakarta Barat", "Jakarta Timur", "Jakarta Utara"], n_samples),
    "Jarak_Minimal_ke_TMU": np.random.randint(100, 2500, n_samples),
    "Persentase_Lahan_Kosong": np.random.randint(5, 80, n_samples),
    "Kepadatan_Penduduk_Anak": np.random.randint(500, 5000, n_samples),
}
df_rw = pd.DataFrame(data_rw)

# Penentuan Label Prioritas berdasarkan aturan logika simulasi
# 2 = Sangat Prioritas, 1 = Cukup Prioritas, 0 = Tidak Prioritas
def assign_label(row):
    if row["Jarak_Minimal_ke_TMU"] <= 500 or row["Persentase_Lahan_Kosong"] <= 15:
        return 0
    elif row["Persentase_Lahan_Kosong"] > 30 and row["Kepadatan_Penduduk_Anak"] > 2000:
        return 2
    else:
        return 1

df_rw["Label_Prioritas"] = df_rw.apply(assign_label, axis=1)

# 2. Pelatihan Model Machine Learning (Live Pipeline)
X = df_rw[["Jarak_Minimal_ke_TMU", "Persentase_Lahan_Kosong", "Kepadatan_Penduduk_Anak"]]
y = df_rw["Label_Prioritas"]

# Membagi data menjadi 80% Training dan 20% Test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Inisialisasi dan Pelatihan Model Random Forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Evaluasi Model
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
st.metric("Skor Akurasi Model (Accuracy Score)", f"{accuracy * 100:.2f}%")

# Feature Importance
importances = rf_model.feature_importances_
df_importances = pd.DataFrame({
    "Fitur": X.columns,
    "Tingkat Kepentingan": importances
}).set_index("Fitur")
st.bar_chart(df_importances, horizontal=True)

# 3. Simulasi Prediksi RW Baru
if st.button("🚀 Simulasikan Prediksi RW Baru"):
    new_data = pd.DataFrame({
        "ID_RW": ["RW-901", "RW-902", "RW-903", "RW-904"],
        "Nama_RW": ["RW 01 Pegangsaan", "RW 04 Cilandak", "RW 07 Pluit", "RW 12 Kalideres"],
        "Wilayah_Administrasi": ["Jakarta Pusat", "Jakarta Selatan", "Jakarta Utara", "Jakarta Barat"],
        "Jarak_Minimal_ke_TMU": [1200, 450, 2500, 1500],
        "Persentase_Lahan_Kosong": [45, 60, 10, 35],
        "Kepadatan_Penduduk_Anak": [3500, 4200, 800, 2200]
    })
    
    X_new = new_data[["Jarak_Minimal_ke_TMU", "Persentase_Lahan_Kosong", "Kepadatan_Penduduk_Anak"]]
    new_data["Prediksi_Prioritas"] = rf_model.predict(X_new)
    st.dataframe(new_data)
```

### Penjelasan Kode & Pipeline

| Komponen | Deskripsi |
|---------|-----------|
| **Impor Library** | Menggunakan `scikit-learn` untuk pipeline ML, `pandas` & `numpy` untuk Dataframe/Simulasi, dan `streamlit` untuk render antarmuka. |
| **Simulasi Dataset RW** | Karena ketiadaan data lapangan yang lengkap, script mensimulasikan 20 baris data RW dengan fitur `Jarak_Minimal_ke_TMU`, `Persentase_Lahan_Kosong`, dan `Kepadatan_Penduduk_Anak` menggunakan `numpy.random`. |
| **Penentuan Label (Ground Truth)** | Menggunakan fungsi kondisional (`assign_label`) untuk melabeli data training sebagai `0` (Tidak Prioritas), `1` (Cukup Prioritas), dan `2` (Sangat Prioritas). |
| **Pembagian Data** | `train_test_split` membagi dataset menjadi 80% data latih (training) dan 20% data uji (testing). |
| **Pelatihan Model** | Algoritma `RandomForestClassifier` dilatih menggunakan `n_estimators=100` (100 pohon keputusan). |
| **Evaluasi (Akurasi & Fitur)** | Model diuji dan akurasinya ditampilkan secara live di Streamlit via `st.metric`. Chart Feature Importance (kontribusi setiap fitur spasial) dimunculkan via `st.bar_chart`. |
| **Simulasi Interaktif** | Pengguna dapat menekan tombol prediksi untuk memasukkan *unseen data* (Data RW Baru) ke dalam model yang sudah dilatih dan melihat hasil prediksinya langsung dalam bentuk tabel yang diwarnai secara otomatis oleh Streamlit. |

---

## Bagian C — Pemetaan Hasil & Kesimpulan

### C.1 Ekspor & Join Hasil Prediksi ke Layer Vektor

Setelah model Random Forest menghasilkan prediksi label prioritas untuk seluruh RW dan diekspor sebagai file CSV (`prediksi_prioritas_rptra.csv`), langkah berikutnya adalah menghubungkan (join) hasil prediksi tersebut kembali ke master layer vektor `Batas_RW_Jakarta.shp` di QGIS.

#### Langkah-Langkah Join Atribut di QGIS

**Langkah 1 — Memuat File CSV ke QGIS**

1. Buka QGIS → klik menu **Layer** → **Add Layer** → **Add Delimited Text Layer…**
2. Atur parameter:
   - **File name:** Arahkan ke file `prediksi_prioritas_rptra.csv`.
   - **File format:** CSV
   - **Geometry definition:** Pilih **"No geometry (attribute only table)"** karena file ini hanya berisi data tabel tanpa koordinat.
   - **Encoding:** UTF-8
3. Klik **Add** → Klik **Close**.

> File CSV akan muncul sebagai layer tabel (tanpa geometri) di panel Layers.

**Langkah 2 — Melakukan Join Atribut**

1. Klik kanan pada layer `Batas_RW_Jakarta` di panel Layers → pilih **Properties**.
2. Buka tab **Joins** (ikon rantai 🔗).
3. Klik tombol **➕ (tambah join baru)** di bagian bawah.
4. Isi formulir Join:

   | Parameter | Nilai |
   |-----------|-------|
   | **Join layer** | `prediksi_prioritas_rptra` (layer CSV yang baru dimuat) |
   | **Join field** | `ID_RW` (kolom kunci di CSV) |
   | **Target field** | `ID_RW` (kolom kunci di layer Batas_RW) |
   | **Joined fields** | Centang `Prediksi_Prioritas` dan `Label_Teks` |
   | **Custom field name prefix** | Kosongkan atau isi `pred_` (opsional) |

5. Klik **OK** → **OK**.

**Langkah 3 — Verifikasi Hasil Join**

1. Buka **Attribute Table** layer `Batas_RW_Jakarta`.
2. Pastikan kolom baru (`Prediksi_Prioritas` dan `Label_Teks`) telah muncul dengan nilai yang sesuai.
3. Pastikan tidak ada nilai `NULL` pada kolom join (menandakan semua `ID_RW` berhasil dicocokkan).

**Langkah 4 — Menyimpan Hasil Join secara Permanen (Opsional)**

Karena join di QGIS bersifat *virtual* (hanya tautan sementara), sebaiknya simpan sebagai layer baru:

1. Klik kanan layer `Batas_RW_Jakarta` → **Export** → **Save Features As…**
2. Pilih format **ESRI Shapefile** atau **GeoPackage**.
3. Nama file: `Batas_RW_dengan_Prediksi.shp` (atau `.gpkg`).
4. Pastikan kolom join termasuk dalam field yang diekspor.
5. Klik **OK**.

---

### C.2 Pengaturan Graduated/Categorized Symbology

Setelah hasil prediksi berhasil di-join ke layer vektor, kita visualisasikan hasilnya menggunakan simbologi berwarna sehingga peta secara visual menunjukkan zona prioritas pembangunan RPTRA.

#### Langkah-Langkah Mengatur Categorized Symbology

1. Klik kanan layer `Batas_RW_dengan_Prediksi` → **Properties** → tab **Symbology**.

2. Pada dropdown di bagian atas, ubah dari **"Single Symbol"** menjadi **"Categorized"**.

3. Atur parameter:
   - **Column (Value):** Pilih field `Prediksi_Prioritas` (atau `Label_Teks`).
   - Klik tombol **Classify** di bagian bawah.

4. QGIS akan secara otomatis mendeteksi nilai unik. Atur warna sesuai aturan berikut:

   | Nilai `Prediksi_Prioritas` | Label Teks | Warna | Kode Hex |
   |:-:|:--|:--|:--|
   | **2** | Sangat Prioritas | 🟢 **Hijau** | `#28a745` |
   | **1** | Cukup Prioritas | 🟡 **Kuning** | `#ffc107` |
   | **0** | Tidak Prioritas | 🔴 **Merah** | `#dc3545` |

5. Untuk mengganti warna setiap kategori:
   - Klik dua kali pada simbol warna di samping setiap kategori.
   - Pada dialog **Symbol Selector**, ubah **Fill color** sesuai tabel di atas.
   - Atur **Opacity** menjadi ~70% agar layer di bawahnya tetap terlihat.
   - Atur **Stroke color** menjadi lebih gelap dari fill (misalnya abu-abu `#333`).
   - Klik **OK**.

6. (Opsional) Edit label yang ditampilkan di legenda:
   - Klik dua kali pada teks label di kolom **Legend**.
   - Ubah label menjadi deskripsi yang lebih jelas, misalnya:
     - `2` → `Sangat Prioritas (Hijau)`
     - `1` → `Cukup Prioritas (Kuning)`
     - `0` → `Tidak Prioritas (Merah)`

7. Klik **Apply** → **OK**.

#### Alternatif: Graduated Symbology

Jika menggunakan **Graduated Symbology** (untuk data numerik kontinu):
1. Pilih **"Graduated"** pada dropdown renderer.
2. **Column:** `Prediksi_Prioritas`
3. **Mode:** `Equal Interval` atau `Manual`
4. Tentukan 3 kelas:
   - `0.0 – 0.5` → Merah (Tidak Prioritas)
   - `0.5 – 1.5` → Kuning (Cukup Prioritas)
   - `1.5 – 2.0` → Hijau (Sangat Prioritas)
5. Klik **Apply** → **OK**.

> **Rekomendasi:** Gunakan **Categorized Symbology** karena label prioritas bersifat diskret (0, 1, 2), bukan kontinu. Graduated lebih tepat untuk data numerik kontinu seperti kepadatan penduduk.

---

### Kesimpulan

Proses lengkap dari analisis spasial hingga pemodelan Machine Learning untuk pemilihan lokasi optimal RPTRA baru dapat dirangkum sebagai berikut:

```
┌─────────────────────────────────────────────────────────────────┐
│                     ALUR KERJA KESELURUHAN                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. FEATURE ENGINEERING (QGIS)                                  │
│     ├── Hitung Jarak_Minimal_ke_TMU  ← Distance to nearest hub │
│     └── Hitung Persentase_Lahan_Kosong ← Intersection + $area  │
│                          │                                      │
│                          ▼                                      │
│  2. EKSPOR ATRIBUT RW → CSV                                    │
│                          │                                      │
│                          ▼                                      │
│  3. TRAINING MODEL (Python/scikit-learn)                        │
│     ├── Fitur X: Jarak TMU, Lahan Kosong, Kepadatan Anak       │
│     ├── Target y: Label_Prioritas (0, 1, 2)                    │
│     ├── Split 80/20 stratified                                  │
│     ├── RandomForestClassifier(n_estimators=100)                │
│     └── Evaluasi: Akurasi, Confusion Matrix, Feature Importance │
│                          │                                      │
│                          ▼                                      │
│  4. EKSPOR PREDIKSI → CSV                                      │
│                          │                                      │
│                          ▼                                      │
│  5. JOIN KE LAYER VEKTOR (QGIS)                                │
│     └── Join atribut via ID_RW                                  │
│                          │                                      │
│                          ▼                                      │
│  6. VISUALISASI PETA PRIORITAS (QGIS / WebGIS)                 │
│     └── Categorized Symbology:                                  │
│         🟢 Hijau = Sangat Prioritas                             │
│         🟡 Kuning = Cukup Prioritas                             │
│         🔴 Merah = Tidak Prioritas                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Dengan pendekatan ini, pengambilan keputusan pembangunan RPTRA baru didasarkan pada:

1. **Analisis spasial** — memastikan RPTRA tidak dibangun terlalu dekat dengan TMU (dampak psikologis dan lingkungan).
2. **Ketersediaan lahan** — RW dengan persentase lahan kosong tinggi lebih realistis untuk dibangun.
3. **Kebutuhan masyarakat** — kepadatan penduduk anak menjadi indikator kebutuhan ruang publik ramah anak.
4. **Machine Learning** — model Random Forest mengintegrasikan ketiga variabel tersebut secara simultan untuk menghasilkan rekomendasi yang objektif dan data-driven.

---

> **Catatan Akhir:** Seluruh kode program, peta interaktif, dan analisis di atas merupakan bagian dari tugas Ujian Akhir Semester (UAS) mata kuliah Sistem Informasi Geografis. Kode aplikasi WebGIS (`app.py`) dapat langsung di-deploy ke Streamlit Cloud dengan mengunggah repository berisi `app.py` dan `requirements.txt` ke GitHub.
