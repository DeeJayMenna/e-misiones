// ==========================================
// VARIABLES GLOBALES
// ==========================================
let fechaActualVisualizacion = new Date(); 
let mesCalendario = new Date().getMonth();
let anioCalendario = new Date().getFullYear();

// ==========================================
// INICIO
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    actualizarHeaderFecha(new Date());
    // Por defecto mostramos Efemérides (sin noticias RSS)
    procesarDatosPorFecha(new Date()); 
    renderizarCalendario(mesCalendario, anioCalendario);
    configurarBuscador();
    configurarMenu();
});

// ==========================================
// MENÚ DE NAVEGACIÓN
// ==========================================
function configurarMenu() {
    // 1. INICIO
    document.getElementById('nav-inicio').addEventListener('click', (e) => {
        e.preventDefault();
        window.location.reload();
    });

    // 2. EFEMÉRIDES (FILTRO ESTRICTO: NO NOTICIAS)
    document.getElementById('nav-efemerides').addEventListener('click', (e) => {
        e.preventDefault();
        fechaActualVisualizacion = new Date(); 
        actualizarHeaderFecha(fechaActualVisualizacion);
        procesarDatosPorFecha(fechaActualVisualizacion);
        renderizarCalendario(mesCalendario, anioCalendario);
        // Reseteamos el título
        document.getElementById('display-date').textContent = obtenerFechaTexto(new Date());
    });

    // 3. NOTICIAS (FILTRO ESTRICTO: SOLO NOTICIAS)
    document.getElementById('nav-noticias').addEventListener('click', (e) => {
        e.preventDefault();
        filtrarSoloNoticias();
    });

    // 4. CONTACTO
    document.getElementById('nav-contacto').addEventListener('click', (e) => {
        e.preventDefault();
        alert('Sección de Contacto disponible próximamente.');
    });
}

// ==========================================
// LÓGICA DE FILTRADO
// ==========================================

// CASO A: MOSTRAR EFEMÉRIDES (Excluye Noticias RSS)
function procesarDatosPorFecha(fecha) {
    const dia = fecha.getDate();
    const mes = fecha.getMonth() + 1; 
    
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error-container').style.display = 'none';

    // FILTRO: Coincide fecha Y la categoría NO contiene "noticia"
    let eventos = BASE_DE_DATOS.filter(item => {
        const cat = (item.categoria || '').toLowerCase();
        const esNoticiaRSS = cat.includes('noticia'); // Detecta "Noticia Local", "Noticia Nacional"
        
        return item.dia === dia && item.mes === mes && !esNoticiaRSS;
    });

    const contenedor = document.getElementById('contenido');

    if (eventos.length === 0) {
        contenedor.innerHTML = `
            <div style="text-align:center; padding: 40px; color: #777;">
                <i class="fas fa-history" style="font-size: 3rem; margin-bottom:15px; opacity:0.5;"></i>
                <h3>Sin Efemérides Históricas</h3>
                <p>No hay eventos históricos cargados para el <strong>${dia}/${mes}</strong>.</p>
                <p><small>(Las noticias recientes están en la sección NOTICIAS)</small></p>
            </div>
        `;
        return;
    }

    ordenarEventos(eventos);
    renderizarTarjetas(eventos);
}

// CASO B: MOSTRAR NOTICIAS (Solo RSS y Actualidad)
function filtrarSoloNoticias() {
    // FILTRO: La categoría DEBE contener "noticia"
    let noticias = BASE_DE_DATOS.filter(item => {
        const cat = (item.categoria || '').toLowerCase();
        return cat.includes('noticia');
    });

    const contenedor = document.getElementById('contenido');
    
    if (noticias.length === 0) {
        contenedor.innerHTML = `
            <div style="text-align:center; padding:40px; color: #777;">
                <i class="fas fa-newspaper" style="font-size: 3rem; margin-bottom:15px; opacity:0.5;"></i>
                <h3>Sin Noticias Recientes</h3>
                <p>No se encontraron noticias RSS descargadas.</p>
                <p><small>Prueba ejecutando 'python actualizar.py'</small></p>
            </div>`;
    } else {
        // Ordenar noticias: Las más recientes arriba (según el orden del array suele bastar, pero forzamos por año)
        // Como todas tienen año 2026, el orden original del RSS (datos.js) es el mejor cronológico inverso.
        // Así que no aplicamos sort complejo, solo renderizamos.
        renderizarTarjetas(noticias);
        document.getElementById('display-date').textContent = "Noticias del Momento";
    }
}

// ==========================================
// VISUALIZACIÓN DE DATOS (Auxiliares)
// ==========================================
function actualizarHeaderFecha(fecha) {
    document.getElementById('display-date').textContent = obtenerFechaTexto(fecha);
}

function obtenerFechaTexto(fecha) {
    const opciones = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const t = fecha.toLocaleDateString('es-ES', opciones);
    return t.charAt(0).toUpperCase() + t.slice(1);
}

// BÚSQUEDA (Busca en TODO: Noticias + Efemérides)
function realizarBusqueda(texto) {
    const termino = texto.toLowerCase().trim();
    if (termino === '') {
        procesarDatosPorFecha(fechaActualVisualizacion);
        return;
    }
    let resultados = BASE_DE_DATOS.filter(item => {
        return (item.titulo && item.titulo.toLowerCase().includes(termino)) || 
               (item.descripcion && item.descripcion.toLowerCase().includes(termino)) ||
               (item.categoria && item.categoria.toLowerCase().includes(termino));
    });
    const contenedor = document.getElementById('contenido');
    if (resultados.length === 0) {
        contenedor.innerHTML = `<div style="text-align:center; padding:20px;">No se encontraron resultados para "${texto}"</div>`;
    } else {
        ordenarEventos(resultados);
        renderizarTarjetas(resultados);
    }
}

