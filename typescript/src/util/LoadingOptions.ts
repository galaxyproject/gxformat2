import { Dictionary, DefaultFetcher, Fetcher, RVOCAB, VOCAB } from './Internal'

export class LoadingOptions {
  fetcher: Fetcher
  idx: Dictionary<any>
  fileUri?: string
  namespaces?: Dictionary<string>
  schemas?: Dictionary<string>
  copyFrom?: LoadingOptions
  originalDoc: any
  vocab: Dictionary<string>
  rvocab: Dictionary<string>

  constructor ({ fileUri, namespaces, schemas, originalDoc, copyFrom, fetcher }: {fileUri?: string, namespaces?: Dictionary<string>, schemas?: Dictionary<string>, originalDoc?: any, copyFrom?: LoadingOptions, fetcher?: Fetcher}) {
    this.idx = {}
    this.fileUri = fileUri
    this.namespaces = namespaces
    this.schemas = schemas
    this.originalDoc = originalDoc

    if (copyFrom != null) {
      this.idx = copyFrom.idx
      if (fetcher === undefined) {
        this.fetcher = copyFrom.fetcher
      }
      if (fileUri === undefined) {
        this.fileUri = copyFrom.fileUri
      }
      if (namespaces === undefined) {
        this.namespaces = copyFrom.namespaces
      }
      if (schemas === undefined) {
        this.schemas = copyFrom.schemas
      }
    }

    if (fetcher != null) {
      this.fetcher = fetcher
    } else {
      this.fetcher = new DefaultFetcher()
    }

    this.vocab = VOCAB
    this.rvocab = RVOCAB

    if (namespaces != null) {
      this.vocab = { ...this.vocab }
      this.rvocab = { ...this.rvocab }
      for (const key in namespaces) {
        const value = namespaces[key]
        this.vocab[key] = value
        this.rvocab[value] = key
      }
    }
  }
}
