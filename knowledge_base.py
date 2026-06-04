"""
Knowledge Base Akademik — Data terstruktur sebagai pengganti PDF
Berisi FAQ, ringkasan peraturan, dan prosedur akademik
"""

DOCUMENTS = [
    # ── SKS & Beban Studi ────────────────────────────────────────────────────
    {
        "id": "sks_01",
        "kategori": "Beban Studi / SKS",
        "judul": "Maksimal SKS per Semester",
        "isi": (
            "Mahasiswa dapat mengambil maksimal 24 SKS per semester jika IPK semester "
            "sebelumnya ≥ 3.00. Jika IPK antara 2.50–2.99 maksimal 21 SKS. "
            "Jika IPK antara 2.00–2.49 maksimal 18 SKS. "
            "Jika IPK di bawah 2.00 maksimal 12 SKS. "
            "Mahasiswa baru (semester 1) dapat mengambil maksimal 20 SKS."
        ),
    },
    {
        "id": "sks_02",
        "kategori": "Beban Studi / SKS",
        "judul": "Total SKS untuk Kelulusan",
        "isi": (
            "Untuk lulus program Sarjana (S1), mahasiswa harus menyelesaikan minimal 144 SKS. "
            "Program Diploma 3 (D3) minimal 110 SKS. "
            "Program Magister (S2) minimal 36 SKS. "
            "Program Doktor (S3) minimal 42 SKS. "
            "Semua mata kuliah wajib dan pilihan harus memenuhi distribusi yang ditetapkan kurikulum."
        ),
    },
    {
        "id": "sks_03",
        "kategori": "Beban Studi / SKS",
        "judul": "Pengisian FRS (Form Rencana Studi)",
        "isi": (
            "FRS diisi setiap awal semester melalui Sistem Informasi Akademik (SIAKAD). "
            "Pengisian FRS dilakukan pada periode yang ditetapkan kalender akademik. "
            "Mahasiswa yang tidak mengisi FRS dianggap tidak aktif pada semester tersebut. "
            "Perubahan FRS (tambah/batal mata kuliah) hanya diperbolehkan pada masa revisi FRS "
            "yang biasanya berlangsung 2 minggu setelah kuliah dimulai. "
            "FRS harus disetujui oleh Dosen Pembimbing Akademik (DPA)."
        ),
    },

    # ── Penilaian & IPK ─────────────────────────────────────────────────────
    {
        "id": "nilai_01",
        "kategori": "Penilaian dan IPK",
        "judul": "Sistem Penilaian dan Konversi Nilai",
        "isi": (
            "Nilai akhir mata kuliah dinyatakan dalam huruf: "
            "A (85–100) = 4.00, A- (80–84) = 3.75, B+ (75–79) = 3.50, "
            "B (70–74) = 3.00, B- (65–69) = 2.75, C+ (60–64) = 2.50, "
            "C (55–59) = 2.00, D (40–54) = 1.00, E (0–39) = 0.00. "
            "Nilai minimal lulus untuk mata kuliah wajib adalah C. "
            "Mata kuliah dengan nilai D atau E harus diulang."
        ),
    },
    {
        "id": "nilai_02",
        "kategori": "Penilaian dan IPK",
        "judul": "Komponen Penilaian Mata Kuliah",
        "isi": (
            "Komponen penilaian terdiri dari: Kehadiran (10–15%), "
            "Tugas/Praktikum (20–30%), Ujian Tengah Semester/UTS (25–30%), "
            "Ujian Akhir Semester/UAS (30–40%). "
            "Proporsi exact ditentukan oleh dosen dan tercantum di RPS (Rencana Pembelajaran Semester). "
            "Mahasiswa wajib hadir minimal 75% dari total pertemuan untuk dapat mengikuti UAS."
        ),
    },
    {
        "id": "nilai_03",
        "kategori": "Penilaian dan IPK",
        "judul": "Konsekuensi IPK Rendah dan Evaluasi Akademik",
        "isi": (
            "Mahasiswa dengan IPK di bawah 2.00 setelah semester 2 akan mendapat peringatan akademik. "
            "Jika IPK tetap di bawah 2.00 setelah semester 4, mahasiswa dapat dikenai sanksi akademik "
            "berupa pembatasan pengambilan SKS. "
            "Mahasiswa yang IPK-nya di bawah 2.00 selama 3 semester berturut-turut dapat dikeluarkan (DO). "
            "Evaluasi akademik dilakukan setiap akhir semester oleh program studi."
        ),
    },
    {
        "id": "nilai_04",
        "kategori": "Penilaian dan IPK",
        "judul": "Ujian Susulan dan Perbaikan Nilai",
        "isi": (
            "Ujian susulan hanya diberikan jika mahasiswa tidak hadir karena: sakit (dengan surat dokter), "
            "keluarga inti meninggal dunia, atau tugas resmi kampus. "
            "Permohonan ujian susulan diajukan maksimal 3 hari setelah ujian berlangsung. "
            "Perbaikan nilai (ngulang mata kuliah) diperbolehkan untuk mata kuliah dengan nilai C ke bawah. "
            "Nilai yang dipakai adalah nilai terbaik dari semua pengambilan."
        ),
    },

    # ── Cuti Akademik ───────────────────────────────────────────────────────
    {
        "id": "cuti_01",
        "kategori": "Cuti Akademik",
        "judul": "Syarat dan Ketentuan Cuti Akademik",
        "isi": (
            "Mahasiswa dapat mengajukan cuti akademik maksimal 2 semester selama masa studi, "
            "baik berturut-turut maupun tidak. "
            "Syarat cuti: sudah menempuh minimal 2 semester, tidak sedang dalam sanksi akademik, "
            "membayar biaya administrasi cuti. "
            "Cuti tidak dihitung sebagai masa studi aktif. "
            "Mahasiswa yang cuti tidak boleh mengikuti kegiatan akademik apapun."
        ),
    },
    {
        "id": "cuti_02",
        "kategori": "Cuti Akademik",
        "judul": "Prosedur Pengajuan Cuti Akademik",
        "isi": (
            "Prosedur cuti akademik: (1) Mahasiswa mengisi formulir permohonan cuti di Biro Akademik. "
            "(2) Mendapat persetujuan DPA (Dosen Pembimbing Akademik). "
            "(3) Mendapat persetujuan Ketua Program Studi. "
            "(4) Membayar biaya administrasi di Biro Keuangan. "
            "(5) Menyerahkan berkas ke Biro Akademik. "
            "Pengajuan dilakukan sebelum atau selama masa FRS berlangsung."
        ),
    },

    # ── Tugas Akhir & Skripsi ───────────────────────────────────────────────
    {
        "id": "ta_01",
        "kategori": "Tugas Akhir / Skripsi",
        "judul": "Syarat Mengambil Tugas Akhir",
        "isi": (
            "Syarat pengambilan Tugas Akhir/Skripsi: "
            "(1) Telah menempuh minimal 120 SKS (untuk S1). "
            "(2) IPK minimal 2.00. "
            "(3) Telah lulus semua mata kuliah prasyarat yang ditetapkan program studi. "
            "(4) Tidak memiliki nilai E pada mata kuliah wajib. "
            "(5) Mendapat persetujuan DPA dan Ketua Program Studi."
        ),
    },
    {
        "id": "ta_02",
        "kategori": "Tugas Akhir / Skripsi",
        "judul": "Prosedur Seminar Proposal",
        "isi": (
            "Prosedur seminar proposal skripsi: "
            "(1) Mahasiswa mengajukan topik ke calon pembimbing. "
            "(2) Menyusun proposal dengan bimbingan dosen pembimbing. "
            "(3) Mendaftar seminar proposal ke program studi. "
            "(4) Seminar proposal dilaksanakan di hadapan dosen pembimbing dan penguji. "
            "(5) Mahasiswa harus melakukan revisi sesuai catatan penguji dalam 2 minggu. "
            "Seminar proposal dapat diulang jika dinyatakan tidak lulus oleh tim penguji."
        ),
    },
    {
        "id": "ta_03",
        "kategori": "Tugas Akhir / Skripsi",
        "judul": "Batas Waktu dan Masa Berlaku Tugas Akhir",
        "isi": (
            "Tugas akhir harus diselesaikan dalam 2 semester sejak terdaftar. "
            "Jika melebihi batas waktu, mahasiswa harus mendaftar ulang dan membayar biaya bimbingan baru. "
            "Topik penelitian yang sudah diseminarkan berlaku selama 1 tahun. "
            "Jika lebih dari 1 tahun tanpa kemajuan signifikan, topik dapat diganti dengan persetujuan pembimbing."
        ),
    },
    {
        "id": "ta_04",
        "kategori": "Tugas Akhir / Skripsi",
        "judul": "Sidang Skripsi / Ujian Akhir",
        "isi": (
            "Syarat sidang skripsi: naskah skripsi telah disetujui pembimbing, "
            "bebas plagiasi (maks 25% similarity index), telah mengikuti seminar proposal, "
            "IPK minimal 2.00, bebas tanggungan administrasi. "
            "Sidang dilakukan di hadapan 3 penguji termasuk pembimbing. "
            "Hasil sidang: Lulus, Lulus dengan Revisi, atau Tidak Lulus. "
            "Revisi harus diselesaikan dalam 1 bulan setelah sidang."
        ),
    },

    # ── Kehadiran & Tata Tertib ─────────────────────────────────────────────
    {
        "id": "hadir_01",
        "kategori": "Kehadiran dan Tata Tertib",
        "judul": "Ketentuan Kehadiran Perkuliahan",
        "isi": (
            "Mahasiswa wajib hadir minimal 75% dari total pertemuan per mata kuliah. "
            "Pertemuan biasanya 16 kali termasuk UTS dan UAS, jadi perkuliahan tatap muka 14 kali. "
            "Mahasiswa yang kehadiran kurang dari 75% tidak diperkenankan mengikuti UAS. "
            "Ketidakhadiran karena sakit/izin resmi tetap dihitung absen, "
            "kecuali ada kebijakan khusus dari dosen. "
            "Mahasiswa yang tidak mengikuti UAS otomatis mendapat nilai 0 untuk komponen UAS."
        ),
    },
    {
        "id": "hadir_02",
        "kategori": "Kehadiran dan Tata Tertib",
        "judul": "Tata Tertib di Lingkungan Kampus",
        "isi": (
            "Mahasiswa wajib menjaga kebersihan dan ketertiban kampus. "
            "Dilarang merokok di area kampus kecuali di zona yang telah ditentukan. "
            "Berpakaian sopan dan rapi sesuai peraturan yang berlaku. "
            "Dilarang membawa atau mengonsumsi minuman beralkohol di kampus. "
            "Dilarang melakukan tindakan kekerasan, perundungan (bullying), atau diskriminasi. "
            "Pelanggaran tata tertib diproses melalui Komisi Disiplin Mahasiswa."
        ),
    },

    # ── Pembimbing Akademik ─────────────────────────────────────────────────
    {
        "id": "dpa_01",
        "kategori": "Dosen Pembimbing Akademik (DPA)",
        "judul": "Peran dan Fungsi DPA",
        "isi": (
            "Dosen Pembimbing Akademik (DPA) bertugas: "
            "(1) Memberikan bimbingan dalam perencanaan studi mahasiswa. "
            "(2) Menyetujui FRS setiap semester. "
            "(3) Memantau perkembangan akademik mahasiswa. "
            "(4) Memberikan rekomendasi untuk keperluan akademik (cuti, pindah prodi, dll). "
            "Mahasiswa wajib berkonsultasi dengan DPA minimal 2 kali per semester. "
            "DPA ditetapkan oleh Ketua Program Studi dan berlaku sepanjang studi mahasiswa."
        ),
    },

    # ── Transfer & Pindah ───────────────────────────────────────────────────
    {
        "id": "pindah_01",
        "kategori": "Transfer dan Pindah Program Studi",
        "judul": "Syarat Pindah Program Studi Internal",
        "isi": (
            "Mahasiswa dapat mengajukan pindah program studi internal dengan syarat: "
            "(1) Telah menempuh minimal 1 semester dan maksimal 3 semester. "
            "(2) IPK minimal 2.75. "
            "(3) Mendapat persetujuan dari program studi asal dan tujuan. "
            "(4) Tersedia kuota di program studi tujuan. "
            "(5) Memenuhi persyaratan administrasi keuangan. "
            "SKS yang dapat ditransfer ditentukan oleh program studi tujuan."
        ),
    },
    {
        "id": "pindah_02",
        "kategori": "Transfer dan Pindah Program Studi",
        "judul": "Mahasiswa Transfer dari Perguruan Tinggi Lain",
        "isi": (
            "Mahasiswa transfer dari PT lain dapat diterima dengan syarat: "
            "akreditasi PT asal minimal B, IPK minimal 3.00, "
            "program studi asal selinear dengan tujuan. "
            "Konversi nilai dan pengakuan SKS dilakukan oleh tim program studi tujuan. "
            "Maksimal SKS yang dapat diakui adalah 50% dari total SKS kurikulum. "
            "Mahasiswa transfer wajib menyelesaikan minimal 50% SKS di kampus tujuan."
        ),
    },

    # ── Sanksi & Pelanggaran ─────────────────────────────────────────────────
    {
        "id": "sanksi_01",
        "kategori": "Sanksi Akademik",
        "judul": "Jenis-Jenis Sanksi Akademik",
        "isi": (
            "Sanksi akademik dibagi menjadi: "
            "(1) Peringatan tertulis: untuk pelanggaran ringan seperti keterlambatan administrasi. "
            "(2) Skorsing: untuk pelanggaran sedang, berlaku 1–2 semester. "
            "(3) Pemberhentian (Drop Out/DO): untuk pelanggaran berat atau tidak memenuhi standar akademik. "
            "Pelanggaran kecurangan akademik (menyontek, plagiat) langsung dikenai nilai E untuk mata kuliah tersebut "
            "dan dapat berlanjut ke sanksi skorsing."
        ),
    },
    {
        "id": "sanksi_02",
        "kategori": "Sanksi Akademik",
        "judul": "Ketentuan Drop Out (DO)",
        "isi": (
            "Mahasiswa dapat dikeluarkan (DO) jika: "
            "(1) Melampaui batas masa studi (S1 maksimal 14 semester atau 7 tahun). "
            "(2) IPK di bawah 2.00 setelah evaluasi 4 semester pertama dan tidak ada perbaikan. "
            "(3) Terbukti melakukan pelanggaran berat (kriminal, narkoba, kekerasan). "
            "(4) Tidak aktif tanpa keterangan selama 2 semester berturut-turut. "
            "Proses DO melalui sidang Komisi Disiplin dan dapat diajukan banding."
        ),
    },

    # ── Wisuda & Kelulusan ───────────────────────────────────────────────────
    {
        "id": "wisuda_01",
        "kategori": "Wisuda dan Kelulusan",
        "judul": "Syarat Kelulusan dan Wisuda",
        "isi": (
            "Syarat yudisium dan wisuda: "
            "(1) Telah menyelesaikan seluruh SKS yang dipersyaratkan (min 144 SKS untuk S1). "
            "(2) IPK ≥ 2.00. "
            "(3) Tidak ada nilai E pada mata kuliah wajib. "
            "(4) Telah lulus sidang skripsi/tugas akhir. "
            "(5) Bebas tanggungan perpustakaan, laboratorium, dan keuangan. "
            "(6) Telah melengkapi semua dokumen administrasi kelulusan."
        ),
    },
    {
        "id": "wisuda_02",
        "kategori": "Wisuda dan Kelulusan",
        "judul": "Predikat Kelulusan",
        "isi": (
            "Predikat kelulusan berdasarkan IPK: "
            "Dengan Pujian/Cumlaude: IPK ≥ 3.51, masa studi ≤ n tahun (sesuai program), tanpa nilai D. "
            "Sangat Memuaskan: IPK 3.01–3.50. "
            "Memuaskan: IPK 2.76–3.00. "
            "Cukup: IPK 2.00–2.75. "
            "Predikat Cumlaude gugur jika mahasiswa pernah cuti atau masa studi melebihi batas normal."
        ),
    },

    # ── Beasiswa ─────────────────────────────────────────────────────────────
    {
        "id": "bea_01",
        "kategori": "Beasiswa",
        "judul": "Jenis Beasiswa yang Tersedia",
        "isi": (
            "Beasiswa yang tersedia di kampus: "
            "(1) Beasiswa Bidikmisi/KIP-K: untuk mahasiswa kurang mampu berprestasi, dibiayai pemerintah. "
            "(2) Beasiswa Prestasi Akademik: IPK ≥ 3.50, tidak sedang menerima beasiswa lain. "
            "(3) Beasiswa Afirmasi: untuk mahasiswa dari daerah 3T (Terdepan, Terluar, Tertinggal). "
            "(4) Beasiswa dari mitra industri/swasta yang dikelola kampus. "
            "Informasi pendaftaran beasiswa tersedia di Biro Kemahasiswaan."
        ),
    },
    {
        "id": "bea_02",
        "kategori": "Beasiswa",
        "judul": "Syarat Umum Beasiswa Prestasi",
        "isi": (
            "Syarat umum beasiswa prestasi: "
            "(1) Mahasiswa aktif minimal semester 2. "
            "(2) IPK minimal 3.50 (dapat berbeda per jenis beasiswa). "
            "(3) Tidak sedang menerima beasiswa lain. "
            "(4) Berkelakuan baik (tidak dalam sanksi akademik). "
            "(5) Melampirkan surat rekomendasi dari DPA. "
            "(6) Mengisi formulir dan menyerahkan dokumen ke Biro Kemahasiswaan sesuai jadwal."
        ),
    },

    # ── FAQ Umum ─────────────────────────────────────────────────────────────
    {
        "id": "faq_01",
        "kategori": "FAQ Umum",
        "judul": "Cara Mendapatkan Transkrip Nilai",
        "isi": (
            "Transkrip nilai dapat diperoleh melalui: "
            "(1) SIAKAD: cetak transkrip sementara secara mandiri kapan saja. "
            "(2) Biro Akademik: minta transkrip resmi bertanda tangan dan stempel untuk keperluan formal. "
            "Transkrip resmi biasanya selesai dalam 3 hari kerja. "
            "Biaya cetak transkrip resmi sesuai tarif yang berlaku. "
            "Transkrip dalam bahasa Inggris tersedia untuk keperluan beasiswa/studi lanjut."
        ),
    },
    {
        "id": "faq_02",
        "kategori": "FAQ Umum",
        "judul": "Prosedur Mengurus Surat Keterangan Aktif",
        "isi": (
            "Surat Keterangan Mahasiswa Aktif diurus di Biro Akademik atau melalui SIAKAD. "
            "Dokumen yang diperlukan: KTM (Kartu Tanda Mahasiswa) atau nomor NIM. "
            "Surat selesai dalam 1 hari kerja. "
            "Dapat digunakan untuk: beasiswa, keringanan biaya, dispensasi pekerjaan, dll. "
            "Masa berlaku surat biasanya 3 bulan sejak diterbitkan."
        ),
    },
    {
        "id": "faq_03",
        "kategori": "FAQ Umum",
        "judul": "Ketentuan Mahasiswa Aktif dan Registrasi Ulang",
        "isi": (
            "Mahasiswa dinyatakan aktif jika telah melakukan registrasi ulang setiap semester. "
            "Registrasi ulang meliputi: pembayaran UKT/biaya kuliah dan pengisian FRS. "
            "Mahasiswa yang tidak registrasi ulang dinyatakan non-aktif pada semester tersebut. "
            "Semester non-aktif tanpa izin cuti tetap dihitung sebagai masa studi. "
            "Untuk aktif kembali setelah non-aktif, mahasiswa harus mengajukan permohonan ke Dekan."
        ),
    },
    {
        "id": "faq_04",
        "kategori": "FAQ Umum",
        "judul": "Cara Mengganti Dosen Pembimbing Akademik",
        "isi": (
            "Pergantian DPA dapat dilakukan dengan alasan: DPA tidak dapat dihubungi lebih dari 1 semester, "
            "konflik kepentingan, atau DPA sudah tidak bertugas di kampus. "
            "Prosedur: ajukan permohonan tertulis ke Ketua Program Studi, "
            "sertakan alasan yang jelas. "
            "Keputusan pergantian DPA ada di tangan Ketua Program Studi. "
            "Penggantian tidak mempengaruhi nilai atau status akademik mahasiswa."
        ),
    },
    {
        "id": "faq_05",
        "kategori": "FAQ Umum",
        "judul": "Penggunaan SIAKAD (Sistem Informasi Akademik)",
        "isi": (
            "SIAKAD adalah sistem informasi akademik online kampus. "
            "Fitur SIAKAD: pengisian FRS, melihat jadwal kuliah, melihat nilai, "
            "cetak transkrip sementara, melihat tagihan UKT, pengumuman akademik. "
            "Akses SIAKAD menggunakan NIM sebagai username dan password awal yang diberikan saat registrasi. "
            "Jika lupa password, hubungi helpdesk IT kampus atau Biro Akademik. "
            "SIAKAD dapat diakses 24 jam melalui browser di siakad.[namakampus].ac.id."
        ),
    },
    {
        "id": "faq_06",
        "kategori": "FAQ Umum",
        "judul": "Batas Masa Studi Program Sarjana",
        "isi": (
            "Masa studi normal program Sarjana (S1) adalah 8 semester (4 tahun). "
            "Batas maksimal masa studi S1 adalah 14 semester (7 tahun). "
            "Masa cuti resmi tidak dihitung dalam masa studi. "
            "Mahasiswa yang mendekati batas masa studi akan mendapat surat peringatan. "
            "Jika melebihi batas maksimal tanpa menyelesaikan studi, mahasiswa akan di-DO."
        ),
    },
]


def get_all_chunks() -> list[str]:
    """Mengembalikan semua dokumen sebagai list string untuk di-embed."""
    chunks = []
    for doc in DOCUMENTS:
        text = (
            f"[{doc['kategori']}] {doc['judul']}\n\n"
            f"{doc['isi']}"
        )
        chunks.append(text)
    return chunks
