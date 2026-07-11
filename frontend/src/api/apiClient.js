// Client API réel — remplace le SDK propriétaire Base44.
// Connecte le frontend au backend Django REST (voir agrivigil_backend/).
//
// Toutes les pages du frontend continuent d'utiliser la même variable `db`
// qu'avant (auth / entities / integrations), pour ne pas avoir à réécrire
// chaque écran : seule l'implémentation change, l'interface reste stable.

const configuredBase = (import.meta.env.VITE_API_BASE_URL || 'https://agrivigil-ai-production.up.railway.app').trim().replace(/\/$/, '');
const API_BASE_URL = configuredBase.endsWith('/api') ? configuredBase : `${configuredBase}/api`;

const ACCESS_KEY = 'agrivigil_access_token';
const REFRESH_KEY = 'agrivigil_refresh_token';

function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY);
}
function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY);
}
function setTokens({ access_token, refresh_token }) {
  if (access_token) localStorage.setItem(ACCESS_KEY, access_token);
  if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
}
function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

async function refreshAccessToken() {
  const refresh = getRefreshToken();
  if (!refresh) {
    clearTokens();
    throw new Error('Session expirée');
  }
  const res = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) {
    clearTokens();
    throw new Error('Session expirée');
  }
  const data = await res.json();
  setTokens({ access_token: data.access });
  return data.access;
}

// `body` peut être un objet JSON classique OU une instance de FormData
// (utilisée automatiquement dès qu'un fichier est présent, ex: images).
async function request(path, { method = 'GET', body, isForm = false, retry = true } = {}) {
  const headers = {};
  const token = getAccessToken();
  const isPublicAuthPath =
    path === '/auth/login/' ||
    path === '/auth/register/' ||
    path === '/auth/verify-otp/' ||
    path === '/auth/resend-otp/' ||
    path === '/auth/forgot-password/' ||
    path === '/auth/reset-password/';

  if (token && !isPublicAuthPath) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (!isForm) headers['Content-Type'] = 'application/json';

  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && retry && getRefreshToken() && path !== '/auth/login/' && path !== '/auth/register/' && path !== '/auth/verify-otp/') {
    await refreshAccessToken();
    return request(path, { method, body, isForm, retry: false });
  }

  const isJson = res.headers.get('content-type')?.includes('application/json');
  const data = isJson ? await res.json().catch(() => ({})) : null;

  if (!res.ok) {
    const message = getApiErrorMessage(res, data);
    const error = new Error(message);
    error.status = res.status;
    error.data = data;
    throw error;
  }
  return data;
}

function getApiErrorMessage(res, data) {
  if (res.status === 429) {
    return 'Quota IA dépassé. Réessaie dans quelques instants ou vérifie ta configuration API.';
  }

  const fallbackMessage = 'Une erreur est survenue';

  if (data?.detail) return data.detail;
  if (data?.message) return data.message;
  if (data?.error?.message) return data.error.message;

  if (Array.isArray(data) && data.length > 0) {
    const first = data[0];
    return typeof first === 'string' ? first : JSON.stringify(first);
  }

  if (typeof data === 'object' && data !== null) {
    const values = Object.values(data);
    const firstString = values.find((value) => typeof value === 'string');
    if (firstString) return firstString;
    if (values.length > 0) return JSON.stringify(values[0]);
  }

  return fallbackMessage;
}

