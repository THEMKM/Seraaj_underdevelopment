describe('Activity Feed', () => {
  before(() => {
    cy.login('layla@example.com', 'Demo123!');
  });

  it('loads opportunities', () => {
    cy.visit('/feed');
    cy.contains('Opportunities');
  });
});
