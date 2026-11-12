from mcp.server.apps import Apps, ResourceCsp

APP_URI = "ui://google-news/search.html"

apps = Apps()


NEWS_APP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Google News Intelligence</title>

    <style>
        :root {
            --bg: #f8fafc;
            --surface: #ffffff;
            --border: #e2e8f0;
            --input-border: #cbd5e1;
            --text: #1e293b;
            --muted: #64748b;
            --accent: #2563eb;
            --accent-soft: #eff6ff;
            --error: #b91c1c;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #0f172a;
                --surface: #1e293b;
                --border: #334155;
                --input-border: #475569;
                --text: #e2e8f0;
                --muted: #94a3b8;
                --accent: #60a5fa;
                --accent-soft: #172554;
                --error: #f87171;
            }
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 24px;
            margin: 0;
        }

        .container {
            max-width: 750px;
            margin: 30px auto;
        }

        h1 {
            font-size: 30px;
            margin: 0 0 8px;
        }

        h2 {
            font-size: 15px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--muted);
            margin: 0 0 10px;
        }

        .subtitle {
            color: var(--muted);
            margin: 0 0 28px;
        }

        form {
            display: flex;
            gap: 10px;
            margin-bottom: 16px;
        }

        input {
            flex: 1;
            min-width: 0;
            padding: 14px;
            border: 1px solid var(--input-border);
            border-radius: 9px;
            font-size: 15px;
            background: var(--surface);
            color: var(--text);
        }

        button {
            padding: 14px 22px;
            border: none;
            border-radius: 9px;
            background: var(--accent);
            color: white;
            font-weight: bold;
            cursor: pointer;
            white-space: nowrap;
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        #status {
            color: var(--muted);
            font-size: 14px;
            margin: 16px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        #status.error {
            color: var(--error);
        }

        .spinner {
            width: 14px;
            height: 14px;
            border: 2px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            flex: none;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .panel {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px;
            margin-top: 16px;
        }

        .briefing {
            background: var(--accent-soft);
        }

        .briefing p {
            white-space: pre-line;
            line-height: 1.55;
            margin: 0;
        }

        .tools {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 14px;
        }

        .chip {
            font-size: 12px;
            color: var(--muted);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 4px 10px;
            background: var(--surface);
        }

        .chip strong {
            color: var(--text);
        }

        .section-title {
            margin-top: 28px;
        }

        .article {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px;
            margin-top: 12px;
        }

        .article h3 {
            font-size: 16px;
            line-height: 1.4;
            margin: 0 0 6px;
        }

        .article a {
            color: var(--accent);
            text-decoration: none;
        }

        .article a:hover {
            text-decoration: underline;
        }

        .article-meta {
            color: var(--muted);
            font-size: 13px;
            margin: 0;
        }

        @media (max-width: 500px) {
            body {
                padding: 16px;
            }

            form {
                flex-direction: column;
            }
        }
    </style>
</head>

<body>

<div class="container">

    <h1>Google News Intelligence</h1>

    <p class="subtitle">
        Ask Gemini to find and analyse news from Google News.
    </p>

    <form id="search-form">
        <input
            id="question"
            type="text"
            placeholder="Ask a question about the news..."
            value="Find the latest AI infrastructure news from BBC"
            aria-label="Your question"
            minlength="2"
            maxlength="300"
            required
        />

        <button id="search-button" type="submit" disabled>
            Search with Gemini
        </button>
    </form>

    <p id="status" role="status">Connecting to MCP server...</p>

    <section id="results" aria-live="polite"></section>

</div>

<script type="module">

    // Self-contained build of the official MCP Apps SDK (no further imports).
    // esm.sh's re-bundled build of this package crashes on load, so we load
    // the package's own "app-with-deps" bundle as a raw file from jsDelivr.
    const SDK_URL =
        "https://cdn.jsdelivr.net/npm/@modelcontextprotocol/ext-apps@2.0.4/dist/src/app-with-deps.js";

    // Gemini may run several tool rounds; allow more than the SDK's 60s default.
    const ANALYSIS_TIMEOUT_MS = 120000;

    let app = null;

    const form = document.getElementById("search-form");
    const questionInput = document.getElementById("question");
    const searchButton = document.getElementById("search-button");
    const status = document.getElementById("status");
    const results = document.getElementById("results");

    function setStatus(text, { busy = false, error = false } = {}) {
        status.replaceChildren();
        status.classList.toggle("error", error);

        if (busy) {
            const spinner = document.createElement("span");
            spinner.className = "spinner";
            spinner.setAttribute("aria-hidden", "true");
            status.appendChild(spinner);
        }

        status.appendChild(document.createTextNode(text));
    }

    function element(tag, className, text) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text !== undefined) node.textContent = text;
        return node;
    }

    function formatDate(value) {
        if (!value) return "";
        const date = new Date(value);
        return Number.isNaN(date.getTime())
            ? ""
            : date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
    }

    function readPayload(result) {
        if (result.structuredContent) return result.structuredContent;

        const text = (result.content || [])
            .filter(item => item.type === "text")
            .map(item => item.text)
            .join("\\n");

        try {
            return JSON.parse(text);
        } catch {
            return null;
        }
    }

    function errorText(result) {
        const text = (result.content || [])
            .filter(item => item.type === "text")
            .map(item => item.text)
            .join(" ")
            .trim();
        return text || "The Gemini analysis failed.";
    }

    function renderBriefing(payload) {
        const panel = element("div", "panel briefing");
        panel.appendChild(element("h2", "", "Gemini's briefing"));
        panel.appendChild(element("p", "", payload.briefing || "No briefing returned."));

        const toolCalls = payload.tool_calls || [];
        if (toolCalls.length) {
            const tools = element("div", "tools");

            for (const call of toolCalls) {
                const chip = element("span", "chip");
                chip.appendChild(element("strong", "", call.name));

                const args = Object.entries(call.arguments || {})
                    .map(([key, value]) => `${key}: ${value}`)
                    .join(", ");
                const outcome = call.error
                    ? `failed: ${call.error}`
                    : `${call.article_count} articles`;

                chip.appendChild(document.createTextNode(
                    [args, outcome].filter(Boolean).map(s => ` · ${s}`).join("")
                ));
                tools.appendChild(chip);
            }

            panel.appendChild(tools);
        }

        results.appendChild(panel);
    }

    function renderArticle(article) {
        const card = element("article", "article");
        const heading = element("h3");
        const link = element("a", "", article.title || "Untitled article");

        try {
            const url = new URL(article.url);

            if (url.protocol === "https:" || url.protocol === "http:") {
                link.href = url.href;
                link.target = "_blank";
                link.rel = "noopener noreferrer";
            }
        } catch {
            // Display the headline even if its URL is invalid.
        }

        heading.appendChild(link);
        card.appendChild(heading);
        card.appendChild(element(
            "p",
            "article-meta",
            [article.publisher, formatDate(article.published_at)].filter(Boolean).join(" · ")
        ));

        return card;
    }

    function renderAnalysis(payload) {
        results.replaceChildren();

        if (!payload) {
            setStatus("Gemini returned an unexpected response.", { error: true });
            return;
        }

        const articles = payload.articles || [];
        const calls = (payload.tool_calls || []).length;

        setStatus(
            `Gemini made ${calls} tool call${calls === 1 ? "" : "s"} ` +
            `and found ${articles.length} article${articles.length === 1 ? "" : "s"}.`
        );

        renderBriefing(payload);

        if (!articles.length) return;

        results.appendChild(element("h2", "section-title", `Relevant articles (${articles.length})`));

        for (const article of articles) {
            results.appendChild(renderArticle(article));
        }
    }

    async function initialize() {

        // Import dynamically so a failed SDK download is reported in the UI
        // instead of silently leaving the app stuck on "Connecting...".
        let App;

        try {
            ({ App } = await import(SDK_URL));
        } catch (error) {
            setStatus(`Failed to load the MCP Apps SDK: ${error.message}`, { error: true });
            return;
        }

        app = new App(
            {
                name: "Google News Intelligence",
                version: "1.1.0"
            },
            {}
        );

        // Receive the initial question provided when the app is opened.
        app.ontoolinput = (params) => {
            const initial = params.arguments?.question ?? params.arguments?.query;

            if (typeof initial === "string" && initial.trim()) {
                questionInput.value = initial;
            }
        };

        try {
            await app.connect();
            setStatus("Connected. Ask Gemini a question about the news.");
            searchButton.disabled = false;
        } catch (error) {
            setStatus(`Connection failed: ${error.message}`, { error: true });
        }
    }

    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        const question = questionInput.value.trim();

        if (question.length < 2) {
            setStatus("Enter at least two characters.", { error: true });
            return;
        }

        searchButton.disabled = true;
        results.replaceChildren();

        const started = Date.now();
        const working = () => setStatus(
            `Gemini is choosing tools and reading Google News... ` +
            `${Math.round((Date.now() - started) / 1000)}s`,
            { busy: true }
        );
        working();
        const timer = setInterval(working, 1000);

        try {
            const response = await app.callServerTool(
                {
                    name: "analyze_news_with_gemini",
                    arguments: { question }
                },
                { timeout: ANALYSIS_TIMEOUT_MS }
            );

            clearInterval(timer);

            if (response.isError) {
                setStatus(errorText(response), { error: true });
                return;
            }

            renderAnalysis(readPayload(response));

        } catch (error) {

            clearInterval(timer);
            setStatus(`Search failed: ${error.message}`, { error: true });

        } finally {

            searchButton.disabled = false;

        }

    });

    initialize();

</script>

</body>
</html>
"""


@apps.tool(
    resource_uri=APP_URI,
    name="open_google_news_app",
    title="Google News Intelligence",
    description="Open the interactive Google News interface, powered by Gemini.",
)
def open_google_news_app(
    question: str = "Find the latest AI infrastructure news from BBC",
) -> str:
    """Open the Google News interface."""

    return f"Google News interface opened for: {question}"


apps.add_html_resource(
    APP_URI,
    NEWS_APP_HTML,
    name="Google News Intelligence",
    title="Google News Intelligence",
    description="Interactive Google News search interface powered by Gemini.",
    csp=ResourceCsp(
        resource_domains=["https://cdn.jsdelivr.net"],
    ),
)
