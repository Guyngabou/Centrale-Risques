const API_URL = "/api/v1";

class CentraleRisquesApp {
    constructor() {
        this.token = localStorage.getItem('token');
        this.role = localStorage.getItem('role');
        this.userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        this.compagnieInfo = JSON.parse(localStorage.getItem('nom_compagnie') || '{}');
        this.init();
    }

    init() {
        if (this.token) {
            this.showApp();
        } else {
            this.showLogin();
        }

        this.attachEventListeners();
    }

    showLogin() {
        document.getElementById('auth-view').classList.remove('hidden');
        document.getElementById('app-view').classList.add('hidden');
    }

    showApp() {
        document.getElementById('auth-view').classList.add('hidden');
        document.getElementById('app-view').classList.remove('hidden');

        const compName = this.compagnieInfo.nom_compagnie || '';
        document.getElementById('user-info').textContent = `${this.userInfo.username} (${compName})`;

        if (this.role === 'ASAC') {
            document.getElementById('nav-asac').classList.remove('hidden');
            document.getElementById('nav-compagnie').classList.add('hidden');
            this.switchNav('asac-dash');
            this.loadStats();
        } else {
            document.getElementById('nav-compagnie').classList.remove('hidden');
            document.getElementById('nav-asac').classList.add('hidden');
            this.switchNav('compagnie-dash');
        }
    }

