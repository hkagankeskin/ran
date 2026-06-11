import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="RAN Analytics", layout="wide")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🔐 RAN Karar Destek Aracı</h2>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        entered_password = st.text_input("Lütfen erişim şifresini giriniz", type="password")
        if st.button("Giriş Yap"):
            if entered_password == st.secrets["password"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Hatalı şifre.")
    return False

# Norm blokları ve model sınırları
# Blok 1: 73-79 ay (1. sınıf)
# Blok 2: 89-96 ay (2. sınıf)
# 80-88 ay: yetersiz veri

BLOK1_YAS = (73, 79)
BLOK2_YAS = (89, 96)
YETERSIZ_YAS = (80, 88)

def yas_blogu(yas):
    if BLOK1_YAS[0] <= yas <= BLOK1_YAS[1]:
        return 1
    elif BLOK2_YAS[0] <= yas <= BLOK2_YAS[1]:
        return 2
    elif YETERSIZ_YAS[0] <= yas <= YETERSIZ_YAS[1]:
        return 0  # yetersiz veri
    elif yas < BLOK1_YAS[0]:
        return -1  # çok küçük
    else:
        return -2  # çok büyük

def bant_goster(t_puani):
    if t_puani <= 30:
        bant = "Çok Zayıf"; renk = "#ef4444"; dolu = 1
    elif t_puani <= 40:
        bant = "Zayıf"; renk = "#f97316"; dolu = 2
    elif t_puani <= 60:
        bant = "Normal"; renk = "#3b82f6"; dolu = 3
    elif t_puani <= 70:
        bant = "İyi"; renk = "#22c55e"; dolu = 4
    else:
        bant = "Çok İyi"; renk = "#16a34a"; dolu = 5

    kareler = ""
    for i in range(1, 6):
        if i <= dolu:
            kareler += f"<span style='background:{renk}; color:white; padding:2px 8px; margin:1px; border-radius:3px; font-size:0.8rem;'>■</span>"
        else:
            kareler += f"<span style='background:#e2e8f0; color:#e2e8f0; padding:2px 8px; margin:1px; border-radius:3px; font-size:0.8rem;'>■</span>"
    return f"{kareler} <span style='font-weight:600; color:{renk};'>{bant}</span>"

def sonuc_hesapla(df, yas_ay, ham_sure):
    df_yas = df[df['Aylik_Yas'] == yas_ay].copy()
    if df_yas.empty:
        return None
    df_yas['raw_numeric'] = pd.to_numeric(df_yas['raw'], errors='coerce')
    idx = (df_yas['raw_numeric'] - ham_sure).abs().idxmin()
    satir = df_yas.loc[idx]
    return {"t": satir['norm'], "p": satir['percentile']}

def klinik_yorum_uret(sonuclar, yas_ay, aktif_testler):
    sinif = "1. sınıf" if yas_ay <= 82 else "2. sınıf"
    zayif = []; normal = []; iyi = []
    for test in aktif_testler:
        s = sonuclar.get(test)
        if s is None: continue
        if s["t"] <= 40: zayif.append(test)
        elif s["t"] <= 60: normal.append(test)
        else: iyi.append(test)

    satirlar = [f"Öğrenci, {yas_ay} aylık ({sinif}) norm grubu baz alınarak değerlendirilmiştir."]
    if iyi:
        satirlar.append(f"**Güçlü alanlar:** {', '.join(iyi)} testlerinde akranlarının üzerinde bir otomatizasyon hızı sergilemiştir.")
    if normal:
        satirlar.append(f"**Beklenen düzey:** {', '.join(normal)} testlerinde yaşıtlarıyla uyumlu bir performans göstermiştir.")
    if zayif:
        satirlar.append(f"**Dikkat gerektiren alanlar:** {', '.join(zayif)} testlerinde akranlarına kıyasla yavaş bir otomatizasyon hızı gözlemlenmiştir. Bu durum okuma güçlüğü riskine işaret edebilir; uzman değerlendirmesi önerilir.")
    if not zayif:
        satirlar.append("Genel değerlendirmede öğrencinin RAN performansı yaş düzeyiyle uyumludur. Herhangi bir müdahale planlamasına gerek görülmemektedir.")
    return "\n\n".join(satirlar)

if check_password():
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa; }
        .header-container { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
        .header-logo { height: 60px; border-radius: 8px; }
        h1 { color: #1e3a8a !important; font-family: 'Inter', sans-serif; font-weight: 700; margin: 0; }
        [data-testid="stMetricValue"] { color: #2563eb !important; font-size: 1.8rem !important; }
        hr { border-top: 1px solid #cbd5e1 !important; }
        </style>
        """, unsafe_allow_html=True)

    logo_url = "https://support.renaissance.com/servlet/rtaImage?eid=ka0Nx00000073KX&feoid=00NQg000006K5pm&refid=0EMQg00000IutXM"
    st.markdown(f"""
        <div class="header-container">
            <img src="{logo_url}" class="header-logo" alt="RAN Logo">
            <h1>RAN Analytics System</h1>
        </div>
        """, unsafe_allow_html=True)
    st.write("Hızlı Otomatik İsimlendirme (RAN) Klinik Karar Destek Aracı")

    @st.cache_data
    def load_data():
        try:
            return {
                "Sekil_1": pd.read_csv("RAN_Sekil_Sinif1_Norm.csv"),
                "Renk_1":  pd.read_csv("RAN_Renk_Sinif1_Norm.csv"),
                "Sayi_1":  pd.read_csv("RAN_Sayi_Sinif1_Norm.csv"),
                "Sekil_2": pd.read_csv("RAN_Sekil_Sinif2_Norm.csv"),
                "Renk_2":  pd.read_csv("RAN_Renk_Sinif2_Norm.csv"),
                "Sayi_2":  pd.read_csv("RAN_Sayi_Sinif2_Norm.csv"),
                "Harf_2":  pd.read_csv("RAN_Harf_Sinif2_Norm.csv"),
            }
        except Exception as e:
            st.error(f"Sistem Hatası: Norm veritabanı yüklenemedi! {e}")
            return None

    norms = load_data()

    if norms:
        st.sidebar.subheader("⚙️ Parametreler")
        yas_ay = st.sidebar.slider("Öğrenci Yaşı (Ay)", 70, 96, 78)

        blok = yas_blogu(yas_ay)

        # Yaş grubu bilgisi
        if blok == 1:
            st.sidebar.success(f"✓ 1. Sınıf norm grubu ({BLOK1_YAS[0]}-{BLOK1_YAS[1]} ay)")
        elif blok == 2:
            st.sidebar.success(f"✓ 2. Sınıf norm grubu ({BLOK2_YAS[0]}-{BLOK2_YAS[1]} ay)")
        elif blok == 0:
            st.sidebar.warning(f"⚠️ {yas_ay} ay için norm verisi yetersiz ({YETERSIZ_YAS[0]}-{YETERSIZ_YAS[1]} ay arası güvenilir veri bulunmamaktadır).")
        elif blok == -1:
            st.sidebar.warning(f"⚠️ {yas_ay} ay norm alt sınırının altında (min: {BLOK1_YAS[0]} ay).")
        else:
            st.sidebar.warning(f"⚠️ {yas_ay} ay norm üst sınırının üzerinde (max: {BLOK2_YAS[1]} ay).")

        if blok in (1, 2):
            st.sidebar.divider()
            st.sidebar.subheader("⏱️ Test Süreleri (Saniye)")
            st.sidebar.caption("Uygulanmayan test için 0 girin.")

            suffix = str(blok)
            sure_sekil = st.sidebar.number_input("Şekil", min_value=0.0, max_value=300.0, value=0.0, step=0.5)
            sure_renk  = st.sidebar.number_input("Renk",  min_value=0.0, max_value=300.0, value=0.0, step=0.5)
            sure_sayi  = st.sidebar.number_input("Sayı",  min_value=0.0, max_value=300.0, value=0.0, step=0.5)

            if blok == 2:
                sure_harf = st.sidebar.number_input("Harf", min_value=0.0, max_value=300.0, value=0.0, step=0.5)
            else:
                sure_harf = 0.0
                st.sidebar.caption("ℹ️ Harf testi 2. sınıf norm grubunda uygulanır.")

            sureler = {
                "Şekil": (sure_sekil, f"Sekil_{suffix}"),
                "Renk":  (sure_renk,  f"Renk_{suffix}"),
                "Sayı":  (sure_sayi,  f"Sayi_{suffix}"),
            }
            if blok == 2:
                sureler["Harf"] = (sure_harf, f"Harf_{suffix}")

            aktif = {t: (s, k) for t, (s, k) in sureler.items() if s > 0}

            if not aktif:
                st.info("👈 Sol panelden öğrenci yaşını ve test sürelerini girin.")
            else:
                sonuclar = {}
                uyarilar = []

                for test, (sure, norm_key) in aktif.items():
                    df_norm = norms[norm_key]
                    raw_min = df_norm.raw.min()
                    raw_max = df_norm.raw.max()

                    if sure < raw_min:
                        uyarilar.append(f"**{test}:** {sure} sn model alt sınırının ({raw_min:.0f} sn) altında.")
                    elif sure > raw_max:
                        uyarilar.append(f"**{test}:** {sure} sn model üst sınırının ({raw_max:.0f} sn) üzerinde.")

                    s = sonuc_hesapla(df_norm, yas_ay, sure)
                    if s:
                        sonuclar[test] = s

                for u in uyarilar:
                    st.warning(u)

                if sonuclar:
                    st.divider()
                    st.subheader("📊 Test Karşılaştırması")

                    cols = st.columns(len(sonuclar))
                    for col, test in zip(cols, sonuclar):
                        col.markdown(f"### {test}")

                    cols = st.columns(len(sonuclar))
                    for col, test in zip(cols, sonuclar):
                        col.metric("T-Skoru", f"{sonuclar[test]['t']:.1f}")

                    cols = st.columns(len(sonuclar))
                    for col, test in zip(cols, sonuclar):
                        col.metric("Persentil", f"%{sonuclar[test]['p']:.1f}")

                    cols = st.columns(len(sonuclar))
                    for col, test in zip(cols, sonuclar):
                        with col:
                            st.markdown(bant_goster(sonuclar[test]['t']), unsafe_allow_html=True)

                    st.divider()
                    st.subheader("📝 Öğretmen İçin Klinik Değerlendirme")
                    yorum = klinik_yorum_uret(sonuclar, yas_ay, list(sonuclar.keys()))
                    st.info(yorum)
        else:
            if blok == 0:
                st.warning(
                    f"**{yas_ay} ay için norm verisi yetersizdir.**\n\n"
                    f"Mevcut normlar **{BLOK1_YAS[0]}-{BLOK1_YAS[1]} ay** (1. sınıf) ve "
                    f"**{BLOK2_YAS[0]}-{BLOK2_YAS[1]} ay** (2. sınıf) grupları için geçerlidir. "
                    f"{YETERSIZ_YAS[0]}-{YETERSIZ_YAS[1]} ay aralığında örneklem yetersizliği nedeniyle "
                    f"güvenilir norm üretilememektedir."
                )

        st.write("")
        st.divider()
        _, l_col1, l_col2, l_col3, _ = st.columns([1, 2, 2, 2, 1])
        with l_col1:
            if os.path.exists("hacettepe.svg"): st.image("hacettepe.svg", width=85)
        with l_col2:
            if os.path.exists("duzce.svg"): st.image("duzce.svg", width=140)
        with l_col3:
            if os.path.exists("Rlogo.svg"): st.image("Rlogo.svg", width=120)

        st.write("")
        st.markdown(
            "<div style='text-align: center; color: #374151; font-size: 0.90rem; margin-bottom: 6px;'>"
            "<strong>Proje Ekibi</strong><br>"
            "Prof. Dr. H. Kağan Keskin — Düzce Üniversitesi &nbsp;|&nbsp; "
            "Prof. Dr. Özay Karadağ — Hacettepe Üniversitesi"
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div style='text-align: center; color: gray; font-size: 0.85rem;'>"
            "Bu normlama sistemi, sürekli normlama yaklaşımı benimsenerek Python ortamında "
            "polinom regresyon modellemesi (derece=3) ile geliştirilmiştir. "
            "Ham skorlar yaş grubuna göre Hazen formülüyle persentile dönüştürülmüş "
            "ve T-skorları hesaplanmıştır (Keskin &amp; Karadağ, 2025).</div>",
            unsafe_allow_html=True
        )
