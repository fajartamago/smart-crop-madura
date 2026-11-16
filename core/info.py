"""Konten informatif tanaman Madura (umum & berhati-hati, tanpa statistik yang tak pasti)."""
from __future__ import annotations

PLANT_COLORS = {
    "jagung": "#E0A800", "tembakau": "#8B5E3C", "kacang tanah": "#C98F5E",
    "cabai rawit": "#D63031", "singkong": "#7C8B6F", "padi gogo": "#5FA052",
}
PLANT_EMOJI = {
    "jagung": "🌽", "tembakau": "🍃", "kacang tanah": "🥜",
    "cabai rawit": "🌶️", "singkong": "🌿", "padi gogo": "🌾",
}

PLANTS = {
    "jagung": {
        "deskripsi": "Serealia pangan utama di lahan kering Madura; relatif toleran pada lahan "
                     "marginal dan menjadi sumber pangan serta pakan ternak.",
        "potensi": "Dikenal sebagai makanan pokok masyarakat Madura (nasi jagung) sehingga "
                   "permintaan lokalnya cenderung stabil.",
        "tips": ["Gunakan benih unggul/varietas adaptif lahan kering.",
                 "Tanam di awal musim hujan agar kebutuhan air terpenuhi saat awal tumbuh.",
                 "Pemupukan berimbang (N, P, K) dan pengendalian gulma pada 3-4 minggu pertama.",
                 "Waspadai hama penggerek batang dan ulat grayak."],
        "musim": "Umumnya ditanam awal musim hujan; dapat juga di awal kemarau bila air tersedia.",
    },
    "tembakau": {
        "deskripsi": "Tanaman komoditas perkebunan semusim yang identik dengan Madura, biasanya "
                     "ditanam pada musim kemarau.",
        "potensi": "Tembakau Madura dikenal di Pamekasan, Sumenep, dan Sampang, dan menjadi "
                   "sumber penghasilan musiman bagi banyak petani.",
        "tips": ["Pilih lahan dengan drainase baik; hindari genangan.",
                 "Atur waktu tanam agar panen tidak bertepatan dengan hujan lebat.",
                 "Perhatikan pengairan secukupnya pada fase awal.",
                 "Kendalikan hama ulat dan penyakit layu secara terpadu."],
        "musim": "Umumnya ditanam pada musim kemarau.",
    },
    "kacang tanah": {
        "deskripsi": "Tanaman legum penghasil polong yang menyukai tanah gembur dan drainase baik; "
                     "cocok sebagai tanaman rotasi.",
        "potensi": "Sesuai untuk lahan kering/berkapur dan membantu menyuburkan tanah melalui "
                   "bintil akar pengikat nitrogen.",
        "tips": ["Gemburkan tanah dan pastikan drainase lancar.",
                 "Pertimbangkan pengapuran bila tanah terlalu masam.",
                 "Hindari kekeringan saat pembungaan dan pengisian polong.",
                 "Rotasi dengan jagung atau padi gogo untuk memutus hama dan penyakit."],
        "musim": "Umum ditanam di akhir musim hujan atau awal kemarau.",
    },
    "cabai rawit": {
        "deskripsi": "Hortikultura bernilai ekonomi tinggi dan harganya mudah berfluktuasi; "
                     "membutuhkan perawatan intensif.",
        "potensi": "Dapat diusahakan di pekarangan maupun ladang, terutama pada lahan subur "
                   "dengan pengairan yang memadai.",
        "tips": ["Gunakan bedengan dan mulsa untuk menekan gulma serta menjaga kelembapan.",
                 "Hindari genangan karena akar mudah busuk.",
                 "Pantau hama thrips, kutu daun, dan penyakit antraknosa.",
                 "Panen bertahap dan pantau harga pasar sebelum menentukan luas tanam."],
        "musim": "Dapat ditanam sepanjang tahun bila air tersedia; hati-hati curah hujan sangat tinggi.",
    },
    "singkong": {
        "deskripsi": "Umbi akar yang sangat toleran terhadap lahan kering dan tanah kurang subur.",
        "potensi": "Cocok untuk tanah kapur dan marjinal sebagai cadangan pangan atau bahan olahan.",
        "tips": ["Gunakan stek batang sehat berumur cukup.",
                 "Tanam saat tanah cukup lembap; hindari genangan.",
                 "Lakukan penyiangan awal agar pertumbuhan tidak terhambat.",
                 "Panen saat umbi cukup umur sesuai varietas."],
        "musim": "Fleksibel; umumnya ditanam di awal musim hujan.",
    },
    "padi gogo": {
        "deskripsi": "Padi lahan kering (tanpa penggenangan) yang bergantung pada curah hujan.",
        "potensi": "Alternatif penghasil beras pada lahan tadah hujan di Madura, bila curah hujan "
                   "cukup selama fase pertumbuhan.",
        "tips": ["Gunakan varietas padi gogo yang toleran kekeringan.",
                 "Tanam serempak di awal musim hujan.",
                 "Jaga kelembapan tanah saat fase anakan dan pengisian bulir.",
                 "Waspadai penyakit blas."],
        "musim": "Umumnya ditanam di awal-tengah musim hujan.",
    },
}

