

let API_BASE = window.API_BASE || '/api';
const DEFAULT_API = 'https://bayesian-inference-lab.onrender.com/api';
const isVercel = window.location.hostname.includes('vercel.app');
const API_FALLBACKS = [
    window.API_BASE,
    isVercel ? DEFAULT_API : '/api',
    isVercel ? '/api' : DEFAULT_API,
    DEFAULT_API
].filter(Boolean);


// State
let networks = [];
let currentNetwork = null;
let currentAlgorithm = 've';
let networkVis = null;
let currentEvidence = {};
let resizeHandlerBound = false;

// DOM Elements
const els = {
    navBtns: document.querySelectorAll('.nav-btn'),
    views: document.querySelectorAll('.view'),
    networkSelect: document.getElementById('networkSelect'),
    queryContainer: document.getElementById('queryVarContainer'),
    neuralStatus: document.getElementById('neuralStatus'),
    runBtn: document.getElementById('runBtn'),
    prob0: document.getElementById('prob0'),
    prob1: document.getElementById('prob1'),
    latency: document.getElementById('latency'),
    gibbsSettings: document.getElementById('gibbsSettings'),
    tabBtns: document.querySelectorAll('.tab-btn'),
    sampleRange: document.getElementById('sampleRange'),
    sampleVal: document.getElementById('sampleVal'),
    evidenceContainer: document.getElementById('evidenceContainer'),
    networkInfo: document.getElementById('networkInfo'),
    compareToggle: document.getElementById('compareToggle'),
    compareSettings: document.getElementById('compareSettings'),
    compareMode: document.getElementById('compareMode'),
    compareSection: document.getElementById('compareSection'),
    veProb0: document.getElementById('veProb0'),
    veProb1: document.getElementById('veProb1'),
    veLatency: document.getElementById('veLatency'),
    gibbsProb0: document.getElementById('gibbsProb0'),
    gibbsProb1: document.getElementById('gibbsProb1'),
    gibbsLatency: document.getElementById('gibbsLatency'),
    compareChartContainer: document.getElementById('compareChartContainer')
};

// Init
async function init() {
    console.log("Inference Lab: Initialization Started");
    console.log("Current API_BASE:", API_BASE);
    setupEventListeners();
    await fetchNetworks();
    setupAether();
    loadAppState();
    setupSplineLazyLoad();
    ensureVisNetwork();
    ensureGsap();

    if (!resizeHandlerBound) {
        window.addEventListener('resize', () => {
            if (networkVis) {
                networkVis.redraw();
                networkVis.fit();
            }
        });
        resizeHandlerBound = true;
    }
}

function ensureVisNetwork() {
    if (window.vis) return;
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/vis-network/standalone/umd/vis-network.min.js';
    script.async = true;
    script.onload = () => {
        console.log('vis-network loaded dynamically');
        if (currentNetwork) {
            renderNeuralMap();
        }
    };
    script.onerror = () => {
        console.warn('Failed to load vis-network dynamically');
    };
    document.head.appendChild(script);
}

function ensureGsap() {
    if (window.gsap) return;
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js';
    script.async = true;
    script.onload = () => {
        console.log('GSAP loaded dynamically');
    };
    script.onerror = () => {
        console.warn('Failed to load GSAP dynamically');
    };
    document.head.appendChild(script);
}

function setupEventListeners() {
    // View Switching
    els.navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const viewId = `view-${btn.dataset.view}`;
            els.navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            els.views.forEach(v => v.classList.remove('active'));
            document.getElementById(viewId).classList.add('active');
        });
    });

    els.networkSelect.addEventListener('change', (e) => {
        loadNetworkUI(e.target.value);
    });

    els.tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            els.tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentAlgorithm = btn.dataset.algo;
            if (currentAlgorithm === 'gibbs') {
                els.gibbsSettings.classList.remove('hidden');
            } else {
                els.gibbsSettings.classList.add('hidden');
            }
        });
    });

    els.sampleRange.addEventListener('input', (e) => {
        els.sampleVal.textContent = e.target.value;
    });

    if (els.compareToggle) {
        els.compareToggle.addEventListener('change', (e) => {
            setCompareUI(e.target.checked);
            applyCompareMode();
        });
    }

    if (els.compareMode) {
        els.compareMode.addEventListener('change', applyCompareMode);
    }

    els.runBtn.addEventListener('click', () => {
        runInference();
        triggerNeuralPulse();
    });
}

