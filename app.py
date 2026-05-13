import streamlit as st
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="RAN Testi Puanlama", layout="wide")

st.title("🎯 RAN Testi Otomatik Puanlama")
st.write("Hızlı Otomatik İsimlendirme (RAN) Norm Karşılaştırma Laboratuvarı")

# 1. VERİ YÜKLEME (Cache kullanarak hızı artırıyoruz)
@st.cache_data
def load_data():
    try:
        sekil = pd.read_csv("RAN_Sekil_Tum_Aylar_Norm_Tablosu.csv")
        renk = pd.read_csv("RAN_Renk_Tum_Aylar_Norm_Tablosu.csv")
        sayi = pd.read_csv("RAN_Sayi_Tum_Aylar_Norm_Tablosu.csv")
        return {"Şekil": sekil, "Renk": renk, "Sayı": sayi}
    except FileNotFoundError:
        st.error("Hata: Norm dosyaları GitHub'da bulunamadı!")
        return None

norms = load_data()

if norms:
    # 2. YAN PANEL (Girişler)
    st.sidebar.header("Öğrenci Bilgileri")
    test_tipi = st.sidebar.selectbox("Test Türü", ["Şekil", "Renk", "Sayı"])
    yas_ay = st.sidebar.slider("Öğrenci Yaşı (Ay)", 70, 82, 75)
    ham_sure = st.sidebar.number_input("Test Süresi (Saniye)", 20, 150, 60)

    # 3. HESAPLAMA MANTIĞI
    df_secili = norms[test_tipi]
    sonuc = df_secili[(df_secili['Aylik_Yas'] == yas_ay) & (df_secili['raw'] == ham_sure)]

    if not sonuc.empty:
        t_puani = sonuc.iloc[0]['norm']
        yuzdelik = sonuc.iloc[0]['percentile']

        # Kategori Belirleme
        if t_puani <= 30:
            durum, renk_kod = "🔴 AĞIR RİSK: Çok Yavaş", "red"
        elif t_puani <= 40:
            durum, renk_kod = "🟡 RİSKLİ: Yavaş", "orange"
        elif t_puani >= 60:
            durum, renk_kod = "🟢 ÜSTÜN: Çok Hızlı", "green"
        else:
            durum, renk_kod = "🔵 NORMAL: Beklenen", "blue"

        # 4. GÖRSEL SONUÇ EKRANI
        st.divider()
        st.markdown(f"### Değerlendirme: :{renk_kod}[{durum}]")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("T-Puanı", f"{t_puani:.2f}")
        col2.metric("Yüzdelik Dilim", f"%{yuzdelik:.1f}")
        col3.metric("Ham Süre", f"{ham_sure} sn")

        st.info(f"Yorum: {yas_ay} aylık bir çocuk için {secilen_test} testinde {ham_sure} saniyelik performans, yaşıtlarının %{yuzdelik:.1f}'inden daha iyidir.")
    else:
        st.warning("Bu değerler için norm tablosunda karşılık bulunamadı. Lütfen girişleri kontrol edin.")
