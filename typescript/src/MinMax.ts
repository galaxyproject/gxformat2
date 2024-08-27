
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
 * Auto-generated class implementation for https://galaxyproject.org/gxformat2/v19_09#MinMax
 */
export class MinMax extends Saveable implements Internal.MinMaxProperties {
  extensionFields?: Internal.Dictionary<any>
  min?: number | undefined
  max?: number | undefined


  constructor ({loadingOptions, extensionFields, min, max} : {loadingOptions?: LoadingOptions} & Internal.MinMaxProperties) {
    super(loadingOptions)
    this.extensionFields = extensionFields ?? {}
    this.min = min
    this.max = max
  }

  /**
   * Used to construct instances of {@link MinMax }.
   *
   * @param __doc                           Document fragment to load this record object from.
   * @param baseuri                         Base URI to generate child document IDs against.
   * @param loadingOptions                  Context for loading URIs and populating objects.
   * @param docRoot                         ID at this position in the document (if available)
   * @returns                               An instance of {@link MinMax }
   * @throws {@link ValidationException}    If the document fragment is not a
   *                                        {@link Dictionary} or validation of fields fails.
   */
  static override async fromDoc (__doc: any, baseuri: string, loadingOptions: LoadingOptions,
    docRoot?: string): Promise<Saveable> {
    const _doc = Object.assign({}, __doc)
    const __errors: ValidationException[] = []
            
    let min
    if ('min' in _doc) {
      try {
        min = await loadField(_doc.min, LoaderInstances.unionOfinttypeOrfloattypeOrundefinedtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `min` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let max
    if ('max' in _doc) {
      try {
        max = await loadField(_doc.max, LoaderInstances.unionOfinttypeOrfloattypeOrundefinedtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `max` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    const extensionFields: Dictionary<any> = {}
    for (const [key, value] of Object.entries(_doc)) {
      if (!MinMax.attr.has(key)) {
        if ((key as string).includes(':')) {
          const ex = expandUrl(key, '', loadingOptions, false, false)
          extensionFields[ex] = value
        } else {
          __errors.push(
            new ValidationException(`invalid field ${key as string}, \
            expected one of: \`min\`,\`max\``)
          )
          break
        }
      }
    }

    if (__errors.length > 0) {
      throw new ValidationException("Trying 'MinMax'", __errors)
    }

    const schema = new MinMax({
      extensionFields: extensionFields,
      loadingOptions: loadingOptions,
      min: min,
      max: max
    })
    return schema
  }
        
  save (top: boolean = false, baseUrl: string = '', relativeUris: boolean = true)
  : Dictionary<any> {
    const r: Dictionary<any> = {}
    for (const ef in this.extensionFields) {
      r[prefixUrl(ef, this.loadingOptions.vocab)] = this.extensionFields.ef
    }

    if (this.min != null) {
      r.min = save(this.min, false, baseUrl, relativeUris)
    }
                
    if (this.max != null) {
      r.max = save(this.max, false, baseUrl, relativeUris)
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
            
  static attr: Set<string> = new Set(['min','max'])
}
