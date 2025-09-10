# X-Scraper 🐦

> Tools advanced untuk scraping data dari X (Twitter) dengan fitur login otomatis dan filtering canggih.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Platform](https://img.shields.io/badge/platform-X%20(Twitter)-1DA1F2.svg)

## 📋 Deskripsi

X-Scraper adalah tools khusus yang dikembangkan dengan Python untuk mengekstrak data tweet dari platform X (Twitter) secara otomatis. Tools ini dilengkapi dengan fitur login otomatis, filtering canggih, dan error handling yang robust untuk pengalaman scraping yang optimal.

## ✨ Fitur Utama

- 🔐 **Auto Login** - Login otomatis dengan kredensial yang disimpan
- 🎯 **Advanced Search** - Pencarian dengan berbagai parameter dan filter
- 🔍 **Multi Search Type** - Support latest, top, people, photos, videos
- 🌐 **Language Filter** - Filter berdasarkan bahasa (default: Indonesian)
- 📅 **Date Range Filter** - Scraping tweet dalam rentang tanggal tertentu
- 👍 **Engagement Filter** - Filter berdasarkan likes, replies, dll
- 🚫 **Content Exclusion** - Exclude replies dan retweets sesuai kebutuhan
- 🕶️ **Headless Mode** - Jalankan dengan atau tanpa browser GUI
- 🌐 **Proxy Support** - Support proxy untuk anonymity
- 📊 **Export Options** - Export hasil ke berbagai format

## 🚀 Quick Start

### Instalasi

1. Clone repository ini:
```bash
git clone https://github.com/username/X-Scraper.git
cd X-Scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Jalankan scraper:
```bash
python main.py
```

## 📱 Cara Penggunaan

Setelah menjalankan `python main.py`, Anda akan melihat interface interaktif:

### 1. Login Setup
```
=== ADVANCED X (TWITTER) SCRAPER ===
Enhanced version with automatic login and better error handling
Do you want to login automatically? (y/n, default: y): y

🔐 LOGIN CREDENTIALS
==============================
Username/Email/Phone: @username_anda
Password: [password_anda]
```

### 2. Browser Configuration
```
Run in headless mode? (y/n, default: n): n
Use proxy? (format: ip:port, leave empty for none): 127.0.0.1:8080
```

### 3. Search Parameters
```
📊 SEARCH PARAMETERS
=========================
Enter search keyword: teknologi AI
Number of tweets to collect (default: 50): 100
Search type (latest/top/people/photos/videos, default: latest): latest
Language filter (default: id for Indonesian): id
```

### 4. Advanced Filters
```
🔍 ADVANCED FILTERS (optional)
===================================
Date since (YYYY-MM-DD, optional): 2024-01-01
Date until (YYYY-MM-DD, optional): 2024-01-31
Minimum likes (optional): 10
Minimum replies (optional): 5
Exclude replies? (y/n, default: n): n
Exclude retweets? (y/n, default: n): y
```

## 🛠️ Konfigurasi Detail

### Search Types
- **latest** - Tweet terbaru berdasarkan waktu
- **top** - Tweet dengan engagement tertinggi
- **people** - Tweet dari akun spesifik
- **photos** - Tweet yang mengandung foto
- **videos** - Tweet yang mengandung video

### Language Codes
- **id** - Bahasa Indonesia
- **en** - English

### Date Format
Gunakan format `YYYY-MM-DD` untuk filter tanggal:
- Date since: `2024-01-01`
- Date until: `2024-12-31`

### Proxy Format
Gunakan format `ip:port` untuk proxy:
- HTTP Proxy: `127.0.0.1:8080`
- SOCKS Proxy: `127.0.0.1:1080`

## 📊 Output Data

Tools ini akan menghasilkan data tweet dalam format JSON dengan struktur:

```json
{
  "search_metadata": {
    "keyword": "teknologi AI",
    "search_type": "latest",
    "language": "id",
    "total_collected": 100,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "tweets": [
    {
      "id": "1234567890",
      "text": "Konten tweet...",
      "author": {
        "username": "username",
        "display_name": "Display Name",
        "followers": 1000
      },
      "metrics": {
        "likes": 25,
        "retweets": 10,
        "replies": 5
      },
      "timestamp": "2024-01-15T10:00:00Z",
      "url": "https://twitter.com/username/status/1234567890"
    }
  ]
}
```

## 📦 Requirements

File `requirements.txt` berisi:

```txt
selenium>=4.0.0
webdriver-manager>=3.8.0
beautifulsoup4>=4.11.0
requests>=2.28.0
pandas>=1.5.0
python-dotenv>=0.19.0
fake-useragent>=1.1.0
undetected-chromedriver>=3.4.0
```

## 🚨 Tips & Best Practices

### Rate Limiting
- Gunakan delay yang wajar (2-5 detik) antar request
- Jangan scraping dalam jumlah besar secara bersamaan
- Monitor untuk signs of rate limiting

### Account Safety
- Gunakan akun test, bukan akun utama
- Rotate proxy jika scraping dalam volume tinggi
- Hindari pattern yang terlalu predictable

### Error Handling
- Tools sudah dilengkapi retry mechanism
- Jika terjadi error, cek koneksi internet dan kredensial
- Restart tools jika browser crash

## 🔧 Troubleshooting

### Common Issues

**1. Login Failed**
```
Solution: Pastikan username/password benar
Cek apakah akun tidak di-suspend atau butuh verification
```

**2. ChromeDriver Error**
```bash
# Update webdriver
pip install --upgrade webdriver-manager
```

**3. Proxy Connection Failed**
```
Solution: Cek format proxy (ip:port)
Test proxy connection secara manual
```

**4. No Tweets Found**
```
Solution: Coba keyword yang lebih umum
Periksa filter tanggal dan parameter lainnya
```

## ⚖️ Legal & Disclaimer

⚠️ **PENTING**: Tools ini dibuat untuk tujuan research dan edukasi. 

**Ketentuan Penggunaan:**
- Patuhi Terms of Service X (Twitter)
- Jangan scraping data personal tanpa consent
- Gunakan untuk research, bukan untuk spam atau harassment
- Respect rate limits dan server capacity
- Data yang di-scrape adalah data publik

**Disclaimer:**
- Developer tidak bertanggung jawab atas penyalahgunaan tools
- Pengguna bertanggung jawab penuh atas penggunaan tools ini
- Scraping berlebihan dapat menyebabkan account suspension

## 🎯 Use Cases

### Research & Analytics
- Analisis sentiment media sosial
- Monitoring brand mention
- Trend analysis
- Academic research

### Business Intelligence
- Competitor monitoring
- Market research
- Customer feedback analysis
- Crisis management monitoring

### Content Strategy
- Hashtag research
- Influencer identification
- Content performance analysis
- Engagement pattern study

## 🤝 Contributing

Kontribusi sangat diterima! 

**Development Setup:**
```bash
git clone https://github.com/Zulkifli1409/X-Scraper.git
cd X-Scraper
pip install -r requirements.txt
# Make your changes
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
```

## 📝 Changelog

### v1.0.0
- ✅ Auto login functionality
- ✅ Advanced search filters
- ✅ Multi search type support
- ✅ Date range filtering
- ✅ Engagement filters
- ✅ Proxy support
- ✅ Headless mode

### Planned Features
- [ ] Scheduled scraping
- [ ] Database integration
- [ ] Real-time streaming
- [ ] Dashboard UI
- [ ] Batch account management

## 📞 Support & Contact

- 🐛 **Issues**: [GitHub Issues](https://github.com/Zulkifli1409/X-Scraper/issues)
- 📧 **Email**: zul140904@gmail.com
- 🔗 **LinkedIn**: [Zulkifli1409](https://www.linkedin.com/in/zulkifli1409).

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

⭐ **Jika tools ini berguna untuk research Anda, berikan star!** ⭐

*Dibuat dengan ❤️ untuk komunitas researcher Indonesia*

---

**⚠️ Gunakan dengan bijak dan bertanggung jawab! ⚠️**