// ==========================================
// CALENDARIO
// ==========================================
function renderizarCalendario(mes, anio) {
    const container = document.getElementById('calendarDays');
    const label = document.getElementById('monthYear');
    const meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
    label.textContent = `${meses[mes]} ${anio}`;
    container.innerHTML = '';
    const diasSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    diasSemana.forEach(d => { container.innerHTML += `<div class="day-name">${d}</div>`; });
    const primerDia = new Date(anio, mes, 1).getDay();
    const diasEnMes = new Date(anio, mes + 1, 0).getDate();
    for (let i = 0; i < primerDia; i++) { container.innerHTML += `<div class="calendar-day empty"></div>`; }
    const hoy = new Date();
    for (let d = 1; d <= diasEnMes; d++) {
        const diaElem = document.createElement('div');
        diaElem.className = 'calendar-day';
        diaElem.textContent = d;
        if (d === hoy.getDate() && mes === hoy.getMonth() && anio === hoy.getFullYear()) diaElem.classList.add('today');
        if (d === fechaActualVisualizacion.getDate() && mes === fechaActualVisualizacion.getMonth() && anio === fechaActualVisualizacion.getFullYear()) diaElem.classList.add('active');
        diaElem.addEventListener('click', () => {
            fechaActualVisualizacion = new Date(anio, mes, d);
            actualizarHeaderFecha(fechaActualVisualizacion);
            procesarDatosPorFecha(fechaActualVisualizacion);
            renderizarCalendario(mes, anio);
        });
        container.appendChild(diaElem);
    }
}
document.getElementById('prevMonth').addEventListener('click', () => {
    mesCalendario--;
    if (mesCalendario < 0) { mesCalendario = 11; anioCalendario--; }
    renderizarCalendario(mesCalendario, anioCalendario);
});
document.getElementById('nextMonth').addEventListener('click', () => {
    mesCalendario++;
    if (mesCalendario > 11) { mesCalendario = 0; anioCalendario++; }
    renderizarCalendario(mesCalendario, anioCalendario);
});

function configurarBuscador() {
    const input = document.getElementById('searchInput');
    const btn = document.getElementById('searchBtn');
    input.addEventListener('keyup', () => { realizarBusqueda(input.value); });
    btn.addEventListener('click', () => { realizarBusqueda(input.value); });
}

// ==========================================
// COLORES Y RENDERIZADO
// ==========================================
function obtenerPrioridad(categoria) {
    const cat = (categoria || '').toLowerCase().trim();
    if (cat.includes('celebraci')) return 1;
    if (cat.includes('santo') || cat.includes('religio') || cat.includes('virgen')) return 2;
    if (cat.includes('aniversario') || cat.includes('fundacion')) return 3;
    if (cat.includes('provinc') || cat.includes('local') || cat.includes('region')) return 4;
    return 5;
}

function obtenerColor(categoria) {
    const cat = (categoria || '').toLowerCase().trim();
    
    // NOTICIAS RSS (Verde para Local, Gris para Nacional)
    if (cat.includes('noticia local')) return '#3c6e71'; 
    if (cat.includes('noticia nacional')) return '#333333';

    // EFEMÉRIDES
    if (cat.includes('celebraci')) return '#033f63';
    if (cat.includes('aniversario') || cat.includes('fundacion') || cat.includes('fundación') || cat.includes('cumple')) return '#fb8500';
    if (cat.includes('regional') || cat.includes('provinc') || cat.includes('local') || cat.includes('municip')) return '#3c6e71';
    if (cat.includes('religio') || cat.includes('santo') || cat.includes('virgen')) return '#2563EB';
    
    return '#333333';
}

function ordenarEventos(lista) {
    lista.sort((a, b) => {
        const prioridadA = obtenerPrioridad(a.categoria);
        const prioridadB = obtenerPrioridad(b.categoria);
        if (prioridadA !== prioridadB) return prioridadA - prioridadB;
        const anioA = parseInt(a.anio) || 9999;
        const anioB = parseInt(b.anio) || 9999;
        return anioA - anioB;
    });
}

function renderizarTarjetas(lista) {
    const contenedor = document.getElementById('contenido');
    contenedor.innerHTML = '';
    
    lista.forEach(item => {
        const colorTema = obtenerColor(item.categoria);
        const tarjeta = document.createElement('div');
        tarjeta.className = 'card';
        tarjeta.style.borderLeftColor = colorTema;

        tarjeta.innerHTML = `
            <div class="card-header">
                <span class="badge-anio">${item.anio || ''}</span>
                <span class="badge-cat" style="color: ${colorTema}; border: 1px solid ${colorTema};">
                    ${item.categoria || ''}
                </span>
            </div>
            <h3 style="color: ${colorTema}">${item.titulo || 'Sin título'}</h3>
            <div class="card-description" onclick="toggleDescripcion(this)">
                ${item.descripcion || ''}
            </div>
        `;
        contenedor.appendChild(tarjeta);
    });
}

window.toggleDescripcion = function(elemento) {
    elemento.classList.toggle('locked');
};