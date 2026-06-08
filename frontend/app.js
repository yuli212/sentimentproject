// 1. Ganti dengan Invoke URL dari API Gateway-mu
const API_URL = "https://53rhocdog2.execute-api.us-east-1.amazonaws.com/dev";

// 2. Fungsi Utama (Wajib menggunakan 'async')
async function cariBerita() {
    // Capture element from HTML
    const keyword = document.getElementById("keywordInput").value;
    const resultsArea = document.getElementById("resultsArea");
    
    // Validate empty input
    if (!keyword) {
        alert("Please enter a keyword!");
        return;
    }

    // Display loading indicator
    resultsArea.innerHTML = "<p style='text-align:center; color:#3498db;'>Fetching and analyzing 10 news articles from the cloud... 🔍</p>";
    // Try-catch block for API call
    try {
        const response = await fetch(`${API_URL}/analyze?keyword=${keyword}`);
        const result = await response.json();

        // Validate if no data found
        if (!result.data || result.data.length === 0) {
            resultsArea.innerHTML = `<p style="color: red; text-align:center;">No news found for "${keyword}".</p>`;
            return;
        }

        // Open grid wrapper
        let htmlContent = `<div class="news-grid">`;

        // Loop through 10 data from Lambda
        result.data.forEach((news, index) => {
            let badgeClass = "neutral";
            if (news.sentiment === "POSITIVE") badgeClass = "positive";
            if (news.sentiment === "NEGATIVE") badgeClass = "negative";

            // Use dynamic illustration image
            const randomImage = `https://picsum.photos/seed/${keyword}${index}/400/200`;

            // Build HTML structure for each card
            htmlContent += `
                <div class="result-card">
                    <img src="${randomImage}" alt="News Illustration" class="news-image">
                    
                    <div class="card-content">
                        <div class="news-title">${news.title}</div>
                        <a href="${news.link}" target="_blank" class="news-link">Read Original Source &rarr;</a>
                        
                        <div class="sentiment-box">
                            <span class="badge ${badgeClass}">${news.sentiment}</span>
                            <span class="confidence">${news.confidence}% Score</span>
                        </div>
                    </div>
                </div>
            `;
        });

        // Close grid wrapper
        htmlContent += `</div>`;
        
        // Insert all cards to screen
        resultsArea.innerHTML = htmlContent;
        
    } catch (error) {
        resultsArea.innerHTML = `<p style="color: red; text-align:center;">Failed to connect to API: ${error.message}</p>`;
    }
}