async function fetchNetworks() {
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    const fetchWithTimeout = async (url, timeoutMs = 15000) => {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeoutMs);
        try {
            return await fetch(url, {
                cache: 'no-store',
                mode: 'cors',
                signal: controller.signal
            });
        } finally {
            clearTimeout(id);
        }
    };

    const debugEl = document.getElementById('apiDebug');
    const debug = (msg) => {
        if (!debugEl) return;
        debugEl.classList.remove('hidden');
        debugEl.textContent = msg;
    };

    if (!els.networkSelect) {
        debug('API debug:\nMissing #networkSelect element in DOM.');
        return;
    }

    els.networkSelect.innerHTML = '<option>Warming backend... retrying</option>';
    debug('API debug: starting requests...');

    let lastErr = null;
    for (const base of API_FALLBACKS) {
        for (let attempt = 1; attempt <= 3; attempt++) {
            try {
                const res = await fetchWithTimeout(`${base}/networks`, 25000);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                networks = await res.json();
                API_BASE = base;
                if (debugEl) debugEl.classList.add('hidden');
                els.networkSelect.innerHTML = '<option value="" disabled selected>Select a Network...</option>';
                networks.forEach(net => {
                    const opt = document.createElement('option');
                    opt.value = net.name;
                    opt.textContent = net.name;
                    els.networkSelect.appendChild(opt);
                });
                if (networks.length > 0) {
                    els.networkSelect.value = networks[0].name;
                    try {
                        loadNetworkUI(networks[0].name);
                    } catch (uiErr) {
                        console.error("UI init error after networks loaded", uiErr);
                        debug(`API debug:\nNetworks loaded.\nUI error: ${uiErr?.message || uiErr}`);
                    }
                }
                return;
            } catch (err) {
                lastErr = err;
                console.error(`Failed to load networks from ${base} (attempt ${attempt})`, err);
                debug(`API debug:\nBase: ${base}\nAttempt: ${attempt}\nError: ${err?.message || err}\nHost: ${window.location.hostname}`);
                await sleep(1500 * attempt);
            }
        }
    }

    els.networkSelect.innerHTML = '<option>Error loading API (check backend URL)</option>';
    if (lastErr) {
        console.error("Failed to load networks from all API bases", lastErr);
        debug(`API debug:\nAll bases failed.\nLast error: ${lastErr?.message || lastErr}\nHost: ${window.location.hostname}`);
    }
}

function loadNetworkUI(networkName, isRestoring = false) {
    currentNetwork = networks.find(n => n.name === networkName);
    if (!currentNetwork) return;

    if (!els.queryContainer) return;
    els.queryContainer.innerHTML = '';
    currentNetwork.variables.forEach((v, idx) => {
        setupQueryVar(v, idx === 0);
    });

    updateNetworkInfo();
    renderNeuralMap();

    if (isRestoring) {
        Object.entries(currentEvidence).forEach(([nodeId, val]) => {
            const node = networkVis.body.data.nodes.get(nodeId);
            if (node) {
                if (val === 1) {
                    node.color = { background: '#10b981', border: '#fff' };
                    node.shadow = { color: 'rgba(16, 185, 129, 0.8)', size: 20 };
                } else {
                    node.color = { background: '#ef4444', border: '#fff' };
                    node.shadow = { color: 'rgba(239, 68, 68, 0.8)', size: 20 };
                }
                networkVis.body.data.nodes.update(node);
            }
        });
        updateNeuralStatusUI();
    } else if (window.gsap) {
        gsap.from(".glass-card", {
            duration: 0.8,
            y: 30,
            opacity: 0,
            stagger: 0.1,
            ease: "power2.out"
        });
    }

    saveAppState();
    showToast("State Auto-saved");
}

