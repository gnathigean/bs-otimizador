// --- MENU MOBILE RESPONSIVO ---
function toggleMenu() {
    const nav = document.getElementById('navMenu');
    nav.classList.toggle('active');
}

// --- ROLAGEM SUAVE ---
function scrollToPricing() { document.getElementById('pricing').scrollIntoView({ behavior: 'smooth' }); }

// --- WIDGET WHATSAPP (Abre/Fecha suavemente) ---
function toggleWa() {
    const popup = document.getElementById('waPopup');
    const icon = document.querySelector('#waBtn i');
    
    if (popup.classList.contains('show')) {
        popup.classList.remove('show');
        setTimeout(() => popup.style.display = 'none', 300); // Aguarda animação
        icon.className = 'fa-brands fa-whatsapp';
    } else {
        popup.style.display = 'block';
        setTimeout(() => popup.classList.add('show'), 10);
        icon.className = 'fa-solid fa-xmark';
    }
}

// --- MODAL AUTH (Login/Registro) ---
const modal = document.getElementById('authModal');
let isLogin = true;
let usuarioLogadoID = null;

function openAuthModal(mode) { setAuthMode(mode); modal.style.display = 'flex'; }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }
window.onclick = function(event) { if (event.target == modal) closeModal('authModal'); }

function setAuthMode(mode) {
    isLogin = (mode === 'login');
    document.getElementById('modalTitle').innerText = isLogin ? "Acessar Painel" : "Criar Nova Conta";
    document.getElementById('modalSubtitle').innerText = isLogin ? "Entre para gerenciar sua assinatura." : "Junte-se à elite e maximize seus FPS agora.";
    document.getElementById('btnSubmit').innerText = isLogin ? "ENTRAR" : "CRIAR CONTA";
    document.getElementById('switchText').innerHTML = isLogin ? 
        'Não tem conta? <a href="#" onclick="setAuthMode(\'registro\')">Crie uma agora</a>' : 
        'Já tem conta? <a href="#" onclick="setAuthMode(\'login\')">Faça Login</a>';
}

async function handleAuth(event) {
    event.preventDefault();
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    const btnSubmit = document.getElementById('btnSubmit');
    
    const originalText = btnSubmit.innerText;
    btnSubmit.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processando...';
    btnSubmit.disabled = true;

    try {
        const response = await fetch('http://127.0.0.1:5000/api/auth', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass, mode: isLogin ? 'login' : 'registro' })
        });
        
        const data = await response.json();

        if (data.sucesso) {
            if (isLogin) {
                usuarioLogadoID = data.user_id;
                closeModal('authModal');
                showToast("Login efetuado! Selecione seu plano.");
            } else {
                showToast("Conta criada! Por favor, faça login.");
                setAuthMode('login');
            }
        } else {
            showToast(data.mensagem);
        }
    } catch (error) {
        showToast("Erro de conexão com o servidor.");
    } finally {
        btnSubmit.innerHTML = originalText;
        btnSubmit.disabled = false;
    }
}

// --- SISTEMA DE COMPRA ---
async function buyPlan(plano) {
    if (!usuarioLogadoID) {
        showToast("Por favor, faça login para assinar o plano.");
        openAuthModal('login');
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/api/comprar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: usuarioLogadoID, plano: plano })
        });
        
        const data = await response.json();
        if (data.sucesso) {
            const keyGerada = data.mensagem.split(': ')[1];
            alert(`🎉 COMPRA APROVADA!\n\nSua Key VIP é:\n${keyGerada}`);
        } else {
            showToast("Falha: " + data.mensagem);
        }
    } catch (error) {
        showToast("Erro no servidor.");
    }
}

function showToast(message) {
    const toast = document.getElementById("toast");
    document.getElementById("toastMsg").innerText = message;
    toast.className = "toast show";
    setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 3500);
}