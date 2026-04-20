// --- EFEITOS GERAIS E ANIMAÇÕES ---
document.addEventListener('mousemove', e => { 
    const g = document.getElementById('cursorGlow'); 
    g.style.left = e.clientX + 'px'; 
    g.style.top = e.clientY + 'px'; 
});

const observer = new IntersectionObserver(e => e.forEach(en => { if(en.isIntersecting) en.target.classList.add('visible'); }), { threshold: 0.1 });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

setInterval(() => { document.getElementById('fpsBefore').innerText = [78, 85, 92, 60, 88, 105][Math.floor(Math.random()*6)]; }, 700);
setInterval(() => { document.getElementById('fpsAfter').innerText = 480 + Math.floor(Math.random()*15); }, 800);

// --- WHATSAPP WIDGET FLUTUANTE ---
function toggleWa() {
    const box = document.getElementById('waBox');
    const icon = document.getElementById('waIcon');
    if (box.classList.contains('show')) {
        box.classList.remove('show');
        setTimeout(() => box.style.display = 'none', 300);
        icon.className = 'fa-solid fa-chevron-up';
    } else {
        box.style.display = 'block';
        setTimeout(() => box.classList.add('show'), 10);
        icon.className = 'fa-solid fa-chevron-down';
    }
}
window.onload = () => { 
    document.getElementById('waBox').style.display = 'block'; 
    setTimeout(() => document.getElementById('waBox').classList.add('show'), 100); 
};

// --- SISTEMA DE AUTENTICAÇÃO ---
let isLoginMode = true; 
let loggedUserID = null; 
let loggedUserEmail = ""; 
let pollingInterval = null;
const API_BASE_URL = "https://bs-optimizer-api.onrender.com"; // Mude para a URL do Render após o deploy

function openAuthModal(mode) {
    isLoginMode = (mode === 'login');
    document.getElementById('authTitle').innerText = isLoginMode ? "Acessar Painel" : "Criar Nova Conta";
    document.getElementById('authSub').innerText = isLoginMode ? "Entre para gerenciar sua assinatura." : "Junte-se à elite e garanta a sua Key.";
    document.getElementById('btnAuth').innerText = isLoginMode ? "ENTRAR" : "CRIAR CONTA";
    document.getElementById('switchText').innerHTML = isLoginMode ? 'Não tem conta? <a href="#" onclick="toggleAuthMode()">Crie uma gratuitamente</a>' : 'Já tem conta? <a href="#" onclick="toggleAuthMode()">Faça Login</a>';
    document.getElementById('emailWrap').style.display = isLoginMode ? 'none' : 'block';
    document.getElementById('authEmail').required = !isLoginMode;
    document.getElementById('authOverlay').style.display = 'flex';
}

function toggleAuthMode() { openAuthModal(isLoginMode ? 'registro' : 'login'); }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }

async function handleAuth(e) {
    e.preventDefault();
    const u = document.getElementById('authUser').value, p = document.getElementById('authPass').value, em = document.getElementById('authEmail').value;
    const btn = document.getElementById('btnAuth');
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processando...'; btn.disabled = true;

    try {
        const res = await fetch(`${API_BASE_URL}/api/auth`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: u, password: p, email: em, mode: isLoginMode ? 'login' : 'registro' })
        });
        const data = await res.json();

        if(data.sucesso) {
            if(isLoginMode) {
                loggedUserID = data.user_id;
                loggedUserEmail = data.email;
                document.getElementById('guestNav').style.display = 'none';
                document.getElementById('userNav').style.display = 'flex';
                document.getElementById('navUsername').innerText = data.username;
                document.getElementById('userAvatar').src = `https://ui-avatars.com/api/?name=${data.username}&background=8b5cf6&color=fff`;
                closeModal('authOverlay');
                showToast("success", `Login efetuado! Bem-vindo, ${data.username}.`);
                document.getElementById('authUser').value = ""; document.getElementById('authPass').value = "";
            } else {
                loggedUserEmail = em; // Salva o email para a hora da compra
                showToast("success", "Conta criada! Faça Login.");
                openAuthModal('login');
            }
        } else { showToast("error", data.mensagem); }
    } catch(err) { showToast("error", "Servidor Backend offline."); }
    btn.innerText = isLoginMode ? "ENTRAR" : "CRIAR CONTA"; btn.disabled = false;
}