SARAN_FITUR = {
    "suhu": ("Suhu lebih rendah dari kebiasaan tanaman ini; pertimbangkan waktu tanam yang lebih hangat.",
             "Suhu lebih tinggi dari kebiasaan; pertimbangkan naungan, mulsa, atau penyesuaian waktu tanam."),
    "kelembapan": ("Udara relatif kering; jaga kelembapan tanah dengan mulsa.",
                   "Udara sangat lembap; waspadai penyakit jamur dan jaga sirkulasi udara."),
    "curah_hujan": ("Curah hujan di bawah kebutuhan umum; siapkan sumber air/irigasi tambahan.",
                    "Curah hujan tinggi; pastikan drainase baik agar tidak tergenang."),
    "ph_tanah": ("Tanah cenderung masam; pertimbangkan pengapuran/bahan organik.",
                 "Tanah cenderung basa; tambahkan bahan organik untuk menyeimbangkan."),
    "ketinggian": ("Lokasi lebih rendah dari kisaran umum; perhatikan drainase.",
                   "Lokasi lebih tinggi dari kisaran umum; perhatikan suhu dan angin."),
}

FAKTA_MADURA = [
    "Madura didominasi lahan kering dan tanah berkapur, sehingga pilihan tanaman yang tahan kekeringan sangat penting.",
    "Tembakau merupakan komoditas khas, terutama di Pamekasan, Sumenep, dan Sampang.",
    "Jagung merupakan tanaman pangan utama masyarakat Madura.",
    "Musim kemarau di Madura relatif panjang, sehingga ketersediaan air menjadi faktor penentu.",
    "Garam rakyat dari Sumenep dan Pamekasan menunjukkan karakter iklim pesisir yang panas dan kering.",
]

KOORDINAT = {
    "Bangkalan": (-7.0451, 112.7345), "Sampang": (-7.1883, 113.2492),
    "Pamekasan": (-7.1568, 113.4825), "Sumenep": (-7.0167, 113.8667),
}

SKENARIO = [
    ("🌾 Kapur Kering Sumenep", dict(kabupaten="Sumenep", musim="Kemarau", jenis_tanah="kapur",
                                     suhu=29.0, kelembapan=66, curah_hujan=75, ph_tanah=6.5, ketinggian=40)),
    ("🚜 Ladang Tembakau Pamekasan", dict(kabupaten="Pamekasan", musim="Kemarau", jenis_tanah="regosol",
                                          suhu=30.0, kelembapan=62, curah_hujan=60, ph_tanah=6.0, ketinggian=35)),
    ("🌧️ Musim Hujan Sampang", dict(kabupaten="Sampang", musim="Hujan", jenis_tanah="aluvial",
                                     suhu=26.5, kelembapan=84, curah_hujan=210, ph_tanah=5.8, ketinggian=15)),
    ("🌶️ Lahan Subur Bangkalan", dict(kabupaten="Bangkalan", musim="Hujan", jenis_tanah="aluvial",
                                       suhu=25.8, kelembapan=79, curah_hujan=155, ph_tanah=6.1, ketinggian=110)),
    ("🌽 Ladang Jagung Sampang", dict(kabupaten="Sampang", musim="Hujan", jenis_tanah="grumusol",
                                      suhu=28.0, kelembapan=71, curah_hujan=115, ph_tanah=6.4, ketinggian=50)),
]
