const API_BASE_URL = (import.meta.env.PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

export interface Menor {
  id: string;
  madre_id: string;
  nombre: string;
  fecha_nacimiento: string;
  alergias?: string;
  requerimientos_medicos?: string;
  creado_en: string;
}

export interface Solicitud {
  id: string;
  madre_id: string;
  menor_id: string;
  inicio_requerido: string;
  fin_requerido: string;
  estado: "Pendiente" | "Parcial" | "Cubierta";
  creado_en: string;
  menor?: Menor;
}

export interface Evento {
  id: string;
  titulo: string;
  descripcion?: string;
  inicio_evento: string;
  fin_evento: string;
  capacidad_maxima: number;
  id_admin: string;
  creado_en: string;
  aforo_actual?: number;
  cupos_disponibles?: number;
}

export interface Reserva {
  id: string;
  evento_id: string;
  solicitud_id: string;
  creado_en: string;
}

export interface Usuario {
  id: string;
  nombre: string;
  correo: string;
  telefono?: string;
  rol: "madre" | "admin";
  proveedor_auth: string;
  activo: boolean;
  creado_en: string;
}

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem("token");
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export async function obtenerPerfil(): Promise<Usuario> {
  const response = await fetch(`${API_BASE_URL}/usuarios/me`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw response;
  return response.json();
}

export async function obtenerMenores(): Promise<Menor[]> {
  const response = await fetch(`${API_BASE_URL}/menores/`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw response;
  return response.json();
}

export async function crearMenor(datos: {
  nombre: string;
  fecha_nacimiento: string;
  alergias?: string;
  requerimientos_medicos?: string;
}): Promise<Menor> {
  const response = await fetch(`${API_BASE_URL}/menores/`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(datos),
  });
  if (!response.ok) throw response;
  return response.json();
}

export async function obtenerSolicitudes(): Promise<Solicitud[]> {
  const response = await fetch(`${API_BASE_URL}/solicitudes/`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw response;
  return response.json();
}

export async function crearSolicitud(datos: {
  menor_id: string;
  inicio_requerido: string;
  fin_requerido: string;
}): Promise<Solicitud> {
  const response = await fetch(`${API_BASE_URL}/solicitudes/`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(datos),
  });
  if (!response.ok) throw response;
  return response.json();
}

export async function obtenerSolicitudesConsolidadas(): Promise<Solicitud[]> {
  const response = await fetch(`${API_BASE_URL}/solicitudes/consolidadas`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw response;
  return response.json();
}

export async function obtenerEventos(): Promise<Evento[]> {
  const response = await fetch(`${API_BASE_URL}/eventos/`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw response;
  return response.json();
}

export async function crearEvento(datos: {
  titulo: string;
  descripcion?: string;
  inicio_evento: string;
  fin_evento: string;
  capacidad_maxima: number;
}): Promise<Evento> {
  const response = await fetch(`${API_BASE_URL}/eventos/`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(datos),
  });
  if (!response.ok) throw response;
  return response.json();
}

export async function reservarCupo(eventoId: string, solicitudId: string): Promise<Reserva> {
  const response = await fetch(`${API_BASE_URL}/eventos/${eventoId}/reservar?solicitud_id=${solicitudId}`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw response;
  return response.json();
}
