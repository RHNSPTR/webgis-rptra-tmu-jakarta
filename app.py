"""
=============================================================================
 Peta Interaktif Monitoring Kapasitas Taman Makam Umum (TMU)
 dan Aksesibilitas RPTRA di DKI Jakarta
=============================================================================
 Nama         : Rehan Saputra   
 NIM          : 41523010065   
 Mata Kuliah  : Sistem Informasi Geografis (SIG)
 Tugas        : Ujian Akhir Semester (UAS)
 Teknologi    : Streamlit · Folium · GeoPandas · Shapely · Pandas
 Deskripsi    : Aplikasi WebGIS interaktif untuk monitoring kapasitas TMU
                dan aksesibilitas RPTRA di wilayah DKI Jakarta dengan
                visualisasi kartografis, buffer analisis, serta
                filter spasial dinamis.
=============================================================================
"""

# ─────────────────────────────────────────────
# 1. IMPOR LIBRARY
# ─────────────────────────────────────────────
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# ─────────────────────────────────────────────
# 2. KONFIGURASI HALAMAN STREAMLIT
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Peta Monitoring TMU & RPTRA – DKI Jakarta",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 3. STYLING CSS KUSTOM
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Header utama */
    .main-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1a1a2e;
        text-align: center;
        padding: 0.5rem 0;
        border-bottom: 3px solid #e94560;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #555;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    /* Ringkasan */
    .exec-summary {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8ecf5 100%);
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        padding: 16px 20px;
        font-size: 0.92rem;
        color: #333;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# 4. DATA SIMULASI (MOCK DATA)
# ─────────────────────────────────────────────
@st.cache_data
def buat_data_tmu() -> gpd.GeoDataFrame:
    """
    Membuat data simulasi Taman Makam Umum (TMU) di DKI Jakarta.
    12 titik tersebar di 5 wilayah administrasi dengan koordinat akurat.
    """
    data = [
        # ── Jakarta Pusat (2 TMU) ──
        {
            "Nama_TMU": "TPU Karet Bivak",
            "Luas_Area_m2": 94000,
            "Status_Kapasitas": "Kritis",
            "Tahun_Berdiri": 1918,
            "Wilayah_Administrasi": "Jakarta Pusat",
            "Kapasitas_Persen": 5,
            "latitude": -6.2030,
            "longitude": 106.8137,
        },
        {
            "Nama_TMU": "TPU Menteng Pulo",
            "Luas_Area_m2": 52000,
            "Status_Kapasitas": "Kritis",
            "Tahun_Berdiri": 1942,
            "Wilayah_Administrasi": "Jakarta Pusat",
            "Kapasitas_Persen": 3,
            "latitude": -6.2223,
            "longitude": 106.8369,
        },
        # ── Jakarta Selatan (3 TMU) ──
        {
            "Nama_TMU": "TPU Jeruk Purut",
            "Luas_Area_m2": 147000,
            "Status_Kapasitas": "Kritis",
            "Tahun_Berdiri": 1954,
            "Wilayah_Administrasi": "Jakarta Selatan",
            "Kapasitas_Persen": 8,
            "latitude": -6.2799,
            "longitude": 106.8129,
        },
        {
            "Nama_TMU": "TPU Tanah Kusir",
            "Luas_Area_m2": 78000,
            "Status_Kapasitas": "Tersedia",
            "Tahun_Berdiri": 1965,
            "Wilayah_Administrasi": "Jakarta Selatan",
            "Kapasitas_Persen": 15,
            "latitude": -6.2528,
            "longitude": 106.7678,
        },
        {
            "Nama_TMU": "TPU Pondok Labu",
            "Luas_Area_m2": 63000,
            "Status_Kapasitas": "Tersedia",
            "Tahun_Berdiri": 1988,
            "Wilayah_Administrasi": "Jakarta Selatan",
            "Kapasitas_Persen": 22,
            "latitude": -6.3049,
            "longitude": 106.7909,
        },
        # ── Jakarta Timur (3 TMU) ──
        {
            "Nama_TMU": "TPU Pondok Ranggon",
            "Luas_Area_m2": 345000,
            "Status_Kapasitas": "Tersedia",
            "Tahun_Berdiri": 1990,
            "Wilayah_Administrasi": "Jakarta Timur",
            "Kapasitas_Persen": 42,
            "latitude": -6.3598,
            "longitude": 106.9115,
        },
        {
            "Nama_TMU": "TPU Penggilingan",
            "Luas_Area_m2": 88000,
            "Status_Kapasitas": "Tersedia",
            "Tahun_Berdiri": 2005,
            "Wilayah_Administrasi": "Jakarta Timur",
            "Kapasitas_Persen": 60,
            "latitude": -6.1972,
            "longitude": 106.8988,
        },
        {
            "Nama_TMU": "TPU Cipayung",
            "Luas_Area_m2": 55000,
            "Status_Kapasitas": "Kritis",
            "Tahun_Berdiri": 1972,
            "Wilayah_Administrasi": "Jakarta Timur",
            "Kapasitas_Persen": 7,
            "latitude": -6.3595,
            "longitude": 106.9086,
        },
        # ── Jakarta Utara (2 TMU) ──
        {
            "Nama_TMU": "TPU Semper",
            "Luas_Area_m2": 210000,
            "Status_Kapasitas": "Tersedia",
            "Tahun_Berdiri": 1978,
            "Wilayah_Administrasi": "Jakarta Utara",
            "Kapasitas_Persen": 25,
            "latitude": -6.1264,
            "longitude": 106.9208,
        },
        {
            "Nama_TMU": "TPU Rorotan",
            "Luas_Area_m2": 180000,
            "Status_Kapasitas": "Tersedia",
            "Tahun_Berdiri": 2010,
            "Wilayah_Administrasi": "Jakarta Utara",
            "Kapasitas_Persen": 68,
            "latitude": -6.1517,
            "longitude": 106.9685,
        },
        # ── Jakarta Barat (2 TMU) ──
        {
            "Nama_TMU": "TPU Tegal Alur",
            "Luas_Area_m2": 120000,
            "Status_Kapasitas": "Tersedia",
            "Tahun_Berdiri": 2001,
            "Wilayah_Administrasi": "Jakarta Barat",
            "Kapasitas_Persen": 55,
            "latitude": -6.1081,
            "longitude": 106.7063,
        },
        {
            "Nama_TMU": "TPU Cengkareng",
            "Luas_Area_m2": 72000,
            "Status_Kapasitas": "Kritis",
            "Tahun_Berdiri": 1960,
            "Wilayah_Administrasi": "Jakarta Barat",
            "Kapasitas_Persen": 9,
            "latitude": -6.1486,
            "longitude": 106.7704,
        },
    ]
    df = pd.DataFrame(data)
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    return gdf