function logout() { 
    loggedUserID = null; 
    loggedUserEmail = ""; 
    document.getElementById('guestNav').style.display = 'flex'; 
    document.getElementById('userNav').style.display = 'none'; 
    showToast("info", "Você saiu da conta."); 
}

// --- DASHBOARD DO PERFIL ---
async function openProfileModal() {
    document.getElementById('profileOverlay').style.display = 'flex';
    document.getElementById('profileBox').classList.add('loading');
    
    try {
        const res = await fetch(`${API_BASE_URL}/api/perfil`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: loggedUserID }) });
        const data = await res.json();
        if(data.sucesso) {
            const p = data.perfil;
            document.getElementById('profName').innerText = `Painel VIP: ${p.username}`;
            document.getElementById('profStatus').innerText = p.status_plano;
            document.getElementById('profDias').innerText = p.dias_restantes;
            
            let tbl = "";
            if(p.historico.length === 0) tbl = "<tr><td colspan='3' style='text-align:center;'>Nenhuma compra realizada ainda.</td></tr>";
            p.historico.forEach(h => {
                let color = h.status === 'Ativa' ? 'var(--accent)' : 'var(--muted)';
                tbl += `<tr><td>${h.plano}</td><td><div class="key-tag"><span>${h.chave}</span><button class="btn-copy" onclick="copiarKey('${h.chave}')"><i class="fa-solid fa-copy"></i></button></div></td><td style="color:${color}; font-weight:bold;">${h.status}</td></tr>`;
            });
            document.getElementById('historyBody').innerHTML = tbl;
        }
    } catch(e) { }
    document.getElementById('profileBox').classList.remove('loading');
}

function copiarKey(chave) { navigator.clipboard.writeText(chave); showToast("success", "Chave copiada!"); }

// --- MERCADO PAGO E PIX ---
async function buyPlan(plano) {
    if(!loggedUserID) { 
        showToast("info", "Faça login para assinar um plano!"); 
        return openAuthModal('login'); // Abre o Modal de Login corretamente 
    }
    
    showToast("info", "Gerando cobrança PIX...");
    
    try {
        const res = await fetch(`${API_BASE_URL}/api/comprar`, { 
            method: 'POST', headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify({ user_id: loggedUserID, plano: plano, email: loggedUserEmail }) 
        });
        const data = await res.json();
        
        if(data.sucesso) {
            document.getElementById('pixQrImage').src = "data:image/jpeg;base64," + data.qr_code_base64;
            document.getElementById('pixCodeText').innerText = data.qr_code;
            document.getElementById('pixOverlay').style.display = 'flex';
            pollingInterval = setInterval(() => checkPaymentStatus(data.payment_id), 5000);
        } else { showToast("error", data.mensagem); }
    } catch(e) { showToast("error", "Falha de conexão com a API de Vendas."); }
}

async function checkPaymentStatus(paymentId) {
    try {
        const res = await fetch(`${API_BASE_URL}/api/check_payment/${paymentId}`);
        const data = await res.json();
        if(data.status === "approved") {
            clearInterval(pollingInterval); fecharPix();
            alert(`🎉 PAGAMENTO APROVADO!\n\nSua Key VIP de 16 Dígitos:\n${data.key}\n\nA chave foi salva no seu Perfil e enviada para seu e-mail.`);
        }
    } catch(e) {}
}

function fecharPix() { if(pollingInterval) clearInterval(pollingInterval); closeModal('pixOverlay'); }
function copiarPix() { navigator.clipboard.writeText(document.getElementById('pixCodeText').innerText); showToast("success", "Código PIX Copiado!"); }

// --- TOAST UI ---
let toastTimer;
function showToast(type, msg) {
    const toast = document.getElementById('toast');
    const icon = type === 'success' ? 'fa-circle-check' : (type === 'error' ? 'fa-circle-xmark' : 'fa-bolt');
    toast.className = `toast show ${type}`;
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${msg}</span>`;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 3500);
}