
import { loadDocument, loadDocumentByString } from '../'
import fs from 'fs'
import url from 'url'

describe('Example Tests', () => {

    it('valid1', async () => {
        await loadDocument(__dirname + '/data/examples/valid1.yml')
    })
    it('valid1 by string', async () => {
        let doc = fs.readFileSync(__dirname + '/data/examples/valid1.yml').toString()
        await loadDocumentByString(doc, url.pathToFileURL(__dirname +
            '/data/examples/').toString())
    })
})
