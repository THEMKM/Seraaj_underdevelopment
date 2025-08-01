import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3030',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/integration/**/*.cy.ts',
  },
});
