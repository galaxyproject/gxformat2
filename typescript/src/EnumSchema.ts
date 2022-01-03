
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
 * Auto-generated class implementation for https://w3id.org/cwl/salad#EnumSchema
 *
 * Define an enumerated type.
 * 
 */
export class EnumSchema extends Saveable implements Internal.EnumSchemaProperties {
  extensionFields?: Internal.Dictionary<any>

  /**
   * Defines the set of valid symbols.
   */
  symbols: Array<string>

  /**
   * Must be `enum`
   */
  type: Internal.enum_d961d79c225752b9fadb617367615ab176b47d77


  constructor ({loadingOptions, extensionFields, symbols, type} : {loadingOptions?: LoadingOptions} & Internal.EnumSchemaProperties) {
    super(loadingOptions)
    this.extensionFields = extensionFields ?? {}
    this.symbols = symbols
    this.type = type
  }

  /**
   * Used to construct instances of {@link EnumSchema }.
   *
   * @param __doc                           Document fragment to load this record object from.
   * @param baseuri                         Base URI to generate child document IDs against.
   * @param loadingOptions                  Context for loading URIs and populating objects.
   * @param docRoot                         ID at this position in the document (if available)
   * @returns                               An instance of {@link EnumSchema }
   * @throws {@link ValidationException}    If the document fragment is not a
   *                                        {@link Dictionary} or validation of fields fails.
   */
  static override async fromDoc (__doc: any, baseuri: string, loadingOptions: LoadingOptions,
    docRoot?: string): Promise<Saveable> {
    const _doc = Object.assign({}, __doc)
    const __errors: ValidationException[] = []
            
    let symbols
    try {
      symbols = await loadField(_doc.symbols, LoaderInstances.uriarrayOfstrtypeTrueFalseNone,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `symbols` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    let type
    try {
      type = await loadField(_doc.type, LoaderInstances.typedslenum_d961d79c225752b9fadb617367615ab176b47d77Loader2,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `type` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    const extensionFields: Dictionary<any> = {}
    for (const [key, value] of Object.entries(_doc)) {
      if (!EnumSchema.attr.has(key)) {
        if ((key as string).includes(':')) {
          const ex = expandUrl(key, '', loadingOptions, false, false)
          extensionFields[ex] = value
        } else {
          __errors.push(
            new ValidationException(`invalid field ${key as string}, \
            expected one of: \`symbols\`,\`type\``)
          )
          break
        }
      }
    }

    if (__errors.length > 0) {
      throw new ValidationException("Trying 'EnumSchema'", __errors)
    }

    const schema = new EnumSchema({
      extensionFields: extensionFields,
      loadingOptions: loadingOptions,
      symbols: symbols,
      type: type
    })
    return schema
  }
        
  save (top: boolean = false, baseUrl: string = '', relativeUris: boolean = true)
  : Dictionary<any> {
    const r: Dictionary<any> = {}
    for (const ef in this.extensionFields) {
      r[prefixUrl(ef, this.loadingOptions.vocab)] = this.extensionFields.ef
    }

    if (this.symbols != null) {
      const u = saveRelativeUri(this.symbols, baseUrl, true,
                                relativeUris, undefined)
      if (u != null) {
        r.symbols = u
      }
    }
                
    if (this.type != null) {
      r.type = save(this.type, false, baseUrl, relativeUris)
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
            
  static attr: Set<string> = new Set(['symbols','type'])
}
