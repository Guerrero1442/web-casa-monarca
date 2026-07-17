const API_BASE_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

export interface Evento {
  id: string;
  titulo: string;
  descripcion?: string;
  fecha_inicio: string;
  fecha_fin: string;
  duracion_horas: number;
  cupo_maximo: number;
  lugar: string;
  id_admin: string;
  creado_en: string;
  cupos_disponibles: number;
  usuario_inscrito: boolean;
}

export interface Inscripcion {
  id: string;
  usuario_id: string;
  evento_id: string;
  asistio: boolean;
  creado_en: string;
}

export interface Usuario {
  id: string;
  nombre: string;
  correo: string;
  telefono?: string;
  rol: string;
  proveedor_auth: string;
  activo: boolean;
  creado_en: string;
}

export interface InscripcionConUsuario extends Inscripcion {
  usuario: Usuario;
}

export interface ImpactoVoluntario {
  total_horas: number;
  total_eventos: number;
  eventos_asistidos: Evento[];
}

/**
 * Decodifica el payload de un token JWT de Supabase de forma ligera en el cliente.
 */
function parseJwt(token: string): any {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

/**
 * Obtiene las cabeceras de autorización HTTP inyectando el JWT de localStorage.
 */
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

/**
 * Recupera la lista de eventos disponibles del backend.
 */
export async function obtenerEventos(): Promise<Evento[]> {
  const response = await fetch(`${API_BASE_URL}/eventos/`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw response;
  }

  return response.json();
}

/**
 * Registra la inscripción del voluntario autenticado en un evento.
 */
export async function inscribirVoluntario(eventoId: string): Promise<Inscripcion> {
  const token = localStorage.getItem("token");
  if (!token) {
    throw new Error("No autenticado");
  }

  const payload = parseJwt(token);
  const usuarioId = payload?.sub;

  if (!usuarioId) {
    throw new Error("Token de sesión inválido");
  }

  const response = await fetch(`${API_BASE_URL}/inscripciones/`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      usuario_id: usuarioId,
      evento_id: eventoId,
    }),
  });

  if (!response.ok) {
    throw response;
  }

  return response.json();
}

/**
 * Obtiene la lista de inscritos para un evento específico.
 */
export async function obtenerInscritosEvento(
  eventoId: string
): Promise<InscripcionConUsuario[]> {
  const response = await fetch(
    `${API_BASE_URL}/eventos/${eventoId}/inscritos`,
    {
      method: "GET",
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    throw response;
  }

  return response.json();
}

/**
 * Actualiza masivamente el estado de asistencia de múltiples inscripciones.
 */
export async function actualizarAsistenciaMasiva(
  eventoId: string,
  inscripcionIds: string[]
): Promise<{ status: string; message: string }> {
  const response = await fetch(
    `${API_BASE_URL}/eventos/${eventoId}/asistencia`,
    {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        inscripcion_ids: inscripcionIds,
      }),
    }
  );

  if (!response.ok) {
    throw response;
  }

  return response.json();
}

/**
 * Obtiene el perfil del usuario autenticado actual.
 */
export async function obtenerPerfil(): Promise<Usuario> {
  const response = await fetch(`${API_BASE_URL}/usuarios/me`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw response;
  }

  return response.json();
}

/**
 * Actualiza los datos del perfil (nombre y/o teléfono) del voluntario actual.
 */
export async function actualizarPerfil(datos: { nombre?: string; telefono?: string }): Promise<Usuario> {
  const response = await fetch(`${API_BASE_URL}/usuarios/me`, {
    method: "PATCH",
    headers: getAuthHeaders(),
    body: JSON.stringify(datos),
  });

  if (!response.ok) {
    throw response;
  }

  return response.json();
}

/**
 * Obtiene el impacto del voluntario (horas y lista de eventos asistidos).
 */
export async function obtenerImpacto(): Promise<ImpactoVoluntario> {
  const response = await fetch(`${API_BASE_URL}/usuarios/me/impacto`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw response;
  }

  return response.json();
}

/**
 * Crea un nuevo evento en el backend (solo para administradores).
 */
export async function crearEvento(eventoData: {
  titulo: string;
  descripcion?: string;
  fecha_inicio: string;
  fecha_fin: string;
  duracion_horas: number;
  cupo_maximo: number;
  lugar: string;
  id_admin: string;
}): Promise<Evento> {
  const response = await fetch(`${API_BASE_URL}/eventos/`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(eventoData),
  });

  if (!response.ok) {
    throw response;
  }

  return response.json();
}

export interface EventoUpdate {
  titulo?: string;
  descripcion?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  duracion_horas?: number;
  cupo_maximo?: number;
  lugar?: string;
}

/**
 * Cancela la inscripción de un voluntario en un evento.
 */
export async function cancelarInscripcion(eventoId: string): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/eventos/${eventoId}/inscripcion`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw response;
  }

  return response.json();
}

/**
 * Actualiza los datos de un evento (solo administradores).
 */
export async function actualizarEvento(eventoId: string, datos: EventoUpdate): Promise<Evento> {
  const response = await fetch(`${API_BASE_URL}/eventos/${eventoId}`, {
    method: "PATCH",
    headers: getAuthHeaders(),
    body: JSON.stringify(datos),
  });

  if (!response.ok) {
    throw response;
  }

  return response.json();
}

/**
 * Elimina un evento de forma permanente (solo administradores).
 */
export async function eliminarEvento(eventoId: string): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/eventos/${eventoId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw response;
  }

  return response.json();
}

/**
 * Completa el flujo de onboarding obligatorios para el voluntario.
 */
export async function completarOnboarding(datos: {
  nombre: string;
  fecha_nacimiento: string;
  sexo: string;
  telefono: string;
}): Promise<Usuario> {
  const response = await fetch(`${API_BASE_URL}/usuarios/me/onboarding`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(datos),
  });

  if (!response.ok) {
    throw response;
  }

  return response.json();
}