function renderNeuralMap() {
    if (!currentNetwork) return;

    const container = document.getElementById('neuralMap');
    if (!container) return;
    if (typeof vis === 'undefined' || !window.vis) {
        console.warn("vis-network not loaded; skipping neural map render.");
        return;
    }

    const nodes = currentNetwork.nodes.map(node => ({
        id: node,
        label: node,
        color: {
            background: 'rgba(2, 6, 23, 0.7)',
            border: '#06b6d4',
            highlight: { background: '#06b6d4', border: '#fff' }
        },
        font: { color: '#fff', size: 14, face: 'Outfit' },
        shape: 'dot',
        size: 25,
        shadow: { enabled: true, color: 'rgba(6, 182, 212, 0.4)', size: 10 }
    }));

    const edges = currentNetwork.edges.map(edge => ({
        from: edge[0],
        to: edge[1],
        arrows: 'to',
        color: { color: 'rgba(6, 182, 212, 0.3)', highlight: '#8b5cf6' },
        width: 2
    }));

    const data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
    const options = {
        physics: { enabled: true, barnesHut: { gravitationalConstant: -2000, centralGravity: 0.3, springLength: 150 } },
        interaction: { hover: true, selectConnectedEdges: false }
    };

    networkVis = new vis.Network(container, data, options);

    currentEvidence = {};
    updateNeuralStatusUI();

    networkVis.on("click", (params) => {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const queryVar = document.querySelector('input[name="queryVar"]:checked')?.value;
            if (nodeId === queryVar) {
                alert("Cannot set evidence on the target variable!");
                return;
            }
            toggleEvidence(nodeId);
        }
    });

    networkVis.on("hoverNode", () => { container.style.cursor = 'crosshair'; });
    networkVis.on("blurNode", () => { container.style.cursor = 'default'; });
}

function toggleEvidence(nodeId) {
    if (currentEvidence[nodeId] === 1) {
        currentEvidence[nodeId] = 0;
    } else if (currentEvidence[nodeId] === 0) {
        delete currentEvidence[nodeId];
    } else {
        currentEvidence[nodeId] = 1;
    }

    const node = networkVis.body.data.nodes.get(nodeId);
    if (currentEvidence[nodeId] === 1) {
        node.color = { background: '#10b981', border: '#fff' };
        node.shadow = { color: 'rgba(16, 185, 129, 0.8)', size: 20 };
    } else if (currentEvidence[nodeId] === 0) {
        node.color = { background: '#ef4444', border: '#fff' };
        node.shadow = { color: 'rgba(239, 68, 68, 0.8)', size: 20 };
    } else {
        node.color = { background: '#1a1f3a', border: '#6366f1' };
        node.shadow = { color: 'rgba(99, 102, 241, 0.4)', size: 10 };
    }
    networkVis.body.data.nodes.update(node);
    updateNeuralStatusUI();
    saveAppState();
}

function updateNeuralStatusUI() {
    if (!els.neuralStatus) return;
    const keys = Object.keys(currentEvidence);
    if (keys.length === 0) {
        els.neuralStatus.innerHTML = '<span style="opacity:0.5; font-style:italic">No neurons probed. Click map to set observations.</span>';
        return;
    }

    let html = '<div style="display:grid; grid-template-columns:1fr 1fr; gap:5px;">';
    keys.forEach(k => {
        const val = currentEvidence[k];
        const color = val === 1 ? '#10b981' : '#ef4444';
        html += `<div style="background:rgba(255,255,255,0.05); padding:4px 8px; border-radius:4px; font-size:0.75rem; border-left:3px solid ${color}">
                    ${k}: <strong>${val === 1 ? 'TRUE' : 'FALSE'}</strong>
                 </div>`;
    });
    html += '</div>';
    els.neuralStatus.innerHTML = html;
}

