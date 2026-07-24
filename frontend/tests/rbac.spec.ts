import { test, expect } from '@playwright/test';

test.describe('Pruebas E2E de Autenticación y Control de Acceso (RBAC) - Cuidado Infantil', () => {

  test('La madre inicia sesión y es redirigida a /solicitud sin error 404', async ({ page }) => {
    // 1. Navegar a la landing
    await page.goto('http://localhost:4321/');
    await page.waitForLoadState('domcontentloaded');

    // Token JWT simulado para madre@test.com (rol 'madre')
    const tokenMadre = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im1hZHJlQHRlc3QuY29tIiwic3ViIjoiNjlhYjk0Y2EtZmEyMy00MWJiLWJmYTYtYTcwZDY3NmVlNTZjIiwidXNlcl9tZXRhZGF0YSI6eyJmdWxsX25hbWUiOiJNYWRyZSBQcnVlYmEifX0=.signature';

    await page.evaluate((jwt) => {
      localStorage.setItem('token', jwt);
    }, tokenMadre);

    // Recargar landing para activar el contenedor de sesión activa
    await page.goto('http://localhost:4321/');
    await page.waitForLoadState('domcontentloaded');

    // Hacer clic en el botón "Ir a Solicitudes de Cuidado"
    const btnPanel = page.locator('#btn-ir-panel');
    await expect(btnPanel).toBeVisible();
    await btnPanel.click();

    // Afirmar que la URL final sea exactamente /solicitud
    await page.waitForURL('**/solicitud');
    expect(page.url()).toContain('/solicitud');

    // Validar que la vista cargue correctamente sin 404
    const tituloVista = page.locator('h2:has-text("Solicitud de Cuidado Infantil")');
    await expect(tituloVista).toBeVisible();
  });

  test('El usuario madre no puede acceder al Dashboard Admin y es redirigido a /solicitud', async ({ page }) => {
    await page.goto('http://localhost:4321/');

    const tokenMadre = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im1hZHJlQHRlc3QuY29tIiwic3ViIjoiNjlhYjk0Y2EtZmEyMy00MWJiLWJmYTYtYTcwZDY3NmVlNTZjIiwidXNlcl9tZXRhZGF0YSI6eyJmdWxsX25hbWUiOiJNYWRyZSBQcnVlYmEifX0=.signature';

    await page.evaluate((jwt) => {
      localStorage.setItem('token', jwt);
    }, tokenMadre);

    // Navegar directamente a admin/dashboard
    await page.goto('http://localhost:4321/admin/dashboard');
    await page.waitForLoadState('domcontentloaded');

    // Validar cartel de acceso denegado
    const accesoDenegadoText = page.locator('text=Acceso Denegado');
    await expect(accesoDenegadoText).toBeVisible();

    // Esperar la redirección a /solicitud
    await page.waitForURL('**/solicitud', { timeout: 5000 });
    expect(page.url()).toContain('/solicitud');
  });

});
