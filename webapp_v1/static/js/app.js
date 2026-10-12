(function(){
  const API = '/api/v1';
  const protectedRoutes = ['/dashboard','/audio','/video','/history','/results','/analytics','/insights','/reports','/profile','/settings','/help'];
  let historyPage = 1;
  let historyPages = 1;

  const suggestionMap = {
    angry: ['Take a short breathing break.','Pause before reacting.','Go for a short walk.'],
    disgust: ['Step away from trigger.','Reset with fresh air.','Re-center with slow breathing.'],
    fear: ['Ground with 5-4-3-2-1 technique.','Focus on one small action.','Talk to someone you trust.'],
    happy: ['Capture this positive moment.','Share gratitude with someone.','Use the energy for a meaningful task.'],
    neutral: ['Plan your next focused task.','Hydrate and stretch briefly.','Reflect on today\'s priorities.'],
    sad: ['Reach out to support.','Try gentle movement.','Write a short reflection.'],
    calm: ['Continue mindful breathing.','Use this state for deep work.','Keep a gratitude note.'],
    surprise: ['Pause and reassess context.','Write what changed.','Choose your next small step.']
  };

  function emojiFor(modality, emotion){
    const m = {
      audio: {angry:'😠',disgust:'🤢',fear:'😨',happy:'😊',neutral:'😐',sad:'😢'},
      video: {neutral:'😐',calm:'😌',happy:'😊',sad:'😢',angry:'😠',fear:'😨',disgust:'🤢',surprise:'😲'}
    };
    return (m[modality] || m.audio)[emotion] || '🤔';
  }

  async function req(path, opts={}){
    const res = await fetch(API + path, Object.assign({headers:{'Content-Type':'application/json'}}, opts));
    const isJson = (res.headers.get('content-type') || '').includes('application/json');
    const data = isJson ? await res.json() : await res.text();
    if(!res.ok){
      throw new Error((data && data.error) || 'Request failed');
    }
    return data;
  }

  async function updateAuthUI(){
    const authOnly = document.getElementById('authOnlyNav');
    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');
    const logoutBtn = document.getElementById('logoutBtn');
    const authSummary = document.getElementById('authSummary');

    try{
      const data = await req('/auth/me', {headers:{}});
      const user = data.user;
      if(authOnly) authOnly.style.display = 'block';
      if(logoutBtn) logoutBtn.style.display = 'inline-flex';
      if(loginLink) loginLink.style.display = 'none';
      if(registerLink) registerLink.style.display = 'none';
      if(authSummary) authSummary.textContent = `${user.fullName} · ${user.email}`;
      return user;
    }catch{
      if(authOnly) authOnly.style.display = 'none';
      if(logoutBtn) logoutBtn.style.display = 'none';
      if(loginLink) loginLink.style.display = 'inline-flex';
      if(registerLink) registerLink.style.display = 'inline-flex';
      if(authSummary) authSummary.textContent = 'Not signed in';
      if(protectedRoutes.includes(location.pathname)) location.href = '/login';
      return null;
    }
  }

  async function logout(){
    try{ await req('/auth/logout', {method:'POST'}); } catch {}
    location.href = '/login';
  }

  async function saveAnalysis(payload){
    try{
      await req('/analysis/save', {method:'POST', body: JSON.stringify(payload)});
      alert('Analysis saved');
    }catch(e){ alert(e.message); }
  }

  async function loadHistory(page){
    historyPage = page || historyPage;
    const search = document.getElementById('historySearch')?.value || '';
    const modality = document.getElementById('historyModality')?.value || '';
    const params = new URLSearchParams({page:String(historyPage), perPage:'10'});
    if(search) params.set('search', search);
    if(modality) params.set('modality', modality);
    try{
      const data = await req('/history?' + params.toString(), {headers:{}});
      historyPages = data.pagination.pages || 1;
      const target = document.getElementById('historyList');
      if(!target) return;
      if(!data.items.length){ target.innerHTML = '<p>No analyses found.</p>'; return; }
      target.innerHTML = data.items.map(item => `
        <div class="tip" style="justify-content:space-between;">
          <div>
            <strong>${item.modality.toUpperCase()}</strong> · ${item.predictedEmotion} · ${Number(item.confidenceScore).toFixed(2)}%
            <div style="font-size:12px;color:var(--txt2);">${new Date(item.createdAt).toLocaleString()}</div>
          </div>
          <div class="bgrp">
            <button class="btn" onclick="window.AIME.openAnalysis(${item.id})">View</button>
            <button class="btn btn-r" onclick="window.AIME.deleteAnalysis(${item.id})">Delete</button>
          </div>
        </div>`).join('');
    }catch(e){ alert(e.message); }
  }

  function prevHistory(){ if(historyPage > 1) loadHistory(historyPage - 1); }
  function nextHistory(){ if(historyPage < historyPages) loadHistory(historyPage + 1); }

  async function openAnalysis(id){
    try{ const data = await req('/analysis/' + id, {headers:{}}); alert(JSON.stringify(data.analysis, null, 2)); }
    catch(e){ alert(e.message); }
  }

  async function deleteAnalysis(id){
    if(!confirm('Delete this analysis?')) return;
    try{ await req('/analysis/' + id, {method:'DELETE'}); loadHistory(historyPage); }
    catch(e){ alert(e.message); }
  }

  function exportHistory(format){
    window.open(`${API}/history/export?format=${encodeURIComponent(format)}`, '_blank');
  }

  async function loadAnalytics(){
    try{
      const data = await req('/analytics/summary', {headers:{}});
      const text = JSON.stringify(data.summary, null, 2);
      const a = document.getElementById('analyticsSummary');
      const r = document.getElementById('reportSummary');
      if(a) a.textContent = text;
      if(r) r.textContent = text;
    }catch(e){
      const a = document.getElementById('analyticsSummary');
      const r = document.getElementById('reportSummary');
      if(a) a.textContent = e.message;
      if(r) r.textContent = e.message;
    }
  }

  function suggestions(emotion){ return suggestionMap[emotion] || suggestionMap.neutral; }

  document.addEventListener('DOMContentLoaded', async () => {
    const user = await updateAuthUI();

    const loginForm = document.getElementById('loginForm');
    if(loginForm){
      loginForm.addEventListener('submit', async (e)=>{
        e.preventDefault();
        const body = JSON.stringify(Object.fromEntries(new FormData(loginForm).entries()));
        try{ await req('/auth/login', {method:'POST', body}); location.href='/dashboard'; }
        catch(err){ alert(err.message); }
      });
    }

    const registerForm = document.getElementById('registerForm');
    if(registerForm){
      registerForm.addEventListener('submit', async (e)=>{
        e.preventDefault();
        const body = JSON.stringify(Object.fromEntries(new FormData(registerForm).entries()));
        try{ await req('/auth/register', {method:'POST', body}); location.href='/dashboard'; }
        catch(err){ alert(err.message); }
      });
    }

    const forgotForm = document.getElementById('forgotForm');
    if(forgotForm){
      forgotForm.addEventListener('submit', async (e)=>{
        e.preventDefault();
        const body = JSON.stringify(Object.fromEntries(new FormData(forgotForm).entries()));
        try{ await req('/auth/password/forgot', {method:'POST', body}); alert('If email exists, reset token was created.'); }
        catch(err){ alert(err.message); }
      });
    }

    const resetForm = document.getElementById('resetForm');
    if(resetForm){
      resetForm.addEventListener('submit', async (e)=>{
        e.preventDefault();
        const body = JSON.stringify(Object.fromEntries(new FormData(resetForm).entries()));
        try{ await req('/auth/password/reset', {method:'POST', body}); location.href='/login'; }
        catch(err){ alert(err.message); }
      });
    }

    const profileForm = document.getElementById('profileForm');
    if(profileForm){
      if(user){
        document.getElementById('profileName').value = user.fullName;
        document.getElementById('profileEmail').value = user.email;
      }
      profileForm.addEventListener('submit', async (e)=>{
        e.preventDefault();
        const body = JSON.stringify(Object.fromEntries(new FormData(profileForm).entries()));
        try{ await req('/users/profile', {method:'PATCH', body}); alert('Profile saved.'); }
        catch(err){ alert(err.message); }
      });
    }

    const pwdForm = document.getElementById('changePasswordForm');
    if(pwdForm){
      pwdForm.addEventListener('submit', async (e)=>{
        e.preventDefault();
        const body = JSON.stringify(Object.fromEntries(new FormData(pwdForm).entries()));
        try{ await req('/auth/password/change', {method:'POST', body}); alert('Password updated'); pwdForm.reset(); }
        catch(err){ alert(err.message); }
      });
    }

    const settingsForm = document.getElementById('settingsForm');
    if(settingsForm){
      try{
        const {preferences} = await req('/users/preferences', {headers:{}});
        settingsForm.theme.value = preferences.theme;
        settingsForm.privacyLevel.value = preferences.privacyLevel;
        settingsForm.retentionDays.value = preferences.retentionDays;
        settingsForm.notificationsEnabled.checked = preferences.notificationsEnabled;
        settingsForm.autoSaveAnalysis.checked = preferences.autoSaveAnalysis;
      }catch{}
      settingsForm.addEventListener('submit', async (e)=>{
        e.preventDefault();
        const fd = new FormData(settingsForm);
        const payload = {
          theme: fd.get('theme'),
          privacyLevel: fd.get('privacyLevel'),
          retentionDays: Number(fd.get('retentionDays')),
          notificationsEnabled: settingsForm.notificationsEnabled.checked,
          autoSaveAnalysis: settingsForm.autoSaveAnalysis.checked,
        };
        try{ await req('/users/preferences', {method:'PATCH', body: JSON.stringify(payload)}); alert('Settings saved'); }
        catch(err){ alert(err.message); }
      });
    }

    if(location.pathname === '/history') loadHistory(1);
  });

  async function deleteAccount(){
    if(!confirm('Delete your account permanently?')) return;
    try{ await req('/auth/account', {method:'DELETE'}); location.href='/'; }
    catch(e){ alert(e.message); }
  }

  window.AIME = {logout,saveAnalysis,loadHistory,prevHistory,nextHistory,openAnalysis,deleteAnalysis,exportHistory,loadAnalytics,suggestions,emojiFor,deleteAccount};
})();
