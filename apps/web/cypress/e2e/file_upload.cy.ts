describe('File upload', () => {
  it('uploads and downloads a file via API', () => {
    cy.fixture('test.pdf', 'binary').then(fileContent => {
      cy.request({
        method: 'POST',
        url: 'http://localhost:8000/v1/files/upload',
        headers: { Authorization: 'Bearer test' },
        form: true,
        body: {
          file: {
            fileContent,
            fileName: 'test.pdf',
            mimeType: 'application/pdf'
          },
          category: 'general'
        }
      }).then(res => {
        expect(res.status).to.eq(200)
        const id = res.body.id
        cy.request({
          url: `http://localhost:8000/v1/files/${id}`,
          headers: { Authorization: 'Bearer test' }
        }).its('status').should('eq', 200)
      })
    })
  })
})
