# Sistema de Diseño Base (Tokens Visuales)

## 1. Paleta de Colores
El frontend debe implementar las siguientes variables de color de forma global:
- **Fondo Principal (`bg-background`):** Crema claro / Beige suave (Referencia: #F5F3ED). Utilizado para el fondo general de la aplicación.
- **Color Primario (`bg-primary`):** Terracota / Naranja quemado (Referencia: #C36B53). Utilizado para botones de acción principales (ej. "Inscribirme", "Publicar evento") y textos de énfasis (ej. "Cupos: 8/20").
- **Color Secundario / Oscuro (`bg-secondary`):** Verde bosque oscuro (Referencia: #23352F). Utilizado para botones secundarios, encabezados principales y el contenedor principal de navegación o bordes de tarjetas activas.
- **Superficies (`bg-surface`):** Blanco puro (Referencia: #FFFFFF). Utilizado para el interior de las tarjetas de eventos y contenedores de formularios.
- **Acentos Neutros:** Gris claro/verde claro para botones inactivos o fondos de áreas informativas menores (ej. el recuadro de "Crear redes para acompañar...").

## 2. Tipografía y Textos
- **Fuente:** Sans-serif moderna y limpia (ej. Inter o Roboto).
- **Color de texto principal:** Verde bosque oscuro (#23352F).
- **Color de texto secundario/metadatos:** Gris oscuro u opaco para fechas, horas y subtítulos.

## 3. Patrones de Componentes (UI)
- **Botones:** Estilo "Pill" (completamente redondeados, ej. `border-radius: 9999px` o `rounded-full` en Tailwind). Sin sombras pronunciadas, diseño plano (Flat Design).
- **Tarjetas (Cards):** Utilizadas para listar eventos y mostrar resúmenes. Fondo blanco, bordes moderadamente redondeados (`rounded-xl` o `rounded-2xl`), sin sombras pesadas, separadas por márgenes definidos. En ocasiones, presentan un borde lateral izquierdo de color (terracota, amarillo o verde) para indicar el estado del evento.
- **Formularios:** Campos de entrada de texto con fondo blanco, bordes sutiles y esquinas redondeadas.

## Regla Estricta de Implementación
El agente utilizará estos tokens de color y estilos de componentes genéricos (tarjetas, botones redondeados) al construir las vistas del frontend. El agente NO debe intentar replicar la disposición exacta de los elementos (layout) mostrada en los mockups, sino aplicar este sistema visual a las estructuras de datos que devuelva la API.


## 4. Configuración de Tailwind CSS

// Estructura base exigida para tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F5F3ED",
        primary: {
          DEFAULT: "#C36B53",
          hover: "#A85A45", // Variante calculada para interacciones
        },
        secondary: {
          DEFAULT: "#23352F",
          hover: "#1A2823",
        },
        surface: "#FFFFFF",
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        'pill': '9999px',
      }
    },
  },
  plugins: [],
}


/* Instrucción para el archivo CSS global del frontend */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-background text-secondary font-sans antialiased;
  }
}

@layer components {
  .btn-primary {
    @apply bg-primary text-white font-medium py-3 px-6 rounded-pill transition-colors duration-200 hover:bg-primary-hover active:scale-95;
  }
  
  .btn-secondary {
    @apply bg-secondary text-white font-medium py-3 px-6 rounded-pill transition-colors duration-200 hover:bg-secondary-hover active:scale-95;
  }

  .card-evento {
    @apply bg-surface rounded-2xl p-5 shadow-sm border border-gray-100 flex flex-col gap-2;
  }
}