@st.cache_data
def buat_data_rptra() -> gpd.GeoDataFrame:
    """
    Membuat data simulasi Ruang Publik Terpadu Ramah Anak (RPTRA)
    di DKI Jakarta dengan koordinat akurat berdasarkan OSM.
    """
    data = [
        # ── Jakarta Barat (4 RPTRA) ──
        {
            "Nama_RPTRA": "RPTRA Kalijodo",
            "Fasilitas_Utama": "Playground",
            "Kondisi": "Lengkap",
            "Wilayah_Administrasi": "Jakarta Barat",
            "latitude": -6.1402,
            "longitude": 106.7886,
        },
        {
            "Nama_RPTRA": "RPTRA Kembangan",
            "Fasilitas_Utama": "Biopori",
            "Kondisi": "Terbatas",
            "Wilayah_Administrasi": "Jakarta Barat",
            "latitude": -6.1751,
            "longitude": 106.7326,
        },
        {
            "Nama_RPTRA": "RPTRA Cengkareng Barat",
            "Fasilitas_Utama": "Perpustakaan",
            "Kondisi": "Lengkap",
            "Wilayah_Administrasi": "Jakarta Barat",
            "latitude": -6.1238,
            "longitude": 106.7309,
        },
        {
            "Nama_RPTRA": "RPTRA Palmerah",
            "Fasilitas_Utama": "Playground",
            "Kondisi": "Terbatas",
            "Wilayah_Administrasi": "Jakarta Barat",
            "latitude": -6.1941,
            "longitude": 106.7943,
        },
        # ── Jakarta Pusat (4 RPTRA) ──
        {
            "Nama_RPTRA": "RPTRA Gondangdia",
            "Fasilitas_Utama": "Perpustakaan",
            "Kondisi": "Lengkap",
            "Wilayah_Administrasi": "Jakarta Pusat",
            "latitude": -6.1946,
            "longitude": 106.8384,
        },
        {
            "Nama_RPTRA": "RPTRA Amir Hamzah",
            "Fasilitas_Utama": "Playground",
            "Kondisi": "Lengkap",
            "Wilayah_Administrasi": "Jakarta Pusat",
            "latitude": -6.2034,
            "longitude": 106.8504,
        },
        {
            "Nama_RPTRA": "RPTRA Kenari",
            "Fasilitas_Utama": "Biopori",
            "Kondisi": "Terbatas",
            "Wilayah_Administrasi": "Jakarta Pusat",
            "latitude": -6.1944,
            "longitude": 106.8488,
        },
        {
            "Nama_RPTRA": "RPTRA Tanah Abang",
            "Fasilitas_Utama": "Playground",
            "Kondisi": "Lengkap",
            "Wilayah_Administrasi": "Jakarta Pusat",
            "latitude": -6.1831,
            "longitude": 106.8172,
        },
        # ── Jakarta Selatan (4 RPTRA) ──
        {
            "Nama_RPTRA": "RPTRA Manunggal",
            "Fasilitas_Utama": "Perpustakaan",
            "Kondisi": "Terbatas",
            "Wilayah_Administrasi": "Jakarta Selatan",
            "latitude": -6.2438,
            "longitude": 106.7472,
        },
        {
            "Nama_RPTRA": "RPTRA Tebet",
            "Fasilitas_Utama": "Playground",
            "Kondisi": "Lengkap",
            "Wilayah_Administrasi": "Jakarta Selatan",
            "latitude": -6.2352,
            "longitude": 106.8531,
        },
        {
            "Nama_RPTRA": "RPTRA Jagakarsa",
            "Fasilitas_Utama": "Biopori",
            "Kondisi": "Terbatas",
            "Wilayah_Administrasi": "Jakarta Selatan",
            "latitude": -6.3301,
            "longitude": 106.8226,
        },
        {
            "Nama_RPTRA": "RPTRA Kebayoran Lama",
            "Fasilitas_Utama": "Perpustakaan",
            "Kondisi": "Lengkap",
            "Wilayah_Administrasi": "Jakarta Selatan",
            "latitude": -6.2135,
            "longitude": 106.7871,
        },
        # ── Jakarta Timur (4 RPTRA) ──
        {
            "Nama_RPTRA": "RPTRA Cililitan",
            "Fasilitas_Utama": "Biopori",
            "Kondisi": "Terbatas",
            "Wilayah_Administrasi": "Jakarta Timur",
            "latitude": -6.2661,
            "longitude": 106.8563,
        },
        {
            "Nama_RPTRA": "RPTRA Cipinang",
            "Fasilitas_Utama": "Perpustakaan",
            "Kondisi": "Terbatas",
            "Wilayah_Administrasi": "Jakarta Timur",
            "latitude": -6.2174,
            "longitude": 106.8825,
        },
        {
            "Nama_RPTRA": "RPTRA Duren Sawit",
            "Fasilitas_Utama": "Playground",
            "Kondisi": "Lengkap",
            "Wilayah_Administrasi": "Jakarta Timur",
            "latitude": -6.2264,
            "longitude": 106.9025,
        },
        {
            "Nama_RPTRA": "RPTRA Pulogadung",
            "Fasilitas_Utama": "Biopori",
            "Kondisi": "Lengkap",
            "Wilayah_Administrasi": "Jakarta Timur",
            "latitude": -6.1980,
            "longitude": 106.8816,
        },
        # ── Jakarta Utara (4 RPTRA) ──
        {
            "Nama_RPTRA": "RPTRA Bahari",
            "Fasilitas_Utama": "Playground",
            "Kondisi": "Lengkap",
            "Wilayah_Administrasi": "Jakarta Utara",
            "latitude": -6.1085,
            "longitude": 106.8643,
        },
        {
            "Nama_RPTRA": "RPTRA Sunter Jaya",
            "Fasilitas_Utama": "Playground",
            "Kondisi": "Lengkap",
            "Wilayah_Administrasi": "Jakarta Utara",
            "latitude": -6.1549,
            "longitude": 106.8733,
        },
        {
            "Nama_RPTRA": "RPTRA Kelapa Gading",
            "Fasilitas_Utama": "Perpustakaan",
            "Kondisi": "Lengkap",
            "Wilayah_Administrasi": "Jakarta Utara",
            "latitude": -6.1661,
            "longitude": 106.9071,
        },
        {
            "Nama_RPTRA": "RPTRA Penjaringan",
            "Fasilitas_Utama": "Biopori",
            "Kondisi": "Terbatas",
            "Wilayah_Administrasi": "Jakarta Utara",
            "latitude": -6.1341,
            "longitude": 106.7962,
        },
    ]
    df = pd.DataFrame(data)
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    return gdf


