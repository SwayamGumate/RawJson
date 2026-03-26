document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const themeToggle = document.getElementById('theme-toggle');
    const rawInput = document.getElementById('raw-input');
    const sqlInput = document.getElementById('sql-input');
    const sqlWrapper = document.getElementById('sql-input-wrapper');
    const fileUpload = document.getElementById('file-upload');
    const fileNameDisplay = document.getElementById('file-name');
    const inputTitle = document.getElementById('input-title');
    const actionBtn = document.getElementById('action-btn');
    
    // Buttons
    const sampleDataBtn = document.getElementById('sample-data-btn');
    const clearBtn = document.getElementById('clear-btn');
    const copyBtn = document.getElementById('copy-btn');
    const downloadJsonBtn = document.getElementById('download-json-btn');
    const downloadCsvBtn = document.getElementById('download-csv-btn');
    
    // Output Areas
    const tabBtns = document.querySelectorAll('.tab-btn');
    const toolBtns = document.querySelectorAll('.tool-btn');
    const views = document.querySelectorAll('.view-content');
    const jsonOutput = document.getElementById('json-output');
    const tableOutput = document.getElementById('table-output');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');

    // --- State ---
    let currentParsedData = null; // Store successful parsed JSON data
    let uploadedFile = null;
    let currentMode = 'raw-to-json'; // 'raw-to-json', 'json-to-table', 'sql-playground'

    // --- Theme Management ---
    const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    themeToggle.addEventListener('click', () => {
        const cTheme = document.documentElement.getAttribute('data-theme');
        const nTheme = cTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', nTheme);
        localStorage.setItem('theme', nTheme);
        updateThemeIcon(nTheme);
    });

    function updateThemeIcon(theme) {
        const i = themeToggle.querySelector('i');
        i.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }

    // --- Tool Switching ---
    toolBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            toolBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMode = btn.getAttribute('data-tool');
            
            // Adjust UI based on mode
            if (currentMode === 'raw-to-json') {
                inputTitle.textContent = "Input: Raw Data";
                rawInput.placeholder = "Paste your raw data, key:value pairs, CSV, or malformed JSON here...";
                sqlWrapper.classList.add('hidden');
                actionBtn.innerHTML = '<i class="fas fa-rocket"></i> Convert to JSON';
            } else if (currentMode === 'json-to-table') {
                inputTitle.textContent = "Input: JSON Data";
                rawInput.placeholder = "Paste your valid JSON array here...";
                sqlWrapper.classList.add('hidden');
                actionBtn.innerHTML = '<i class="fas fa-table"></i> Generate Table';
            } else if (currentMode === 'sql-playground') {
                inputTitle.textContent = "Input: JSON Table Source";
                rawInput.placeholder = "Paste JSON data here to act as the 'data' table source...";
                sqlWrapper.classList.remove('hidden');
                actionBtn.innerHTML = '<i class="fas fa-play"></i> Run SQL Query';
                if (!sqlInput.value) sqlInput.value = "SELECT * FROM data LIMIT 10;";
            }
        });
    });

    // --- Tab Switching ---
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            views.forEach(v => v.classList.add('hidden'));
            
            btn.classList.add('active');
            const target = btn.getAttribute('data-target');
            document.getElementById(target).classList.remove('hidden');
        });
    });

    // --- File Upload Handling ---
    fileUpload.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadedFile = e.target.files[0];
            fileNameDisplay.textContent = uploadedFile.name;
        } else {
            uploadedFile = null;
            fileNameDisplay.textContent = 'No file chosen (.txt, .csv, .json)';
        }
    });

    // --- Utilities ---
    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
        setTimeout(() => {
            errorMessage.classList.add('hidden');
        }, 5000);
    }

    function showLoading() {
        loadingSpinner.classList.remove('hidden');
    }

    function hideLoading() {
        loadingSpinner.classList.add('hidden');
    }

    function switchTab(targetId) {
        const btn = document.querySelector(`.tab-btn[data-target="${targetId}"]`);
        if (btn) btn.click();
    }

    // --- Clear & Sample Data ---
    clearBtn.addEventListener('click', () => {
        rawInput.value = '';
        if (currentMode === 'sql-playground') {
            sqlInput.value = "SELECT * FROM data LIMIT 10;";
        }
        fileUpload.value = '';
        uploadedFile = null;
        fileNameDisplay.textContent = 'No file chosen (.txt, .csv, .json)';
        jsonOutput.textContent = 'Output will appear here...';
        tableOutput.innerHTML = 'Table will appear here...';
        currentParsedData = null;
        errorMessage.classList.add('hidden');
    });

    sampleDataBtn.addEventListener('click', () => {
        if (currentMode === 'raw-to-json') {
            rawInput.value = `id: 1\nname: "John Doe"\nrole: "Admin"\n---\nid: 2\nname: "Jane Smith"\nrole: "User"`;
        } else {
            rawInput.value = `[\n  {"id": 1, "name": "John Doe", "role": "Admin", "score": 95},\n  {"id": 2, "name": "Jane Smith", "role": "User", "score": 88},\n  {"id": 3, "name": "Sam Lake", "role": "User", "score": 72}\n]`;
        }
    });

    // --- Execution Pipeline ---
    actionBtn.addEventListener('click', async () => {
        if (currentMode === 'raw-to-json') {
            await runConversion('/convert/raw-to-json', 'json-view');
        } else if (currentMode === 'json-to-table') {
            await runConversion('/convert/json-to-table', 'table-view');
        } else if (currentMode === 'sql-playground') {
            await runSQL();
        }
    });

    async function runConversion(endpoint, targetView) {
        showLoading();
        errorMessage.classList.add('hidden');
        
        const formData = new FormData();
        const textData = rawInput.value.trim();
        
        if (uploadedFile) {
            formData.append('file', uploadedFile);
        } else if (textData) {
            formData.append('data', textData);
        } else {
            hideLoading();
            showError("Please provide input data.");
            return;
        }

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            const isJsonResp = response.headers.get('content-type')?.includes('application/json');
            if (!response.ok) {
                const errorData = isJsonResp ? await response.json() : await response.text();
                throw new Error(errorData.error || 'Conversion failed. Invalid format.');
            }

            if (endpoint === '/convert/raw-to-json') {
                const result = await response.json();
                currentParsedData = result;
                jsonOutput.textContent = JSON.stringify(result, null, 4);
                switchTab('json-view');
            } else if (endpoint === '/convert/json-to-table') {
                const result = await response.json();
                tableOutput.innerHTML = result.table;
                switchTab('table-view');
            }
        } catch (error) {
            showError(error.message);
        } finally {
            hideLoading();
        }
    }

    async function runSQL() {
        showLoading();
        errorMessage.classList.add('hidden');
        const textData = rawInput.value.trim();
        const queryText = sqlInput.value.trim();

        if (!textData && !uploadedFile) {
            hideLoading();
            showError("Please provide JSON data source.");
            return;
        }
        if (!queryText) {
            hideLoading();
            showError("Please provide an SQL query.");
            return;
        }

        try {
            // First we must resolve the data input (especially if it's a file)
            let jsonData = textData;
            if (uploadedFile) {
                const fileText = await uploadedFile.text();
                jsonData = fileText;
            }

            // We must parse it to send via JSON body
            let parsedArgs;
            try {
                parsedArgs = JSON.parse(jsonData);
            } catch(e) {
                throw new Error("Input must be valid JSON to be loaded into SQL table.");
            }

            const response = await fetch('/query/run-sql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data: parsedArgs, query: queryText })
            });

            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'SQL Execution failed');
            
            // Render result
            currentParsedData = result.result;
            jsonOutput.textContent = JSON.stringify(result.result, null, 4);
            
            // Also automatically render it as a table in the UI
            renderTableLocally(result.result);
            switchTab('table-view');

        } catch (error) {
            showError(error.message);
        } finally {
            hideLoading();
        }
    }

    function renderTableLocally(data) {
        if (!Array.isArray(data)) data = [data];
        if (data.length === 0) {
            tableOutput.innerHTML = "<p style='padding:1rem;'>No results formatting to table.</p>";
            return;
        }
        const cols = Object.keys(data[0] || {});
        let html = '<table class="data-table"><thead><tr>';
        cols.forEach(c => html += `<th>${c}</th>`);
        html += '</tr></thead><tbody>';
        data.forEach(row => {
            html += '<tr>';
            cols.forEach(c => html += `<td>${row[c]}</td>`);
            html += '</tr>';
        });
        html += '</tbody></table>';
        tableOutput.innerHTML = html;
    }

    // --- Actions ---
    copyBtn.addEventListener('click', () => {
        const activeTab = document.querySelector('.tab-btn.active').getAttribute('data-target');
        let textToCopy = '';
        
        if (activeTab === 'json-view') {
            textToCopy = jsonOutput.textContent;
        } else if (activeTab === 'table-view') {
            const table = document.getElementById('table-output').querySelector('table');
            if (table) {
                const rows = Array.from(table.querySelectorAll('tr'));
                textToCopy = rows.map(row => Array.from(row.querySelectorAll('th, td')).map(c => c.innerText).join('\t')).join('\n');
            }
        }
        
        if (textToCopy && textToCopy !== 'Output will appear here...' && textToCopy !== 'Table will appear here...') {
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => { copyBtn.innerHTML = originalText; }, 2000);
            });
        } else {
            showError("Nothing valid to copy.");
        }
    });

    downloadJsonBtn.addEventListener('click', () => {
        if (!currentParsedData) {
            showError("No valid JSON loaded to download.");
            return;
        }
        downloadFile(JSON.stringify(currentParsedData, null, 4), 'rawjson_output.json', 'application/json');
    });

    downloadCsvBtn.addEventListener('click', () => {
        const table = document.getElementById('table-output').querySelector('table');
        if (!table) {
            showError("No table data to download.");
            return;
        }
        const rows = Array.from(table.querySelectorAll('tr'));
        const csvContent = rows.map(row => Array.from(row.querySelectorAll('th, td')).map(c => `"${c.innerText.replace(/"/g, '""')}"`).join(',')).join('\n');
        downloadFile(csvContent, 'rawjson_output.csv', 'text/csv');
    });

    function downloadFile(content, filename, type) {
        const blob = new Blob([content], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
});
