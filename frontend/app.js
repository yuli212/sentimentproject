// GANTI STRING DI BAWAH INI DENGAN INVOKE URL DARI API GATEWAY-MU
const API_URL = "https://53rhocdog2.execute-api.us-east-1.amazonaws.com/dev";

async function cariBerita() {
    const keyword = document.getElementById("keywordInput").value;
    const hasilArea = document.getElementById("hasilArea");
    
    if (!keyword) {
        alert("Mohon masukkan kata kunci terlebih dahulu!");
        return;
    }

    // Memberikan indikator loading
    hasilArea.innerHTML = "<p>Sedang mencari dan menganalisis berita... Mohon tunggu.</p>";

    try {
        // 1. Memanggil rute /get-news dari API Gateway-mu
        const response = await fetch(`${API_URL}/get-news?keyword=${keyword}`);
        const result = await response.json();

        // 2. Menampilkan respons mentah di layar untuk tahap debugging
        hasilArea.innerHTML = `
            <h3>Berhasil Terhubung! Berikut respons mentah dari Serverless-mu:</h3>
            <pre style="background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto;">
${JSON.stringify(result, null, 2)}
            </pre>
        `;
        
        console.log("Data berhasil ditarik:", result);

    } catch (error) {
        hasilArea.innerHTML = `<p style="color: red;">Gagal terhubung ke API: ${error.message}</p>`;
        console.error("Terjadi kesalahan:", error);
    }
}