function setupQueryVar(varName, isChecked) {
    const label = document.createElement('label');
    label.className = 'radio-item';
    label.innerHTML = `
        <input type="radio" name="queryVar" value="${varName}" ${isChecked ? 'checked' : ''}>
        ${varName}
    `;
    label.querySelector('input').addEventListener('change', () => {
        // When query changes, clear evidence on that node if any
        if (currentEvidence[varName] !== undefined) {
            delete currentEvidence[varName];
            const node = networkVis.body.data.nodes.get(varName);
            node.color = { background: '#1a1f3a', border: '#6366f1' };
            networkVis.body.data.nodes.update(node);
            updateNeuralStatusUI();
        }
    });
    els.queryContainer.appendChild(label);
}

async function runInference() {
    if (!currentNetwork) return;

    const compareEnabled = els.compareToggle?.checked;
    if (!compareEnabled) {
            if (window.gsap) {
                gsap.to("#neuralMap", { scale: 0.98, duration: 0.1, yoyo: true, repeat: 1 });
            }
    }

    els.runBtn.innerHTML = compareEnabled
        ? '<i class="ri-loader-4-line ri-spin"></i> RUNNING VE + GIBBS...'
        : '<i class="ri-loader-4-line ri-spin"></i> PROBING NEURONS...';

    const queryVar = document.querySelector('input[name="queryVar"]:checked').value;
    const evidence = currentEvidence;
    const samples = parseInt(els.sampleRange.value);

    try {
        if (compareEnabled) {
            const payloadBase = {
                network: currentNetwork.name,
                query_var: queryVar,
                evidence: evidence,
                samples: samples
            };

            const [veData, gibbsData] = await Promise.all([
                fetchInference({ ...payloadBase, algorithm: 've' }),
                fetchInference({ ...payloadBase, algorithm: 'gibbs' })
            ]);

            updateCompareResults(veData, gibbsData);
        } else {
            const payload = {
                network: currentNetwork.name,
                algorithm: currentAlgorithm,
                query_var: queryVar,
                evidence: evidence,
                samples: samples
            };

            const data = await fetchInference(payload);
            updateResults(data);

            if (window.gsap) {
                gsap.from(".stat-card .value", {
                    textContent: 0,
                    duration: 1,
                    ease: "power2.out",
                    snap: { textContent: 0.0001 },
                    stagger: 0.2
                });
            }
        }
    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        els.runBtn.innerHTML = '<span class="btn-text">RUN INFERENCE</span><i class="ri-play-fill"></i>';
    }
}

function updateNetworkInfo() {
    if (!els.networkInfo || !currentNetwork) return;

    const nodes = currentNetwork.nodes || [];
    const edges = currentNetwork.edges || [];
    const n = nodes.length;
    const m = edges.length;

    const indeg = {};
    const outdeg = {};
    nodes.forEach(node => {
        indeg[node] = 0;
        outdeg[node] = 0;
    });
    edges.forEach(edge => {
        const [from, to] = edge;
        if (outdeg[from] !== undefined) outdeg[from] += 1;
        if (indeg[to] !== undefined) indeg[to] += 1;
    });

    const indegVals = Object.values(indeg);
    const outdegVals = Object.values(outdeg);
    const avgIn = indegVals.length ? (indegVals.reduce((a, b) => a + b, 0) / indegVals.length) : 0;
    const avgOut = outdegVals.length ? (outdegVals.reduce((a, b) => a + b, 0) / outdegVals.length) : 0;
    const density = n > 1 ? (m / (n * (n - 1))) : 0;

    const roots = nodes.filter(node => indeg[node] === 0);
    const leaves = nodes.filter(node => outdeg[node] === 0);

    const varsPreview = nodes.slice(0, 10).join(', ') + (nodes.length > 10 ? '...' : '');

    const cptSizes = currentNetwork.cpt_sizes || {};
    const stateCounts = currentNetwork.state_counts || {};
    const totalCpt = currentNetwork.total_cpt_entries ?? Object.values(cptSizes).reduce((a, b) => a + b, 0);

    const largestCpts = Object.entries(cptSizes)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map(([k, v]) => `${k} (${v})`)
        .join(', ');

    const statePreview = Object.entries(stateCounts)
        .slice(0, 6)
        .map(([k, v]) => `${k}: ${v}`)
        .join(', ');

    els.networkInfo.innerHTML = `
        <div><strong>Name:</strong> ${currentNetwork.name}</div>
        <div><strong>Nodes:</strong> ${n} &nbsp; <strong>Edges:</strong> ${m}</div>
        <div><strong>Density:</strong> ${density.toFixed(3)} &nbsp; <strong>Avg In:</strong> ${avgIn.toFixed(2)} &nbsp; <strong>Avg Out:</strong> ${avgOut.toFixed(2)}</div>
        <div><strong>Roots:</strong> ${roots.join(', ') || '-'}</div>
        <div><strong>Leaves:</strong> ${leaves.join(', ') || '-'}</div>
        <div><strong>Variables:</strong> ${varsPreview}</div>
        <div><strong>Total CPT entries:</strong> ${totalCpt}</div>
        <div><strong>Largest CPTs:</strong> ${largestCpts || '-'}</div>
        <div><strong>State counts:</strong> ${statePreview || '-'}</div>
    `;
}