# ─────────────────────────────────────────────
# 5. FUNGSI UTILITAS BUFFER 500 m
# ─────────────────────────────────────────────
@st.cache_data
def buat_buffer_tmu(_gdf_tmu: gpd.GeoDataFrame, radius_m: int = 500) -> gpd.GeoDataFrame:
    """
    Membuat poligon buffer dengan radius tertentu (default 500 m) di
    sekeliling setiap titik TMU.  Proses:
      1. Proyeksikan ke CRS metrik (EPSG:32748 – UTM 48S untuk Jakarta).
      2. Hitung buffer dalam satuan meter.
      3. Konversi kembali ke WGS84 (EPSG:4326).
    """
    # Proyeksi ke sistem koordinat metrik (UTM zona 48S)
    gdf_proj = _gdf_tmu.to_crs(epsg=32748)
    gdf_proj["geometry"] = gdf_proj.geometry.buffer(radius_m)
    # Kembalikan ke WGS84 untuk Folium
    gdf_buffer = gdf_proj.to_crs(epsg=4326)
    return gdf_buffer


# ─────────────────────────────────────────────
# 6. FUNGSI WARNA PENANDA BERDASARKAN KAPASITAS
# ─────────────────────────────────────────────
def warna_kapasitas(persen: int) -> str:
    """
    Menentukan warna penanda TMU berdasarkan Kapasitas_Persen:
      - Hijau  : > 30 %  (masih tersedia cukup)
      - Kuning : 10–30 % (menipis)
      - Merah  : < 10 %  (kritis)
    """
    if persen > 30:
        return "green"
    elif persen >= 10:
        return "orange"  # Folium 'orange' tampil kuning-oranye
    else:
        return "red"


def warna_rptra(kondisi: str) -> str:
    """
    Menentukan warna penanda RPTRA berdasarkan Kondisi:
      - Biru  : Lengkap
      - Ungu  : Terbatas
    """
    return "blue" if kondisi == "Lengkap" else "purple"


