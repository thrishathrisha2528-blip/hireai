(function () {
  const API_BASE = 'http://127.0.0.1:5000';

  // No token = not really logged in, send to login page
  if (!localStorage.getItem('hireai_token')) {
    localStorage.removeItem('hireai_logged_in');
    window.location.href = 'login.html';
    return;
  }

  // Automatically attach the login token to every backend request
  const originalFetch = window.fetch;
  window.fetch = async function (input, init = {}) {
    const url = typeof input === 'string' ? input : input.url;
    const isApiCall = url.startsWith(API_BASE);
    const isAuthCall = url.includes('/api/login') || url.includes('/api/register');

    if (isApiCall && !isAuthCall) {
      init.headers = {
        ...(init.headers || {}),
        'Authorization': 'Bearer ' + localStorage.getItem('hireai_token')
      };
    }

    const res = await originalFetch(input, init);

    // Token expired or invalid -> back to login
    if (isApiCall && !isAuthCall && res.status === 401) {
      localStorage.removeItem('hireai_token');
      localStorage.removeItem('hireai_logged_in');
      window.location.href = 'login.html';
    }
    return res;
  };
})();