async function fetchInference(payload) {
    const res = await fetch(`${API_BASE}/inference`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail);
    return data;
}

function updateResults(data) {
    // Stats
    els.prob0.className = 'value red';
    els.prob1.className = 'value green';
    els.latency.className = 'value cyan';

    els.prob0.textContent = (data.probabilities['0'] || 0).toFixed(4);
    els.prob1.textContent = (data.probabilities['1'] || 0).toFixed(4);
    els.latency.textContent = data.time_ms.toFixed(2) + ' ms';

    const trace = {
        x: ['FALSE (0)', 'TRUE (1)'],
        y: [data.probabilities['0'], data.probabilities['1']],
        type: 'bar',
        marker: { color: ['#ef4444', '#10b981'] },
        text: [data.probabilities['0']?.toFixed(4), data.probabilities['1']?.toFixed(4)],
        textposition: 'auto'
    };

    const layout = {
        title: { text: 'Probability Distribution', font: { color: '#fff' } },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#e0e7ff' },
        yaxis: { range: [0, 1] },
        margin: { t: 40, b: 40, l: 40, r: 40 }
    };

    const config = {
        displayModeBar: false,
        responsive: true,
        staticPlot: false
    };

    Plotly.newPlot('probabilityChart', [trace], layout, config);
}

function updateCompareResults(veData, gibbsData) {
    els.veProb0.textContent = (veData.probabilities['0'] || 0).toFixed(4);
    els.veProb1.textContent = (veData.probabilities['1'] || 0).toFixed(4);
    els.veLatency.textContent = veData.time_ms.toFixed(2) + ' ms';

    els.gibbsProb0.textContent = (gibbsData.probabilities['0'] || 0).toFixed(4);
    els.gibbsProb1.textContent = (gibbsData.probabilities['1'] || 0).toFixed(4);
    els.gibbsLatency.textContent = gibbsData.time_ms.toFixed(2) + ' ms';

    const traceVe = {
        x: ['FALSE (0)', 'TRUE (1)'],
        y: [veData.probabilities['0'], veData.probabilities['1']],
        type: 'bar',
        name: 'VE',
        marker: { color: '#06b6d4' }
    };

    const traceGibbs = {
        x: ['FALSE (0)', 'TRUE (1)'],
        y: [gibbsData.probabilities['0'], gibbsData.probabilities['1']],
        type: 'bar',
        name: 'Gibbs',
        marker: { color: '#8b5cf6' }
    };

    const layout = {
        title: { text: 'VE vs Gibbs Probability Comparison', font: { color: '#fff' } },
        barmode: 'group',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#e0e7ff' },
        yaxis: { range: [0, 1] },
        margin: { t: 40, b: 40, l: 40, r: 40 }
    };

    const config = {
        displayModeBar: false,
        responsive: true
    };

    Plotly.newPlot('compareChart', [traceVe, traceGibbs], layout, config);
}

