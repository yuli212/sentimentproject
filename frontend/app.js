// 1. API Gateway URL
const API_URL = "https://53rhocdog2.execute-api.us-east-1.amazonaws.com/dev";

// 2. Tab navigation
function switchTab(tabName) {
    document.getElementById("tab-search").style.display = (tabName === "search") ? "flex" : "none";
    document.getElementById("tab-history").style.display = (tabName === "history") ? "flex" : "none";

    document.getElementById("tab-btn-search").classList.toggle("active", tabName === "search");
    document.getElementById("tab-btn-history").classList.toggle("active", tabName === "history");

    if (tabName === "history") {
        currentPage = 1;
        fetchHistoryPage(1);
    }
}

// 3. Search and Analyze News
async function searchNews() {
    const keyword = document.getElementById("keywordInput").value;
    const resultsArea = document.getElementById("resultsArea");

    if (!keyword) {
        alert("Please enter a keyword!");
        return;
    }

        resultsArea.innerHTML = "<div style='width: 100%; display: flex; justify-content: center;'><p style='color: #64748b; margin-top: 40px; font-weight: 500;'>Fetching and analyzing 10 news articles...</p></div>";

    try {
        const response = await fetch(`${API_URL}/analyze?keyword=${keyword}`);
        const result = await response.json();

        if (!result.data || result.data.length === 0) {
            resultsArea.innerHTML = `<p style="color: red; text-align:center;">No news found for "${keyword}".</p>`;
            return;
        }

        let htmlContent = `<div class="news-list">`;

        result.data.forEach((news) => {
            let badgeClass = "neutral";
            if (news.sentiment === "POSITIVE") badgeClass = "positive";
            if (news.sentiment === "NEGATIVE") badgeClass = "negative";

            const publishDate = news.date || "Unknown release time";

            htmlContent += `
                <div class="list-item">
                    <div class="news-meta">${publishDate}</div>
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

// 4. Pagination state
let currentPage = 1;
const ROWS_PER_PAGE = 20;

// 5. Fetch a specific page from the backend
async function fetchHistoryPage(page) {
    const historyBody = document.getElementById("historyBody");
    const paginationControls = document.getElementById("paginationControls");

    historyBody.innerHTML = `<tr><td colspan='4' style='text-align:center;'>Loading page ${page}...</td></tr>`;
    paginationControls.style.display = "none";

    try {
        const response = await fetch(`${API_URL}/history?page=${page}&limit=${ROWS_PER_PAGE}`);
        const result = await response.json();

        if (response.ok && result.data) {
            currentPage = result.pagination.page;
            renderHistoryPage(result.data, result.pagination);
        } else {
            historyBody.innerHTML = `<tr><td colspan='4' style='text-align:center; color:red;'>Failed to load history: ${result.error || result.message}</td></tr>`;
        }
    } catch (error) {
        console.error("Error fetching history:", error);
        historyBody.innerHTML = "<tr><td colspan='4' style='text-align:center; color:red;'>Network error while fetching history.</td></tr>";
    }
}

// 6. Render the page data returned by the backend
function renderHistoryPage(pageData, pagination) {
    const historyBody = document.getElementById("historyBody");
    const paginationControls = document.getElementById("paginationControls");
    const pageIndicator = document.getElementById("pageIndicator");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");

    if (pageData.length === 0) {
        historyBody.innerHTML = "<tr><td colspan='4' style='text-align:center;'>No analysis history found.</td></tr>";
        paginationControls.style.display = "none";
        return;
    }

    let htmlContent = "";
    pageData.forEach((item) => {
        const formattedDate = new Date(item.Timestamp).toLocaleString("id-ID");
        const badgeClass = item.Sentiment.toLowerCase();

        htmlContent += `
            <tr>
                <td style="white-space: nowrap;">${formattedDate}</td>
                <td><strong>${item.Keyword}</strong></td>
                <td><span class="badge ${badgeClass}">${item.Sentiment}</span></td>
                <td>${item.Plain_Text || "Text not available"}</td>
            </tr>
        `;
    });

    historyBody.innerHTML = htmlContent;

    pageIndicator.innerText = `Page ${pagination.page} of ${pagination.totalPages}`;
    paginationControls.style.display = "flex";

    prevBtn.disabled = (pagination.page === 1);
    nextBtn.disabled = (pagination.page === pagination.totalPages);
    prevBtn.style.opacity = (pagination.page === 1) ? "0.5" : "1";
    nextBtn.style.opacity = (pagination.page === pagination.totalPages) ? "0.5" : "1";
}

// 7. Handle Previous / Next button clicks
function changePage(direction) {
    fetchHistoryPage(currentPage + direction);
    document.getElementById("tab-history").scrollIntoView({ behavior: "smooth" });
}