# ─────────────────────────────────────────────
# 7. FUNGSI PEMBUATAN POP-UP HTML
# ─────────────────────────────────────────────
def popup_tmu(row: pd.Series) -> folium.Popup:
    """Membuat pop-up HTML informatif untuk marker TMU."""
    # Tentukan badge warna sesuai kapasitas
    badge_color = warna_kapasitas(row["Kapasitas_Persen"])
    html = f"""
    <div style="font-family:Arial,sans-serif; width:260px;">
        <h4 style="margin:0 0 6px; color:#1a1a2e;">{row['Nama_TMU']}</h4>
        <table style="font-size:13px; border-collapse:collapse; width:100%;">
            <tr><td style="padding:3px 6px; font-weight:600;">Luas Area</td>
                <td style="padding:3px 6px;">{row['Luas_Area_m2']:,} m²</td></tr>
            <tr style="background:#f9f9f9;">
                <td style="padding:3px 6px; font-weight:600;">Tahun Berdiri</td>
                <td style="padding:3px 6px;">{row['Tahun_Berdiri']}</td></tr>
            <tr><td style="padding:3px 6px; font-weight:600;">Wilayah</td>
                <td style="padding:3px 6px;">{row['Wilayah_Administrasi']}</td></tr>
            <tr style="background:#f9f9f9;">
                <td style="padding:3px 6px; font-weight:600;">Status</td>
                <td style="padding:3px 6px;">
                    <span style="background:{badge_color}; color:white;
                    padding:2px 8px; border-radius:10px; font-size:12px;">
                    {row['Status_Kapasitas']}</span></td></tr>
            <tr><td style="padding:3px 6px; font-weight:600;">Kapasitas</td>
                <td style="padding:3px 6px; font-weight:700;">{row['Kapasitas_Persen']}%</td></tr>
        </table>
    </div>
    """
    return folium.Popup(html, max_width=300)


def popup_rptra(row: pd.Series) -> folium.Popup:
    """Membuat pop-up HTML informatif untuk marker RPTRA."""
    kondisi_color = "#3b82f6" if row["Kondisi"] == "Lengkap" else "#8b5cf6"
    html = f"""
    <div style="font-family:Arial,sans-serif; width:250px;">
        <h4 style="margin:0 0 6px; color:#1a1a2e;">{row['Nama_RPTRA']}</h4>
        <table style="font-size:13px; border-collapse:collapse; width:100%;">
            <tr><td style="padding:3px 6px; font-weight:600;">Fasilitas Utama</td>
                <td style="padding:3px 6px;">{row['Fasilitas_Utama']}</td></tr>
            <tr style="background:#f9f9f9;">
                <td style="padding:3px 6px; font-weight:600;">Kondisi</td>
                <td style="padding:3px 6px;">
                    <span style="background:{kondisi_color}; color:white;
                    padding:2px 8px; border-radius:10px; font-size:12px;">
                    {row['Kondisi']}</span></td></tr>
            <tr><td style="padding:3px 6px; font-weight:600;">Wilayah</td>
                <td style="padding:3px 6px;">{row['Wilayah_Administrasi']}</td></tr>
        </table>
    </div>
    """
    return folium.Popup(html, max_width=280)


