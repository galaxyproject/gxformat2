
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
 * Auto-generated class implementation for https://w3id.org/cwl/salad#ArraySchema
 */
export class ArraySchema extends Saveable implements Internal.ArraySchemaProperties {
  extensionFields?: Internal.Dictionary<any>

  /**
   * Defines the type of the array elements.
   */
  items: Internal.PrimitiveType | Internal.RecordSchema | Internal.EnumSchema | Internal.ArraySchema | string | Array<Internal.PrimitiveType | Internal.RecordSchema | Internal.EnumSchema | Internal.ArraySchema | string>

  /**
   * Must be `array`
   */
  type: Internal.enum_d062602be0b4b8fd33e69e29a841317b6ab665bc


  constructor ({loadingOptions, extensionFields, items, type} : {loadingOptions?: LoadingOptions} & Internal.ArraySchemaProperties) {
    super(loadingOptions)
    this.extensionFields = extensionFields ?? {}
    this.items = items
    this.type = type
  }

  /**
   * Used to construct instances of {@link ArraySchema }.
   *
   * @param __doc                           Document fragment to load this record object from.
   * @param baseuri                         Base URI to generate child document IDs against.
   * @param loadingOptions                  Context for loading URIs and populating objects.
   * @param docRoot                         ID at this position in the document (if available)
   * @returns                               An instance of {@link ArraySchema }
   * @throws {@link ValidationException}    If the document fragment is not a
   *                                        {@link Dictionary} or validation of fields fails.
   */
  static override async fromDoc (__doc: any, baseuri: string, loadingOptions: LoadingOptions,
    docRoot?: string): Promise<Saveable> {
    const _doc = Object.assign({}, __doc)
    const __errors: ValidationException[] = []
            
    let items
    try {
      items = await loadField(_doc.items, LoaderInstances.uriunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeOrarrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeFalseTrue2,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `items` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    let type
    try {
      type = await loadField(_doc.type, LoaderInstances.typedslenum_d062602be0b4b8fd33e69e29a841317b6ab665bcLoader2,
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
      if (!ArraySchema.attr.has(key)) {
        if ((key as string).includes(':')) {
          const ex = expandUrl(key, '', loadingOptions, false, false)
          extensionFields[ex] = value
        } else {
          __errors.push(
            new ValidationException(`invalid field ${key as string}, \
            expected one of: \`items\`,\`type\``)
          )
          break
        }
      }
    }

    if (__errors.length > 0) {
      throw new ValidationException("Trying 'ArraySchema'", __errors)
    }

    const schema = new ArraySchema({
      extensionFields: extensionFields,
      loadingOptions: loadingOptions,
      items: items,
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

    if (this.items != null) {
      const u = saveRelativeUri(this.items, baseUrl, false,
                                relativeUris, 2)
      if (u != null) {
        r.items = u
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
            
  static attr: Set<string> = new Set(['items','type'])
}