function toFormData(fields) {
  const form = new FormData();
  Object.entries(fields).forEach(([key, value]) => {
    if (value === undefined || value === null) return;
    form.append(key, value);
  });
  return form;
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

const auth = {
  async isAuthenticated() {
    return !!getAccessToken();
  },

  async me() {
    return request('/auth/me/');
  },

  async loginViaEmailPassword(email, password) {
    const data = await request('/auth/login/', { method: 'POST', body: { email, password } });
    setTokens(data);
    return data.user;
  },

  loginWithProvider() {
    // La connexion Google nécessite une configuration OAuth côté backend,
    // non incluse dans ce MVP. On informe l'utilisateur clairement au lieu
    // de planter silencieusement.
    window.alert("La connexion via Google n'est pas encore disponible sur cette version. Utilisez votre email et mot de passe.");
  },

  async register({ email, password, full_name }) {
    const body = { email, password, full_name };
    // En développement, demander au backend de renvoyer le code OTP pour démo
    if (import.meta.env.DEV || import.meta.env.VITE_DEBUG_OTP === 'true') {
      body.debug = true;
    }
    return request('/auth/register/', { method: 'POST', body });
  },

  async verifyOtp({ email, otpCode }) {
    const data = await request('/auth/verify-otp/', { method: 'POST', body: { email, otp_code: otpCode } });
    setTokens(data);
    return data;
  },

  async resendOtp(email) {
    return request('/auth/resend-otp/', { method: 'POST', body: { email } });
  },

  setToken(access_token) {
    setTokens({ access_token });
  },

  async resetPasswordRequest(email) {
    return request('/auth/forgot-password/', { method: 'POST', body: { email } });
  },

  async resetPassword({ resetToken, newPassword, email }) {
    return request('/auth/reset-password/', {
      method: 'POST',
      body: { email, reset_token: resetToken, new_password: newPassword },
    });
  },

  logout(redirectUrl) {
    clearTokens();
    if (redirectUrl) window.location.href = '/login';
  },

  redirectToLogin() {
    window.location.href = '/login';
  },
};

// ---------------------------------------------------------------------------
// Entities
// ---------------------------------------------------------------------------

function makeListCreateEntity(basePath) {
  return {
    async list() {
      const data = await request(`${basePath}/`);
      return Array.isArray(data) ? data : data.results || [];
    },
    async get(id) {
      return request(`${basePath}/${id}/`);
    },
    async filter(query = {}, _sort, _limit) {
      const params = new URLSearchParams(query).toString();
      const data = await request(`${basePath}/${params ? `?${params}` : ''}`);
      return Array.isArray(data) ? data : data.results || [];
    },
    async create(fields) {
      const hasFile = Object.values(fields).some((v) => v instanceof File || v instanceof Blob);
      if (hasFile) {
        return request(`${basePath}/`, { method: 'POST', body: toFormData(fields), isForm: true });
      }
      return request(`${basePath}/`, { method: 'POST', body: fields });
    },
    // Le MVP communique en REST pur (pas de WebSocket). `subscribe` fait un
    // polling léger pour simuler le temps réel sans complexifier le backend.
    subscribe(callback, intervalMs = 6000, query = {}) {
      let seenIds = new Set();
      let stopped = false;
      const hasQuery = Object.keys(query).length > 0;
      const fetchItems = () => (hasQuery ? this.filter(query) : this.list());

      const poll = async () => {
        if (stopped) return;
        try {
          const items = await fetchItems();
          items.forEach((item) => {
            if (!seenIds.has(item.id)) {
              seenIds.add(item.id);
              callback({ type: 'create', data: item });
            }
          });
          if (seenIds.size === 0) {
            seenIds = new Set(items.map((i) => i.id));
          }
        } catch (e) {
          // silencieux : le polling réessaiera au prochain intervalle
        }
      };

      fetchItems().then((items) => { seenIds = new Set(items.map((i) => i.id)); });
      const timer = setInterval(poll, intervalMs);
      return () => { stopped = true; clearInterval(timer); };
    },
    async delete(id) {
      return request(`${basePath}/${id}/`, { method: 'DELETE' });
    },
  };
}

const entities = {
  CropScan: makeListCreateEntity('/scans'),
  CropScanTracking: makeListCreateEntity('/trackings'),
  HealthAlert: makeListCreateEntity('/alerts'),
  FertilizerCalculation: makeListCreateEntity('/calculator'),
  Expert: makeListCreateEntity('/experts'),
  ExpertMessage: makeListCreateEntity('/experts/messages'),
};

// ---------------------------------------------------------------------------
// Integrations — upload + diagnostic IA
// ---------------------------------------------------------------------------

const integrations = {
  Core: {
    // Conserve un fichier en mémoire le temps de l'analyse (pas d'upload
    // générique séparé côté backend : l'image est envoyée directement au
    // moment du diagnostic, voir AnalyzeCropImage ci-dessous).
    async UploadFile({ file }) {
      return { file_url: URL.createObjectURL(file), _file: file };
    },

    // Analyse réelle d'une image de culture (voir ScanIA.jsx).
    // Remplace l'ancien flux Base44 (UploadFile + InvokeLLM générique) par
    // un appel unique et explicite à l'endpoint /scans/analyze/.
    async AnalyzeCropImage(file, { location_lat, location_lng, crop_name, subject_type, tracking_id, new_tracking_name } = {}) {
      const form = toFormData({ image: file, location_lat, location_lng, crop_name, subject_type, tracking_id, new_tracking_name });
      return request('/scans/analyze/', { method: 'POST', body: form, isForm: true });
    },

    async AnalyzeSoilImage(file) {
      const form = toFormData({ image: file });
      return request('/calculator/analyze-soil/', { method: 'POST', body: form, isForm: true });
    },

    async GetCropAdvice(cropType) {
      return request(`/advice/?crop_type=${encodeURIComponent(cropType)}`);
    },

    async GetWeather(city) {
      return request(`/weather/?city=${encodeURIComponent(city)}`);
    },

    async ListCities() {
      return request('/weather/cities/');
    },
  },
};

export const db = { auth, entities, integrations };
export const base44 = db;
export default db;