# ─────────────────────────────────────────────
# 8. FUNGSI LEGENDA KUSTOM (HTML INLINE)
# ─────────────────────────────────────────────
def render_legenda():
    """
    Membuat legenda peta menggunakan HTML/CSS dengan inline styles
    yang eksplisit (warna teks hitam, background putih) sehingga
    immune terhadap dark mode / tema gelap Streamlit.
    """
    legenda_html = '''<div style="background: #ffffff; border: 2px solid #d1d5db; border-radius: 10px; padding: 18px 22px; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; color: #1f2937; line-height: 2.0; box-shadow: 0 4px 12px rgba(0,0,0,0.10);">
<!-- Judul Legenda -->
<div style="font-size: 16px; font-weight: 700; color: #111827; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 2px solid #e5e7eb;">Legenda Peta</div>
<!-- Bagian TMU -->
<div style="font-weight: 700; color: #374151; margin-bottom: 4px;">Penanda TMU (Kapasitas Sisa)</div>
<div style="display:flex; align-items:center; margin-bottom:3px;">
<span style="display:inline-block; width:16px; height:16px; background:#28a745; border-radius:50%; margin-right:10px; border:1px solid #1e7e34; flex-shrink:0;"></span>
<span style="color:#1f2937;">Hijau — Kapasitas &gt; 30% (Tersedia)</span>
</div>
<div style="display:flex; align-items:center; margin-bottom:3px;">
<span style="display:inline-block; width:16px; height:16px; background:#ffc107; border-radius:50%; margin-right:10px; border:1px solid #d4a106; flex-shrink:0;"></span>
<span style="color:#1f2937;">Kuning — Kapasitas 10–30% (Menipis)</span>
</div>
<div style="display:flex; align-items:center; margin-bottom:8px;">
<span style="display:inline-block; width:16px; height:16px; background:#dc3545; border-radius:50%; margin-right:10px; border:1px solid #b02a37; flex-shrink:0;"></span>
<span style="color:#1f2937;">Merah — Kapasitas &lt; 10% (Kritis)</span>
</div>
<!-- Bagian RPTRA -->
<div style="font-weight: 700; color: #374151; margin-bottom: 4px;">Penanda RPTRA</div>
<div style="display:flex; align-items:center; margin-bottom:3px;">
<span style="display:inline-block; width:16px; height:16px; background:#3b82f6; border-radius:50%; margin-right:10px; border:1px solid #2563eb; flex-shrink:0;"></span>
<span style="color:#1f2937;">Biru — Fasilitas Lengkap</span>
</div>
<div style="display:flex; align-items:center; margin-bottom:8px;">
<span style="display:inline-block; width:16px; height:16px; background:#8b5cf6; border-radius:50%; margin-right:10px; border:1px solid #7c3aed; flex-shrink:0;"></span>
<span style="color:#1f2937;">Ungu — Fasilitas Terbatas</span>
</div>
<!-- Bagian Buffer -->
<div style="font-weight: 700; color: #374151; margin-bottom: 4px;">Zona Buffer Eksklusi</div>
<div style="display:flex; align-items:center;">
<span style="display:inline-block; width:24px; height:16px; background:rgba(232,141,156,0.5); border:1px solid #d63a5e; border-radius:4px; margin-right:10px; flex-shrink:0;"></span>
<span style="color:#1f2937;">Area 500 m sekitar TMU (zona penyangga)</span>
</div>
</div>'''
    st.markdown(legenda_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 9. MUAT DATA
# ─────────────────────────────────────────────
gdf_tmu = buat_data_tmu()
gdf_rptra = buat_data_rptra()
gdf_buffer = buat_buffer_tmu(gdf_tmu)

# ─────────────────────────────────────────────
# 10. SIDEBAR — FILTER DINAMIS & KONTROL LAYER
# ─────────────────────────────────────────────
st.sidebar.markdown("## Panel Kontrol Peta")
st.sidebar.markdown("---")

# 10a. Filter Wilayah Administrasi
semua_wilayah = sorted(
    set(gdf_tmu["Wilayah_Administrasi"].tolist() + gdf_rptra["Wilayah_Administrasi"].tolist())
)
pilihan_wilayah = st.sidebar.multiselect(
    "Filter Wilayah Administrasi",
    options=semua_wilayah,
    default=semua_wilayah,
    help="Pilih satu atau lebih wilayah untuk ditampilkan di peta.",
)

# 10b. Filter Status Kapasitas TMU
semua_status = sorted(gdf_tmu["Status_Kapasitas"].unique().tolist())
pilihan_status = st.sidebar.multiselect(
    "️ Filter Status Kapasitas TMU",
    options=semua_status,
    default=semua_status,
    help="Pilih status kapasitas TMU yang ingin ditampilkan.",
)

st.sidebar.markdown("---")

# 10c. Kontrol Visibilitas Layer (Checkbox)
st.sidebar.markdown("### Kontrol Visibilitas Layer")
tampil_tmu = st.sidebar.checkbox("Tampilkan Layer TMU", value=True)
tampil_rptra = st.sidebar.checkbox("Tampilkan Layer RPTRA", value=True)
tampil_buffer = st.sidebar.checkbox("Tampilkan Buffer 500 m TMU ", value=True)

st.sidebar.markdown("---")
st.sidebar.caption("© 2025 — Ujian Akhir Semester SIG")

# ─────────────────────────────────────────────
# 11. TERAPKAN FILTER
# ─────────────────────────────────────────────
gdf_tmu_filtered = gdf_tmu[
    (gdf_tmu["Wilayah_Administrasi"].isin(pilihan_wilayah))
    & (gdf_tmu["Status_Kapasitas"].isin(pilihan_status))
]

gdf_rptra_filtered = gdf_rptra[
    gdf_rptra["Wilayah_Administrasi"].isin(pilihan_wilayah)
]

# Buffer hanya untuk TMU yang lolos filter
gdf_buffer_filtered = gdf_buffer[gdf_buffer.index.isin(gdf_tmu_filtered.index)]

# ─────────────────────────────────────────────
# 12. HEADER UTAMA
# ─────────────────────────────────────────────
tab1, tab2 = st.tabs(["WebGIS Peta Interaktif Monitoring", "Sistem Pendukung Keputusan Lokasi Optimal Pembangunan RPTRA Baru Berbasis Machine Learning (Random Forest)"])

with tab1:

    st.markdown(
        "<h2 style='color: #FFFFFF; text-align: center;'>Peta Interaktif Monitoring TMU & Aksesibilitas RPTRA di DKI Jakarta</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-title">Sistem Informasi Geografis · Ujian Akhir Semester · Rehan Saputra (41523010065)</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────

    # Titik pusat Jakarta
    PUSAT_JAKARTA = [-6.2088, 106.8456]

    m = folium.Map(
        location=PUSAT_JAKARTA,
        zoom_start=11,
        tiles="OpenStreetMap",
        control_scale=True,  # Skala peta (scale bar)
    )

    # ── 13a. Layer Buffer TMU (di bawah marker agar tidak menutupi) ──
    if tampil_buffer and not gdf_buffer_filtered.empty:
        fg_buffer = folium.FeatureGroup(name="Buffer 500 m TMU", show=True)
        for _, row in gdf_buffer_filtered.iterrows():
            # Konversi geometry ke GeoJSON
            folium.GeoJson(
                data=json.loads(gpd.GeoSeries([row.geometry]).to_json()),
                style_function=lambda x: {
                    "fillColor": "#e88d9c",
                    "color": "#d63a5e",
                    "weight": 1,
                    "fillOpacity": 0.18,
                },
                tooltip=f"Zona Buffer 500 m — {row['Nama_TMU']}",
            ).add_to(fg_buffer)
        fg_buffer.add_to(m)

    # ── 13b. Layer TMU ──
    if tampil_tmu and not gdf_tmu_filtered.empty:
        fg_tmu = folium.FeatureGroup(name="Taman Makam Umum (TMU)", show=True)
        for _, row in gdf_tmu_filtered.iterrows():
            warna = warna_kapasitas(row["Kapasitas_Persen"])
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=popup_tmu(row),
                tooltip=f"{row['Nama_TMU']} ({row['Kapasitas_Persen']}%)",
                icon=folium.Icon(color=warna, icon="plus-sign", prefix="glyphicon"),
            ).add_to(fg_tmu)
        fg_tmu.add_to(m)

    # ── 13c. Layer RPTRA ──
    if tampil_rptra and not gdf_rptra_filtered.empty:
        fg_rptra = folium.FeatureGroup(name="RPTRA", show=True)
        for _, row in gdf_rptra_filtered.iterrows():
            warna = warna_rptra(row["Kondisi"])
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=popup_rptra(row),
                tooltip=f"{row['Nama_RPTRA']}",
                icon=folium.Icon(color=warna, icon="tree-deciduous", prefix="glyphicon"),
            ).add_to(fg_rptra)
        fg_rptra.add_to(m)

    # ── 13d. Layer Control bawaan Folium ──
    folium.LayerControl(collapsed=False).add_to(m)