function setCompareUI(isCompare) {
    const singleEls = document.querySelectorAll('.single-only');
    const compareEls = document.querySelectorAll('.compare-only');
    singleEls.forEach(el => el.classList.toggle('hidden', isCompare));
    compareEls.forEach(el => el.classList.toggle('hidden', !isCompare));

    if (els.compareSettings) {
        els.compareSettings.classList.toggle('hidden', !isCompare);
    }

    if (els.gibbsSettings) {
        const showGibbs = isCompare || currentAlgorithm === 'gibbs';
        els.gibbsSettings.classList.toggle('hidden', !showGibbs);
    }

    if (els.tabBtns) {
        els.tabBtns.forEach(btn => {
            btn.disabled = isCompare;
            btn.classList.toggle('disabled', isCompare);
        });
    }

    if (!isCompare && window.Plotly) {
        Plotly.purge('compareChart');
    }
}

function applyCompareMode() {
    if (!els.compareMode || !els.compareSection) return;
    const mode = els.compareMode.value;
    const showCards = mode === 'cards' || mode === 'both';
    const showChart = mode === 'chart' || mode === 'both';

    const cards = els.compareSection.querySelector('.compare-cards');
    if (cards) cards.classList.toggle('hidden', !showCards);
    if (els.compareChartContainer) {
        els.compareChartContainer.classList.toggle('hidden', !showChart);
    }
}

function setupAether() {
    const canvas = document.getElementById('aether-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width, height, particles = [];
    let mouse = { x: -1000, y: -1000, active: false };

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }

    class Particle {
        constructor() {
            this.init();
        }
        init() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.size = Math.random() * 2 + 1;
            this.baseX = this.x;
            this.baseY = this.y;
            this.speedX = (Math.random() - 0.5) * 0.5;
            this.speedY = (Math.random() - 0.5) * 0.5;
            this.alpha = Math.random() * 0.5 + 0.2;
            this.color = Math.random() > 0.5 ? '#06b6d4' : '#8b5cf6';
        }
        update() {
            // Natural drift
            this.x += this.speedX;
            this.y += this.speedY;

            // Interaction
            if (mouse.active) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    const force = (150 - dist) / 150;
                    this.x -= dx * force * 0.05;
                    this.y -= dy * force * 0.05;
                }
            }

            // Boundary wrap
            if (this.x < 0) this.x = width;
            if (this.x > width) this.x = 0;
            if (this.y < 0) this.y = height;
            if (this.y > height) this.y = 0;
        }
        draw() {
            ctx.fillStyle = this.color;
            ctx.globalAlpha = this.alpha;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.globalAlpha = 1;
        }
    }

    const count = window.innerWidth < 768 ? 50 : 100;
    for (let i = 0; i < count; i++) particles.push(new Particle());

    function animate() {
        ctx.clearRect(0, 0, width, height);
        particles.forEach(p => { p.update(); p.draw(); });
        requestAnimationFrame(animate);
    }

    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        mouse.active = true;
    });
    window.addEventListener('mouseleave', () => mouse.active = false);
    window.addEventListener('touchstart', (e) => {
        mouse.x = e.touches[0].clientX;
        mouse.y = e.touches[0].clientY;
        mouse.active = true;
    });
    window.addEventListener('touchend', () => mouse.active = false);

    resize();
    animate();
}

// --- Persistence ---

function saveAppState() {
    const state = {
        networkName: els.networkSelect.value,
        algorithm: currentAlgorithm,
        evidence: currentEvidence,
        samples: els.sampleRange.value,
        compareEnabled: els.compareToggle?.checked,
        compareMode: els.compareMode?.value
    };
    localStorage.setItem('inference_lab_state', JSON.stringify(state));
}

