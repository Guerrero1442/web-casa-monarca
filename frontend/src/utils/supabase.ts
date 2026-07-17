import { createClient } from "@supabase/supabase-js";

// Obtener las variables de entorno de Supabase públicas de Astro
let supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = import.meta.env.PUBLIC_SUPABASE_ANON_KEY || "";

// Limpieza inteligente de la URL en caso de que incluya sufijos /rest/v1/ o barras finales redundantes
if (supabaseUrl) {
  supabaseUrl = supabaseUrl
    .replace(/\/rest\/v1\/?$/, "")
    .replace(/\/auth\/v1\/?$/, "")
    .trim()
    .replace(/\/+$/, "");
}

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(
    "Supabase credentials are missing. Verify PUBLIC_SUPABASE_URL and PUBLIC_SUPABASE_ANON_KEY in env variables."
  );
}

// Inicializar el cliente
export const supabase = createClient(supabaseUrl, supabaseAnonKey);