# ─────────────────────────────────────────────


    # 14. TAMPILKAN PETA
# ─────────────────────────────────────────────


    # Peringatan jika tidak ada data setelah filter
    if gdf_tmu_filtered.empty and gdf_rptra_filtered.empty:
        st.warning(
            "️ Tidak ada data yang cocok dengan filter yang dipilih. "
            "Silakan ubah pengaturan filter pada sidebar."
        )

    st_folium(m, width="100%", height=620, returned_objects=[])

    # ─────────────────────────────────────────────
    # 15. LEGENDA KUSTOM & STATISTIK (DUA KOLOM)
    col_legend, col_stats = st.columns([1, 1])

    with col_legend:
        render_legenda()

    # ─────────────────────────────────────────────
    # 16. STATISTIK RINGKAS
    with col_stats:
        st.markdown("### Statistik Data Saat Ini")

        total_tmu = len(gdf_tmu_filtered)
        tmu_kritis = len(gdf_tmu_filtered[gdf_tmu_filtered["Status_Kapasitas"] == "Kritis"])
        total_rptra = len(gdf_rptra_filtered)
        rptra_lengkap = len(gdf_rptra_filtered[gdf_rptra_filtered["Kondisi"] == "Lengkap"])

        met1, met2 = st.columns(2)
        met1.metric("Total TMU Ditampilkan", total_tmu)
        met2.metric("TMU Kritis (< 10 %)", tmu_kritis)

        met3, met4 = st.columns(2)
        met3.metric("Total RPTRA Ditampilkan", total_rptra)
        met4.metric("RPTRA Kondisi Lengkap", rptra_lengkap)

        if total_tmu > 0:
            rata2_kapasitas = gdf_tmu_filtered["Kapasitas_Persen"].mean()
            st.progress(
                min(int(rata2_kapasitas), 100),
                text=f"Rata-rata Kapasitas TMU yang ditampilkan: **{rata2_kapasitas:.1f}%**",
            )
        else:
            st.info("Tidak ada TMU yang ditampilkan untuk menghitung rata-rata.")

    # ─────────────────────────────────────────────
    # 17. TABEL DATA INTERAKTIF
    st.markdown("---")
    with st.expander("Lihat Tabel Data TMU", expanded=False):
        if not gdf_tmu_filtered.empty:
            st.dataframe(
                gdf_tmu_filtered.drop(columns=["geometry"]).reset_index(drop=True),
                use_container_width=True,
            )
        else:
            st.info("Tidak ada data TMU sesuai filter yang dipilih.")

    with st.expander("Lihat Tabel Data RPTRA", expanded=False):
        if not gdf_rptra_filtered.empty:
            st.dataframe(
                gdf_rptra_filtered.drop(columns=["geometry"]).reset_index(drop=True),
                use_container_width=True,
            )
        else:
            st.info("Tidak ada data RPTRA sesuai filter yang dipilih.")

    # ─────────────────────────────────────────────
    # 18. RINGKASAN EKSEKUTIF
    st.markdown("---")
    st.markdown("### Ringkasan Eksekutif")
    st.markdown(
        """
        <div class="exec-summary">
        <b>Peta Interaktif Monitoring Kapasitas TMU dan Aksesibilitas RPTRA DKI Jakarta</b>
        merupakan sistem informasi geografis berbasis web yang dirancang untuk mendukung
        pengambilan keputusan Pemerintah Provinsi DKI Jakarta dalam mengelola kapasitas
        pemakaman umum serta mengevaluasi sebaran dan aksesibilitas Ruang Publik Terpadu
        Ramah Anak (RPTRA). Dashboard ini menampilkan <b>12 lokasi TMU</b> dan <b>20 lokasi
        RPTRA</b> yang tersebar di 5 wilayah administrasi Jakarta dalam format peta interaktif
        dengan simbolisasi kartografis berbasis kapasitas dan kondisi fasilitas. Zona buffer
        eksklusi 500 meter di sekitar TMU divisualisasikan untuk memastikan pembangunan RPTRA
        baru tidak berdekatan dengan area pemakaman demi kenyamanan psikologis dan dampak
        lingkungan. Melalui integrasi filter dinamis serta analisis spasial lanjutan
        (Random Forest), sistem ini mampu merekomendasikan lokasi prioritas pembangunan
        RPTRA baru secara data-driven.
        <br><br>
        <b>️ Disclaimer & Sumber Data:</b>
        <br>Data spasial (titik koordinat <i>Latitude/Longitude</i>) untuk lokasi TMU dan RPTRA didapatkan 
        secara presisi dari data dunia nyata melalui <b>OpenStreetMap</b> dan <b>Google Maps</b>. 
        Namun, data atribut yang menyertainya (seperti Luas Area, Status Kapasitas, Tahun Berdiri, Fasilitas, dan Kondisi) 
        serta dataset tingkat RW pada modul Machine Learning merupakan <b>Data Simulasi (Mock/Synthetic Data)</b>. 
        Data simulasi ini dibuat secara terprogram menggunakan pustaka <code>pandas</code> dan <code>numpy</code> 
        untuk merepresentasikan kondisi riil (berdasarkan asumsi logika perencanaan kota dari Dinas Pertamanan dan Hutan Kota 
        serta Dinas PPPA DKI Jakarta) guna mendemonstrasikan secara penuh kapabilitas <i>Geoprocessing (Buffer)</i>, 
        <i>Spatial Filtering</i>, dan <i>Machine Learning</i> dari purwarupa aplikasi ini.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<br><center><sub>Dibangun dengan Streamlit · Folium · GeoPandas · Shapely — "
        "Ujian Akhir Semester Sistem Informasi Geografis</sub></center>",
        unsafe_allow_html=True,
    )


with tab2:
    st.markdown("<h2 style='color: #FFFFFF; text-align: center;'>Sistem Pendukung Keputusan Lokasi Optimal Pembangunan RPTRA Baru dengan Mempertimbangkan Zona Eksklusi TMU Berbasis Machine Learning (Random Forest)</h2>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'>Sistem rekomendasi berbasis <b>Machine Learning (Random Forest)</b> untuk menganalisis kelayakan lokasi RW dalam pembangunan RPTRA baru berdasarkan parameter keruangan dan kependudukan.</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 1 Dataset Simulasi Tingkat RW (Spatial Features)")
    
    # Generate Mock Data
    np.random.seed(42)
    n_samples = 20
    
    data_rw = {
        "ID_RW": [f"RW-{str(i).zfill(3)}" for i in range(1, n_samples + 1)],
        "Nama_RW": [f"RW {i:02d} Kel. Simulasi" for i in range(1, n_samples + 1)],
        "Wilayah_Administrasi": np.random.choice(["Jakarta Pusat", "Jakarta Selatan", "Jakarta Barat", "Jakarta Timur", "Jakarta Utara"], n_samples),
        "Jarak_Minimal_ke_TMU": np.random.randint(100, 2500, n_samples), # dalam meter
        "Persentase_Lahan_Kosong": np.random.randint(5, 80, n_samples), # persentase
        "Kepadatan_Penduduk_Anak": np.random.randint(500, 5000, n_samples), # angka/skala
    }
    
    df_rw = pd.DataFrame(data_rw)
    
    # Penentuan Label Prioritas berdasarkan aturan logika simulasi
    # 2 = Sangat Prioritas (Jarak > 500, Lahan > 30%, Kepadatan > 2000)
    # 1 = Cukup Prioritas (Jarak > 500, Lahan > 15%)
    # 0 = Tidak Prioritas (Jarak <= 500 atau Lahan <= 15%)
    def assign_label(row):
        if row["Jarak_Minimal_ke_TMU"] <= 500 or row["Persentase_Lahan_Kosong"] <= 15:
            return 0
        elif row["Persentase_Lahan_Kosong"] > 30 and row["Kepadatan_Penduduk_Anak"] > 2000:
            return 2
        else:
            return 1
            
    df_rw["Label_Prioritas"] = df_rw.apply(assign_label, axis=1)
    
    st.dataframe(df_rw, use_container_width=True)
    st.caption("Keterangan Label Prioritas Data Training: **2 = Sangat Prioritas**, **1 = Cukup Prioritas**, **0 = Tidak Prioritas**")
    
    st.markdown("---")
    st.markdown("### 2 Pelatihan Model Machine Learning (Live Pipeline)")
    
    # Splitting Data
    X = df_rw[["Jarak_Minimal_ke_TMU", "Persentase_Lahan_Kosong", "Kepadatan_Penduduk_Anak"]]
    y = df_rw["Label_Prioritas"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model Training
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # Evaluation
    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.metric("Skor Akurasi Model (Accuracy Score)", f"{accuracy * 100:.2f}%")
        st.success(" Pipeline Executed! Model Random Forest Classifier berhasil dilatih menggunakan dataset dengan proporsi 80% Training Set dan 20% Test Set.")
        
    with col2:
        st.markdown("**Feature Importance (Faktor Paling Berpengaruh):**")
        # Feature Importance
        importances = rf_model.feature_importances_
        df_importances = pd.DataFrame({
            "Fitur": X.columns,
            "Tingkat Kepentingan": importances
        }).set_index("Fitur")
        
        st.bar_chart(df_importances, horizontal=True)
        
    st.markdown("---")
    st.markdown("### 3 Simulasi Prediksi RW Baru")
    
    if st.button("Simulasikan Prediksi RW Baru"):
        # Data baru yang belum berlabel
        new_data = pd.DataFrame({
            "ID_RW": ["RW-901", "RW-902", "RW-903", "RW-904"],
            "Nama_RW": ["RW 01 Pegangsaan", "RW 04 Cilandak", "RW 07 Pluit", "RW 12 Kalideres"],
            "Wilayah_Administrasi": ["Jakarta Pusat", "Jakarta Selatan", "Jakarta Utara", "Jakarta Barat"],
            "Jarak_Minimal_ke_TMU": [1200, 450, 2500, 1500],
            "Persentase_Lahan_Kosong": [45, 60, 10, 35],
            "Kepadatan_Penduduk_Anak": [3500, 4200, 800, 2200]
        })
        
        # Prediksi
        X_new = new_data[["Jarak_Minimal_ke_TMU", "Persentase_Lahan_Kosong", "Kepadatan_Penduduk_Anak"]]
        new_data["Prediksi_Prioritas"] = rf_model.predict(X_new)
        
        # Pewarnaan Tabel
        def color_pred(val):
            if val == 2:
                color = '#28a745'
            elif val == 1:
                color = '#ffc107' # Yellow
            else:
                color = '#dc3545' # Red
            return f'background-color: {color}; color: white; font-weight: bold;'
        
        # Determine Pandas version for applymap vs map styling
        if hasattr(new_data.style, 'map'):
            styled_new_data = new_data.style.map(color_pred, subset=['Prediksi_Prioritas'])
        else:
            styled_new_data = new_data.style.applymap(color_pred, subset=['Prediksi_Prioritas'])
            
        st.dataframe(styled_new_data, use_container_width=True)
        st.info("**Hasil Prediksi Berdasarkan Model:** Hijau = Sangat Prioritas (2), Kuning = Cukup Prioritas (1), Merah = Tidak Prioritas (0)")

    st.markdown("---")
    
    with st.expander("📚 Narasi Edukasi & Jawaban Ujian (Bagian A, B, C)", expanded=False):
        st.markdown("""
        **Bagian A: Spatial Feature Engineering di QGIS**
        Untuk mendapatkan atribut jarak ke TMU terdekat, digunakan tool **Distance to nearest hub (Line to hub)** di QGIS dengan layer RW sebagai *origin* dan layer TMU sebagai *hub*. Untuk atribut lahan kosong, dilakukan proses **Intersection** antara polygon RW dan polygon penggunaan lahan (*land use*), kemudian dihitung persentase luas lahan kosong (Area Lahan Kosong / Area RW * 100) menggunakan **Field Calculator** (`$area`).
        
        **Bagian B: Pseudo-code Python Sistem Rekomendasi ML**
        ```python
        # 1. Load spatial dataframe atribut RW
        df_rw = load_rw_attributes()
        
        # 2. Define Features & Target Matrix
        X = df_rw[["Jarak_ke_TMU", "Lahan_Kosong", "Kepadatan_Anak"]]
        y = df_rw["Label_Prioritas"]
        
        # 3. Train Test Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        # 4. Initialize & Train Random Forest
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X_train, y_train)
        
        # 5. Predict on new unlabelled data
        predictions = model.predict(X_new)
        ```
        
        **Bagian C: Visualisasi Hasil Prediksi ML ke QGIS**
        Setelah mendapatkan output prediksi dalam format CSV/Excel dari skrip Python, data tersebut diimpor kembali ke QGIS. Lakukan operasi **Join Attributes by Field Value** antara layer vektor `Batas_RW_Jakarta.shp` dengan file CSV prediksi berdasarkan kolom kunci `ID_RW`. Setelah terhubung, buka pengaturan *Layer Properties*, pilih **Symbology -> Graduated**, lalu klasifikasikan berdasarkan kolom `Prediksi_Prioritas` menggunakan skema warna intuitif (misal: Merah untuk 0, Kuning untuk 1, Hijau untuk 2) guna menghasilkan **Peta Kesesuaian Lokasi RPTRA Final**.
        """)
