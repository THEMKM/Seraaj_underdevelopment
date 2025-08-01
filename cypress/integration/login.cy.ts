describe('Login Flow', () => {
  it('allows a user to log in', () => {
    cy.visit('/auth/login');
    cy.get('input[name="email"]').type('layla@example.com');
    cy.get('input[name="password"]').type('Demo123!');
    cy.contains('button', 'Login').click();
    cy.url().should('include', '/feed');
  });
});
