describe('Opportunity Application', () => {
  before(() => {
    cy.login('layla@example.com', 'Demo123!');
  });

  it('submits an application from the feed', () => {
    cy.visit('/feed');
    cy.get('button').contains('Apply').first().click();
    cy.contains('Application submitted');
  });
});
