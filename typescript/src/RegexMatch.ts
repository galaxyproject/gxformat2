
import {
  Dictionary,
  expandUrl,
  loadField,
  LoaderInstances,
  LoadingOptions,
  Saveable,
  ValidationException,
  prefixUrl,
  save,
  saveRelativeUri
} from './util/Internal'
import { v4 as uuidv4 } from 'uuid'
import * as Internal from './util/Internal'


/**
 * Auto-generated class implementation for https://galaxyproject.org/gxformat2/v19_09#RegexMatch
 */
export class RegexMatch extends Saveable implements Internal.RegexMatchProperties {
  extensionFields?: Internal.Dictionary<any>

  /**
   * Check if a regular expression matches the value. A value is only valid if a match is found.
   */
  regex: string

  /**
   * Message to provide to user if validator did not succeed.
   */
  doc: string


  constructor ({loadingOptions, extensionFields, regex, doc} : {loadingOptions?: LoadingOptions} & Internal.RegexMatchProperties) {
    super(loadingOptions)
    this.extensionFields = extensionFields ?? {}
    this.regex = regex
    this.doc = doc
  }

  /**
   * Used to construct instances of {@link RegexMatch }.
   *
   * @param __doc                           Document fragment to load this record object from.
   * @param baseuri                         Base URI to generate child document IDs against.
   * @param loadingOptions                  Context for loading URIs and populating objects.
   * @param docRoot                         ID at this position in the document (if available)
   * @returns                               An instance of {@link RegexMatch }
   * @throws {@link ValidationException}    If the document fragment is not a
   *                                        {@link Dictionary} or validation of fields fails.
   */
  static override async fromDoc (__doc: any, baseuri: string, loadingOptions: LoadingOptions,
    docRoot?: string): Promise<Saveable> {
    const _doc = Object.assign({}, __doc)
    const __errors: ValidationException[] = []
            
    let regex
    try {
      regex = await loadField(_doc.regex, LoaderInstances.unionOfstrtype,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `regex` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    let doc
    try {
      doc = await loadField(_doc.doc, LoaderInstances.unionOfstrtype,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `doc` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    const extensionFields: Dictionary<any> = {}
    for (const [key, value] of Object.entries(_doc)) {
      if (!RegexMatch.attr.has(key)) {
        if ((key as string).includes(':')) {
          const ex = expandUrl(key, '', loadingOptions, false, false)
          extensionFields[ex] = value
        } else {
          __errors.push(
            new ValidationException(`invalid field ${key as string}, \
            expected one of: \`regex\`,\`doc\``)
          )
          break
        }
      }
    }

    if (__errors.length > 0) {
      throw new ValidationException("Trying 'RegexMatch'", __errors)
    }

    const schema = new RegexMatch({
      extensionFields: extensionFields,
      loadingOptions: loadingOptions,
      regex: regex,
      doc: doc
    })
    return schema
  }
        
  save (top: boolean = false, baseUrl: string = '', relativeUris: boolean = true)
  : Dictionary<any> {
    const r: Dictionary<any> = {}
    for (const ef in this.extensionFields) {
      r[prefixUrl(ef, this.loadingOptions.vocab)] = this.extensionFields.ef
    }

    if (this.regex != null) {
      r.regex = save(this.regex, false, baseUrl, relativeUris)
    }
                
    if (this.doc != null) {
      r.doc = save(this.doc, false, baseUrl, relativeUris)
    }
                
    if (top) {
      if (this.loadingOptions.namespaces != null) {
        r.$namespaces = this.loadingOptions.namespaces
      }
      if (this.loadingOptions.schemas != null) {
        r.$schemas = this.loadingOptions.schemas
      }
    }
    return r
  }
            
  static attr: Set<string> = new Set(['regex','doc'])
}
