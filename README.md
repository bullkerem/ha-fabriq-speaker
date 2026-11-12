# 🔊 Fabriq Wi-Fi Speaker (Linkplay A31) - Home Assistant Custom Integration

[![GitHub Release](https://img.shields.io/github/v/release/bullkerem/ha-fabriq-speaker?style=for-the-badge&color=brightgreen)](https://github.com/bullkerem/ha-fabriq-speaker/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-18BCF2.svg?style=for-the-badge&logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/bullkerem/ha-fabriq-speaker?style=for-the-badge&color=yellow)](https://github.com/bullkerem/ha-fabriq-speaker/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/bullkerem/ha-fabriq-speaker?style=for-the-badge&color=orange)](https://github.com/bullkerem/ha-fabriq-speaker/issues)
[![Last Commit](https://img.shields.io/github/last-commit/bullkerem/ha-fabriq-speaker?style=for-the-badge&color=purple)](https://github.com/bullkerem/ha-fabriq-speaker/commits/main)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bullkerem&repository=ha-fabriq-speaker&category=integration)

**Fabriq Chorus** ve **Fabriq Riff** (Linkplay A31 tabanlı) Wi-Fi/Bluetooth akıllı hoparlörler için özel olarak geliştirilmiş, **uyku modunda bağlantı kopmasını önleyen (Sleep-Resilient)** tam kapsamlı Home Assistant eklentisi.

---

## ✨ Özellikler (Neden Standart Linkplay Yerine Bu Eklenti?)

1. **🛡️ Uyku Modu Koruması (Sleep-Resilient):**
   - Pilli Fabriq hoparlörler derin uykuya geçtiğinde standart entegrasyonlar `Unavailable` (Kullanılamıyor) hatasına düşer ve Home Assistant yeniden başlatıldığında kurulumu reddeder.
   - Bu eklenti hoparlör uyurken bile cihazı **`Standby / Uyku Modunda`** olarak canlı tutar, uyandığı anda otomatik olarak bağlanır ve iç saatini (`timeSync`) senkronize eder.
2. **🎚️ Donanımsal Ekolayzer (EQ) Seçici (`select`):**
   - `Normal (Flat)`, `Klasik`, `Pop`, `Bass / Jazz`, `Vokal` modlarını doğrudan çip üzerinden değiştirir (`EQLoad:0..4`).
3. **🔌 Giriş Kaynağı Seçici (`select`):**
   - `Wi-Fi / Ağ`, `Bluetooth`, `AUX (Line-In)` modları arasında tek tıkla geçiş yapar (`setPlayerCmd:switchmode:`).
4. **🔊 Stereo / Sol / Sağ Kanal Seçici (`select`):**
   - İki Fabriq hoparlörü sağ/sol stüdyo çifti veya bağımsız stereo olarak ayarlar (`setPlayerCmd:slave_channel:`).
5. **🗣️ Sesli Uyarı (Voice Prompt) Anahtarı (`switch`):**
   - Hoparlörün açılış/bağlantı sesli bildirimlerini açıp kapatır (`PromptEnable:1` / `0`).
6. **🔗 Tek Tıkla Multiroom & Tekil Mod (`button` & Servisler):**
   - Hoparlörleri birbirine bağlama (`fabriq_speaker.join_multiroom`) veya gruptan ayırıp bağımsız çaldırma (`fabriq_speaker.leave_multiroom`).
7. **📶 Canlı Wi-Fi Sinyal Gücü (RSSI dBm) ve Durum Sensörleri (`sensor`).**

---

## 📦 Kurulum

### Yöntem 1: HACS ile Kurulum (Önerilen)
1. Home Assistant'ta **HACS → Entegrasyonlar** bölümüne gidin.
2. Sağ üstteki üç noktaya (`⋮`) tıklayıp **Özel Depolar (Custom Repositories)** seçeneğini açın.
3. Depo URL'sini yapıştırın ve kategori olarak **Integration (Entegrasyon)** seçip ekleyin.
4. **Fabriq Wi-Fi Speaker** eklentisini indirip Home Assistant'ı yeniden başlatın.

### Yöntem 2: Manuel Kurulum
1. Bu depodaki `custom_components/fabriq_speaker` klasörünü Home Assistant'ınızın `/config/custom_components/fabriq_speaker` dizinine kopyalayın.
2. Home Assistant'ı yeniden başlatın.

---

## ⚙️ Hoparlör Ekleme (Arayüzden 1 Tıkla)

1. **Ayarlar → Cihazlar ve Hizmetler → Entegrasyon Ekle** butonuna tıklayın.
2. Arama kutusuna **Fabriq Wi-Fi Speaker** yazın.
3. Hoparlörünüzün IP adresini (Örn: `192.168.8.124` veya `192.168.8.241`) ve adını girip **Gönder**'e tıklayın.

---

## 🛠️ Özel Servisler (Geliştirici Araçları / Otomasyonlar)

- `fabriq_speaker.send_command`: Herhangi bir Linkplay HTTP API komutunu (`EQLoad:2`, `PromptEnable:0`, `reboot` vb.) tek veya tüm hoparlörlere gönderir.
- `fabriq_speaker.join_multiroom`: İki Fabriq hoparlörü birbirine bağlar.
- `fabriq_speaker.leave_multiroom`: Hoparlörleri gruptan ayırıp bağımsız (tekil) moda alır.

---

## 🆕 Sürüm Geçmişi / Changelog

### v1.0.0
- 🚀 İlk resmi HACS sürümü: Sleep-Resilient Linkplay A31 / Fabriq koordinatörü, donanımsal EQ, kaynak ve stereo kanal seçicileri, sesli uyarı anahtarı ve multiroom servisleri.
- 🏷️ Dinamik GitHub Release, HACS Custom, Home Assistant (`2024.1+`), License MIT, Yıldız, Sorun, Son Commit rozetleri ve tek tıkla **My Home Assistant (HACS)** kurulum butonu eklendi.
- 🛠️ `media_player.py` içindeki `async_volume_up` yazım düzeltmesi yapıldı.

---

## 📄 Lisans
Bu proje [MIT Lisansı](LICENSE) altında açık kaynak olarak paylaşılmıştır.
