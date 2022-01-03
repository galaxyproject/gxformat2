
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
 * Auto-generated class implementation for https://galaxyproject.org/gxformat2/gxformat2common#StepPosition
 *
 * This field specifies the location of the step's node when rendered in the workflow editor.
 */
export class StepPosition extends Saveable implements Internal.StepPositionProperties {
  extensionFields?: Internal.Dictionary<any>

  /**
   * Relative vertical position of the step's node when rendered in the workflow editor.
   * 
   */
  top: number

  /**
   * Relative horizontal position of the step's node when rendered in the workflow editor.
   * 
   */
  left: number


  constructor ({loadingOptions, extensionFields, top, left} : {loadingOptions?: LoadingOptions} & Internal.StepPositionProperties) {
    super(loadingOptions)
    this.extensionFields = extensionFields ?? {}
    this.top = top
    this.left = left
  }

  /**
   * Used to construct instances of {@link StepPosition }.
   *
   * @param __doc                           Document fragment to load this record object from.
   * @param baseuri                         Base URI to generate child document IDs against.
   * @param loadingOptions                  Context for loading URIs and populating objects.
   * @param docRoot                         ID at this position in the document (if available)
   * @returns                               An instance of {@link StepPosition }
   * @throws {@link ValidationException}    If the document fragment is not a
   *                                        {@link Dictionary} or validation of fields fails.
   */
  static override async fromDoc (__doc: any, baseuri: string, loadingOptions: LoadingOptions,
    docRoot?: string): Promise<Saveable> {
    const _doc = Object.assign({}, __doc)
    const __errors: ValidationException[] = []
            
    let top
    try {
      top = await loadField(_doc.top, LoaderInstances.unionOffloattypeOrinttype,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `top` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    let left
    try {
      left = await loadField(_doc.left, LoaderInstances.unionOffloattypeOrinttype,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `left` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    const extensionFields: Dictionary<any> = {}
    for (const [key, value] of Object.entries(_doc)) {
      if (!StepPosition.attr.has(key)) {
        if ((key as string).includes(':')) {
          const ex = expandUrl(key, '', loadingOptions, false, false)
          extensionFields[ex] = value
        } else {
          __errors.push(
            new ValidationException(`invalid field ${key as string}, \
            expected one of: \`top\`,\`left\``)
          )
          break
        }
      }
    }

    if (__errors.length > 0) {
      throw new ValidationException("Trying 'StepPosition'", __errors)
    }

    const schema = new StepPosition({
      extensionFields: extensionFields,
      loadingOptions: loadingOptions,
      top: top,
      left: left
    })
    return schema
  }
        
  save (top: boolean = false, baseUrl: string = '', relativeUris: boolean = true)
  : Dictionary<any> {
    const r: Dictionary<any> = {}
    for (const ef in this.extensionFields) {
      r[prefixUrl(ef, this.loadingOptions.vocab)] = this.extensionFields.ef
    }

    if (this.top != null) {
      r.top = save(this.top, false, baseUrl, relativeUris)
    }
                
    if (this.left != null) {
      r.left = save(this.left, false, baseUrl, relativeUris)
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
            
  static attr: Set<string> = new Set(['top','left'])
}