    attachEventListeners() {
        // Login
        document.getElementById('login-form').addEventListener('submit', (e) => this.handleLogin(e));

        // Logout
        document.getElementById('logout-btn').addEventListener('click', () => this.handleLogout());

        // Nav
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => this.switchNav(e.target.dataset.view));
        });

        // Search
        document.getElementById('search-form').addEventListener('submit', (e) => this.handleSearch(e));

        // Declare
        document.getElementById('declare-form').addEventListener('submit', (e) => this.handleDeclare(e));

        // Create User
        const createUserForm = document.getElementById('create-user-form');
        if (createUserForm) {

            createUserForm.addEventListener('submit', (e) => this.handleCreateUser(e));
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorEl = document.getElementById('login-error');

        try {
            const resp = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!resp.ok) throw new Error('Auth failed');

            const data = await resp.json();
            this.token = data.access_token;
            this.role = data.role;
            this.userInfo = { username };
            this.compagnieInfo = { nom_compagnie: data.nom_compagnie };

            localStorage.setItem('token', this.token);
            localStorage.setItem('role', this.role);
            localStorage.setItem('userInfo', JSON.stringify(this.userInfo));
            localStorage.setItem('nom_compagnie', JSON.stringify(this.compagnieInfo));

            this.showApp();
        } catch (err) {
            errorEl.style.display = 'block';
        }
    }

    handleLogout() {
        localStorage.clear();
        location.reload();
    }

    switchNav(viewId) {
        // Update Nav visibility
        document.querySelectorAll('.view-section').forEach(s => s.classList.add('hidden'));
        const activeSection = document.getElementById(viewId);
        if (activeSection) {
            activeSection.classList.remove('hidden');

            // Reset all forms within this section
            activeSection.querySelectorAll('form').forEach(form => form.reset());

            // Clear search result if applicable
            const searchResult = activeSection.querySelector('#search-result');
            if (searchResult) searchResult.classList.add('hidden');
        }

        // Update Nav active state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.view === viewId);
        });

        // Special loads
        if (viewId === 'asac-dash') this.loadStats();
        if (viewId === 'asac-companies') this.loadCompanies();
        if (viewId === 'asac-users') {
            this.loadUsers();
            this.loadCompanies(true); // Populate the dropdown
        }
    }

    async handleSearch(e) {
        e.preventDefault();
        const type = document.getElementById('search-doc-type').value;
        const num = document.getElementById('search-doc-num').value;
        const nom = document.getElementById('search-nom').value;
        const prenom = document.getElementById('search-prenom').value;

        let queryParams = "";
        if (num) {
            queryParams = `numero_document=${num}&type_document=${type}`;
        } else if (nom && prenom) {
            queryParams = `nom=${nom}&prenom=${prenom}`;
        }

        try {
            const resp = await fetch(`${API_URL}/assures/score?${queryParams}`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await resp.json();
            this.displayScore(data);
        } catch (err) {
            alert("Erreur lors de la recherche");
        }
    }

    displayScore(data) {
        const resEl = document.getElementById('search-result');
        const scoreEl = document.getElementById('score-display');
        const detailsEl = document.getElementById('score-details');

        resEl.classList.remove('hidden');
        scoreEl.textContent = `${data.score} / 100`;

        // Style based on score
        scoreEl.className = 'score-badge';
        if (data.score <= 20) scoreEl.classList.add('score-low');
        else if (data.score <= 40) scoreEl.classList.add('score-modere');
        else if (data.score <= 60) scoreEl.classList.add('score-eleve');
        else scoreEl.classList.add('score-critique');

        detailsEl.innerHTML = `
            <div><strong>Classe:</strong> ${data.classe_risque}</div>
            <div><strong>Fréquence:</strong> ${data.detail.frequence} pts</div>
            <div><strong>Responsabilité:</strong> ${data.detail.responsabilite} pts</div>
            <div><strong>Gravité:</strong> ${data.detail.gravite} pts</div>
            <div><strong>Corporel:</strong> ${data.detail.corporel} pts</div>
            <div><strong>Récidive:</strong> ${data.detail.recidive} pts</div>
        `;
    }

    async handleDeclare(e) {
        e.preventDefault();

        // 1. Collect Causes
        const causes = [];
        const mainCauseVal = document.querySelector('input[name="main-cause"]:checked')?.value;
        document.querySelectorAll('.dec-cause:checked').forEach(cb => {
            causes.push({
                cause_code: cb.value,
                cause_principale: cb.value === mainCauseVal
            });
        });

        // 2. Build Payload
        const payload = {
            assure: {
                type_assure: document.getElementById('dec-type-assure').value,
                nom: document.getElementById('dec-nom').value,
                prenom: document.getElementById('dec-prenom').value,
                date_naissance: document.getElementById('dec-dob').value || null,
                lieu_naissance: document.getElementById('dec-lieu-naissance').value,
                sexe: document.getElementById('dec-sexe').value,
                type_document: document.getElementById('dec-doc-type').value,
                numero_document: document.getElementById('dec-doc-num').value
            },
            sinistre: {
                date_survenance: document.getElementById('dec-date').value,
                lieu_survenance: document.getElementById('dec-lieu-sinistre').value,
                nature_sinistre: document.getElementById('dec-nature').value,
                branche: document.getElementById('dec-branche').value,
                role_assure: document.getElementById('dec-role').value,
                taux_responsabilite: parseFloat(document.getElementById('dec-taux').value) || 0,
                classe_cout: document.getElementById('dec-cout').value,
                corporel: document.getElementById('dec-corporel').checked,
                deces: document.getElementById('dec-deces').checked,
                vehicule_au_rebut: document.getElementById('dec-rebut').checked
            },
            causes: causes
        };

        try {
            const resp = await fetch(`${API_URL}/sinistres`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(payload)
            });

            if (resp.ok) {
                alert("Sinistre déclaré avec succès !");
                this.switchNav('compagnie-dash');
            } else {
                const err = await resp.json();
                alert("Erreur: " + (err.detail || "Inconnue"));
            }
        } catch (err) {
            alert("Erreur lors de la déclaration: " + err.message);
        }
    }

    async loadStats() {
        try {
            const resp = await fetch(`${API_URL}/admin/stats`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });

            if (!resp.ok) {
                console.error("API Error:", await resp.text());
                return;
            }

            const data = await resp.json();
            document.getElementById('stat-sinistres').textContent = data.total_sinistres || 0;
            document.getElementById('stat-sinistres-annee').textContent = data.sinistres_annee_en_cours || 0;
            document.getElementById('stat-assures').textContent = data.total_assures || 0;
            document.getElementById('stat-compagnies').textContent = data.total_compagnies || 0;

            this.renderCharts(data);
        } catch (err) {
            console.error("Error loading stats:", err);
        }
    }

    renderCharts(data) {
        if (!data || !data.ventilation_nature) return;

        const colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

        // Helper to create/update chart
        const updateChart = (id, type, labels, values, label) => {
            const ctx = document.getElementById(id).getContext('2d');

            // Destroy existing chart if it exists
            if (this.charts && this.charts[id]) {
                this.charts[id].destroy();
            } else if (!this.charts) {
                this.charts = {};
            }

            // Register Datalabels plugin
            Chart.register(ChartDataLabels);

            this.charts[id] = new Chart(ctx, {
                type: type,
                data: {
                    labels: labels,
                    datasets: [{
                        label: label,
                        data: values,
                        backgroundColor: type === 'pie' ? colors : colors[0],
                        borderColor: colors[0],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' },
                        datalabels: {
                            color: '#fff',
                            font: { weight: 'bold' },
                            formatter: (value) => value > 0 ? value : '', // Only show if > 0
                            display: type === 'pie' // Only show on pie charts
                        }
                    },
                    scales: type === 'bar' || type === 'line' ? {
                        y: { beginAtZero: true, ticks: { stepSize: 1 } }
                    } : {}
                }
            });
        };

        // 1. Nature (Pie)
        const natureLabels = Object.keys(data.ventilation_nature);
        const natureValues = Object.values(data.ventilation_nature);
        updateChart('chart-nature', 'pie', natureLabels, natureValues, 'Sinistres par Nature');

        // 2. Cause (Pie)
        const causeLabels = Object.keys(data.ventilation_cause);
        const causeValues = Object.values(data.ventilation_cause);
        updateChart('chart-cause', 'pie', causeLabels, causeValues, 'Sinistres par Cause');

        // 3. Coût (Bar)
        const coutLabels = Object.keys(data.ventilation_cout);
        const coutValues = Object.values(data.ventilation_cout);
        updateChart('chart-cout', 'bar', coutLabels, coutValues, 'Sinistres par Classe de Coût');

        // 4. Trend (Line)
        const trendLabels = Object.keys(data.trend_3_ans);
        const trendValues = Object.values(data.trend_3_ans);
        updateChart('chart-trend', 'line', trendLabels, trendValues, 'Évolution sur 3 ans');
    }

    async loadCompanies(forDropdown = false) {
        const tableBody = document.getElementById('companies-table-body');
        const dropdown = document.getElementById('usr-compagnie');
        try {
            const resp = await fetch(`${API_URL}/admin/compagnies`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await resp.json();

            if (forDropdown && dropdown) {
                dropdown.innerHTML = data.map(c => `<option value="${c.compagnie_id}">${c.nom_compagnie}</option>`).join('');
            } else if (tableBody) {
                tableBody.innerHTML = data.map(c => `
                    <tr style="border-bottom: 1px solid var(--border-color);">
                        <td style="padding: 0.75rem;">${c.code_compagnie}</td>
                        <td style="padding: 0.75rem;">${c.nom_compagnie}</td>
                        <td style="padding: 0.75rem;"><span class="score-low" style="padding: 0.2rem 0.5rem; border-radius: 1rem; font-size: 0.75rem;">ACTIF</span></td>
                    </tr>
                `).join('');
            }
        } catch (err) { }
    }

    async loadUsers() {
        const tableBody = document.getElementById('users-table-body');
        try {
            const resp = await fetch(`${API_URL}/admin/utilisateurs`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await resp.json();
            tableBody.innerHTML = data.map(u => `
                <tr style="border-bottom: 1px solid var(--border-color);">
                    <td style="padding: 0.75rem;">${u.code_utilisateur}</td>
                    <td style="padding: 0.75rem;">${u.nom_utilisateur}</td>
                    <td style="padding: 0.75rem;">${u.compagnie_id}</td>
                    <td style="padding: 0.75rem;">${u.role_utilisateur}</td>
                    <td style="padding: 0.75rem;"><span class="score-low" style="padding: 0.2rem 0.5rem; border-radius: 1rem; font-size: 0.75rem;">${u.statut_utilisateur}</span></td>
                </tr>
            `).join('');
        } catch (err) { }
    }

    async handleCreateUser(e) {
        e.preventDefault();
        const payload = {
            code_utilisateur: document.getElementById('usr-code').value,
            nom_utilisateur: document.getElementById('usr-nom').value,
            mot_de_passe: document.getElementById('usr-password').value,
            compagnie_id: parseInt(document.getElementById('usr-compagnie').value),
            tel_utilisateur: document.getElementById('usr-tel').value,
            email_utilisateur: document.getElementById('usr-email').value,
            role_utilisateur: document.getElementById('usr-role').value,
            statut_utilisateur: document.getElementById('usr-statut').value
        };

        try {
            const resp = await fetch(`${API_URL}/admin/utilisateurs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(payload)
            });

            if (resp.ok) {
                alert("Utilisateur créé avec succès !");
                this.loadUsers();
                e.target.reset();
            } else {
                const err = await resp.json();
                alert("Erreur: " + (err.detail || "Inconnue"));
            }
        } catch (err) {
            alert("Erreur lors de la création: " + err.message);
        }
    }
}

const app = new CentraleRisquesApp();
window.app = app; // For inline onclick access
