import { test, expect } from '@playwright/test';

test.describe('Pruebas de Control de Acceso Basado en Roles (RBAC)', () => {

  test('El voluntario no ve el enlace Panel Admin y tiene el acceso denegado en el Dashboard', async ({ page }) => {
    // 1. Navegar a la landing para inicializar el origen de localStorage
    await page.goto('http://localhost:4321/');

    // JWT simulado para voluntario@test.com
    const tokenVoluntario = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InZvbHVudGFyaW9AdGVzdC5jb20iLCJzdWIiOiI2OWViOTRjYS1mYTIzLTQxYmItYmZhNi1hNzBkNjc2ZWU1NmMiLCJ1c2VyX21ldGFkYXRhIjp7ImZ1bGxfbmFtZSI6IlZvbHVudGFyaW9QcnVlYmEifX0=.signature';

    await page.evaluate((jwt) => {
      localStorage.setItem('token', jwt);
    }, tokenVoluntario);

    // 2. Navegar a la página de eventos del voluntario
    await page.goto('http://localhost:4321/voluntario/eventos');
    await page.waitForLoadState('domcontentloaded');

    // 3. Afirmar que el enlace del Panel Admin está oculto o no es visible
    const linkAdmin = page.locator('#nav-link-admin');
    await expect(linkAdmin).toBeHidden();

    // 4. Forzar navegación directa al Dashboard administrativo
    await page.goto('http://localhost:4321/admin/dashboard');
    await page.waitForLoadState('domcontentloaded');

    // 5. Afirmar que el texto "Acceso Denegado" es visible
    const accesoDenegadoText = page.locator('text=Acceso Denegado');
    await expect(accesoDenegadoText).toBeVisible();

    // 6. Esperar la redirección (3 segundos) y verificar retorno al catálogo
    await page.waitForURL('**/voluntario/eventos', { timeout: 5000 });
    expect(page.url()).toContain('/voluntario/eventos');
  });

});
