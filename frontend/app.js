// 1. API Gateway URL
const API_URL = "https://53rhocdog2.execute-api.us-east-1.amazonaws.com/dev";

// 2. Main Function
async function cariBerita() {
    const keyword = document.getElementById("keywordInput").value;
    const resultsArea = document.getElementById("resultsArea");
    
    if (!keyword) {
        alert("Please enter a keyword!");
        return;
    }

    // Display loading indicator
    resultsArea.innerHTML = "<p style='text-align:center; color:#3498db;'>Fetching and analyzing 10 news articles from the cloud... 🔍</p>";

    try {
        // Call API Gateway directly without authentication headers
        const response = await fetch(`${API_URL}/analyze?keyword=${keyword}`);
        const result = await response.json();

        // Validate if no data found
        if (!result.data || result.data.length === 0) {
            resultsArea.innerHTML = `<p style="color: red; text-align:center;">No news found for "${keyword}".</p>`;
            return;
        }

        // Open news list wrapper
        let htmlContent = `<div class="news-list">`;

        result.data.forEach((news) => {
            let badgeClass = "neutral";
            if (news.sentiment === "POSITIVE") badgeClass = "positive";
            if (news.sentiment === "NEGATIVE") badgeClass = "negative";

            // Get publication date from Lambda
            // If not available, show unknown
            const publishDate = news.date || "Unknown release time";

            // Build HTML structure without image, add date meta
            htmlContent += `
                <div class="list-item">
                    <div class="news-meta">🕒 ${publishDate}</div>
                    
                    <div class="news-title">${news.title}</div>
                    <a href="${news.link}" target="_blank" class="news-link">Read Original Source &rarr;</a>
                    
                    <div class="sentiment-box">
                        <span class="badge ${badgeClass}">${news.sentiment}</span>
                        <span class="confidence">${news.confidence}% Score</span>
                    </div>
                </div>
            `;
        });

        htmlContent += `</div>`;
        resultsArea.innerHTML = htmlContent;
        
    } catch (error) {
        resultsArea.innerHTML = `<p style="color: red; text-align:center;">Failed to connect to API: ${error.message}</p>`;
    }
}