function loadAppState() {
    const saved = localStorage.getItem('inference_lab_state');
    if (!saved) {
        setCompareUI(false);
        applyCompareMode();
        return;
    }

    try {
        const state = JSON.parse(saved);
        if (state.networkName) els.networkSelect.value = state.networkName;
        if (state.algorithm) {
            currentAlgorithm = state.algorithm;
            els.tabBtns.forEach(btn => {
                btn.classList.toggle('active', btn.dataset.algo === currentAlgorithm);
            });
            els.gibbsSettings.classList.toggle('hidden', currentAlgorithm !== 'gibbs');
        }
        if (state.evidence) currentEvidence = state.evidence;
        if (state.samples) {
            els.sampleRange.value = state.samples;
            els.sampleVal.textContent = state.samples;
        }
        if (state.compareEnabled !== undefined && els.compareToggle) {
            els.compareToggle.checked = state.compareEnabled;
            setCompareUI(state.compareEnabled);
        }
        if (state.compareMode && els.compareMode) {
            els.compareMode.value = state.compareMode;
        }
        applyCompareMode();

        // Load the network specifically to restore map evidence
        if (state.networkName) loadNetworkUI(state.networkName, true);
    } catch (err) {
        console.error("Error loading state", err);
    }
}


function showToast(message) {
    let toast = document.getElementById('persistence-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'persistence-toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2000);
}

// --- Animations ---

function triggerNeuralPulse() {
    if (!networkVis || !currentNetwork) return;

    const queryVar = document.querySelector('input[name="queryVar"]:checked')?.value;
    const evidenceNodes = Object.keys(currentEvidence);

    // Animate edges from evidence to highlight "flow"
    const edges = networkVis.body.data.edges.get();
    edges.forEach(edge => {
        if (evidenceNodes.includes(edge.from)) {
            const originalColor = edge.color.color;
            networkVis.body.data.edges.update({
                id: edge.id,
                color: { color: '#06b6d4', opacity: 1 },
                width: 4
            });
            setTimeout(() => {
                networkVis.body.data.edges.update({
                    id: edge.id,
                    color: { color: originalColor },
                    width: 2
                });
            }, 1000);
        }
    });

    // Pulse the query node
    if (queryVar) {
        const node = networkVis.body.data.nodes.get(queryVar);
        if (node) {
            const originalShadow = node.shadow;
            networkVis.body.data.nodes.update({
                id: queryVar,
                shadow: { color: '#fff', size: 40 }
            });
            setTimeout(() => {
                networkVis.body.data.nodes.update({
                    id: queryVar,
                    shadow: originalShadow
                });
            }, 1500);
        }
    }
}

function setupSplineLazyLoad() {
    const spline = document.querySelector('spline-viewer');
    const loading = document.getElementById('splineLoading');
    const poster = document.getElementById('splinePoster');
    const mobileBtn = document.getElementById('splineMobileBtn');
    if (!spline) return;

    const url = spline.getAttribute('data-url');
    if (!url) return;

    const isMobile = window.innerWidth < 768;
    if (isMobile) {
        if (loading) loading.classList.add('hidden');
        if (mobileBtn) mobileBtn.classList.remove('hidden');
        if (mobileBtn) {
            mobileBtn.addEventListener('click', () => {
                if (loading) loading.classList.remove('hidden');
                startLoad();
            }, { once: true });
        }
        return;
    }

    const startLoad = () => {
        if (!spline.getAttribute('url')) {
            spline.setAttribute('url', url);
        }
    };

    const hideLoading = () => {
        if (loading) {
            if (window.gsap) {
                gsap.to(loading, { opacity: 0, duration: 0.5, onComplete: () => loading.classList.add('hidden') });
            } else {
                loading.classList.add('hidden');
            }
        }
        if (poster) {
            if (window.gsap) {
                gsap.to(poster, { opacity: 0, duration: 0.8, onComplete: () => poster.classList.add('hidden') });
            } else {
                poster.classList.add('hidden');
            }
        }
    };

    spline.addEventListener('load', hideLoading, { once: true });
    // Fallback: hide loader if Spline takes too long (keeps app usable)
    setTimeout(hideLoading, 10000);

    // Use Intersection Observer for more efficient loading
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            startLoad();
            observer.disconnect();
        }
    }, { threshold: 0.1 });

    observer.observe(spline);
}

init();

